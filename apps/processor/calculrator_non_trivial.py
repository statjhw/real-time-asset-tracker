from pyflink.common import Types, Time, Configuration
from pyflink.common.serialization import SimpleStringSchema, SerializationSchema
from pyflink.datastream import StreamExecutionEnvironment, RuntimeContext
from pyflink.datastream.functions import MapFunction, CoProcessFunction
from pyflink.datastream.state import ValueStateDescriptor
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaSink, KafkaOffsetsInitializer, KafkaRecordSerializationSchema, DeliveryGuarantee
from pyflink.common.watermark_strategy import WatermarkStrategy
from dotenv import load_dotenv
import json
import os
import time
from pathlib import Path

load_dotenv()

class ChangeRateCalculator(MapFunction):
    def __init__(self):
        self.last_prices = {}  # exchange_symbol별로 마지막 가격 저장
        
    def map(self, value: dict):
        try:
            exchange = value.get("exchange", "unknown")
            symbol = value.get("symbol", "unknown")
            key = f"{exchange}_{symbol}"  # 복합 키 사용
            current_price = float(value["price"])
            
            change_rate = 0.0
            
            if key in self.last_prices and self.last_prices[key] > 0:
                last_price = self.last_prices[key]
                change_rate = (current_price - last_price) / last_price
            
            self.last_prices[key] = current_price
            value["change_rate"] = round(change_rate, 4)
            return value
            
        except Exception as e:
            print(f"Error in ChangeRateCalculator: {e}")
            return value

class DeviationCalculator(MapFunction):
    def __init__(self, alpha: float = 0.1):
        self.alpha = alpha
        self.ema_values = {}  # EMA 값들을 저장할 딕셔너리

    def map(self, value: dict):
        try:
            exchange = value.get("exchange", "unknown")
            symbol = value.get("symbol", "unknown")
            key = f"{exchange}_{symbol}"  # 복합 키 사용
            current_price = float(value["price"])
            
            if key not in self.ema_values:
                ema = current_price 
            else:
                prev_ema = self.ema_values[key]
                ema = self.alpha * current_price + (1 - self.alpha) * prev_ema
            
            self.ema_values[key] = ema
            if ema != 0:
                deviation = (current_price - ema) / ema
            else:
                deviation = 0.0

            value["ema_price"] = round(ema, 2)
            value["deviation_rate"] = round(deviation, 4)
            return value
            
        except Exception as e:
            print(f"Error in DeviationCalculator: {e}")
            return value

class PremiumCalculator(CoProcessFunction):
    def __init__(self, fx_url: str):
        self.fx_url = fx_url
        self.upbit_price_state = None
        self.binance_price_state = None

    def open(self, runtime_context: RuntimeContext):
        self.upbit_price_state = runtime_context.get_state(ValueStateDescriptor("upbit_price", Types.DOUBLE()))
        self.binance_price_state = runtime_context.get_state(ValueStateDescriptor("binance_price", Types.DOUBLE()))

    def process_element1(self, upbit_data: dict, ctx: CoProcessFunction.Context, out):
        """업비트 스트림에서 데이터가 들어올 때 처리"""
        self.upbit_price_state.update(upbit_data["price"])
        binance_price = self.binance_price_state.value()

        if binance_price is not None:
            self._calculate_and_emit_premium(upbit_data["price"], binance_price, out)

    def process_element2(self, binance_data: dict, ctx: CoProcessFunction.Context, out):
        """바이낸스 스트림에서 데이터가 들어올 때 처리"""
        self.binance_price_state.update(binance_data["price"])
        upbit_price = self.upbit_price_state.value()

        if upbit_price is not None:
            self._calculate_and_emit_premium(upbit_price, binance_data["price"], out)

    def _get_fx_rate(self):
        """환율 정보 가져오기"""
        return 1300.00

    def _calculate_and_emit_premium(self, p_krw: float, p_usd: float, out):
        fx_rate = self._get_fx_rate()
        p_usd_in_krw = p_usd * fx_rate
        if p_usd_in_krw > 0: 
            premium = ((p_krw - p_usd_in_krw) / p_usd_in_krw) * 100
            # OpenSearch에 저장할 데이터 구조
            out.collect({
                "symbol": "KRW-BTC-Premium", 
                "premium": round(premium, 4),
                # Grafana에서 인식할 @timestamp 필드 추가
                "@timestamp": int(time.time() * 1000)
            })

def run_crypto_analysis_pipeline():
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)  # 단순화를 위해 병렬도 1로 설정

    kafka_jar = "file:///app/jars/flink-sql-connector-kafka-3.3.0-1.20.jar"
    env.add_jars(kafka_jar)

    # --- Kafka 소스 설정 ---
    kafka_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")  # Docker 환경 기본값 수정
    print(f"Using Kafka servers: {kafka_servers}")
    
    source = KafkaSource.builder() \
        .set_bootstrap_servers(kafka_servers) \
        .set_topics("crypto-ticker-binance", "crypto-ticker-bithumb", "crypto-ticker-bybit", "crypto-ticker-coinone", "crypto-ticker-upbit") \
        .set_group_id("crypto-analysis-group") \
        .set_starting_offsets(KafkaOffsetsInitializer.latest()) \
        .set_value_only_deserializer(SimpleStringSchema()) \
        .build()
    
    # --- 기본 데이터 스트림 (@timestamp 필드 추가) ---
    unified_stream = env.from_source(source, WatermarkStrategy.no_watermarks(), "Kafka Source") \
                        .map(lambda x: json.loads(x)) \
                        .filter(lambda data: data is not None) \
                        .map(lambda d: {
                            **d, 
                            "@timestamp": int(d.get("timestamp", time.time() * 1000))
                        })

    # --- 변동률 및 괴리율 계산 파이프라인 ---
    volatility_stream = unified_stream \
                    .key_by(lambda x: f"{x.get('exchange', 'unknown')}_{x.get('symbol', 'unknown')}") \
                    .map(ChangeRateCalculator()) \
                    .map(DeviationCalculator(alpha=0.1))

    # --- Kafka Sink 설정 (수정됨) ---
    kafka_sink = KafkaSink.builder() \
        .set_bootstrap_servers(kafka_servers) \
        .set_record_serializer(
            KafkaRecordSerializationSchema.builder()
                .set_topic("crypto-ticker-volatility")
                .set_value_serialization_schema(SimpleStringSchema())
                .build()
        ) \
        .set_delivery_guarantee(DeliveryGuarantee.AT_LEAST_ONCE) \
        .set_transactional_id_prefix("crypto-volatility-") \
        .set_property("transaction.timeout.ms", "60000") \
        .build()

    # Kafka에 저장할 데이터를 JSON 문자열로 변환합니다.
    # 'key' 필드에 'exchange' 값을 포함시켜서 저장합니다.
    volatility_stream.map(
        lambda d: json.dumps({
            "value": d
        }),
        output_type=Types.STRING()
    ).sink_to(kafka_sink).name("Volatility Kafka Sink")

    print("Starting Flink job...")
    env.execute("Crypto Analysis Pipeline")

if __name__ == "__main__":
    run_crypto_analysis_pipeline()