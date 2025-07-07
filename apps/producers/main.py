import time 
import yaml
import threading
from kafka import KafkaProducer
import json

from collectors.binance_collector import BinanceCollector
from collectors.bithumb_collector import BithumbCollector
from collectors.bybit_collector import BybitCollector
from collectors.upbit_collector import UpbitCollector
from collectors.coinone_collector import CoinoneCollector
from utils.logger import setup_default_logger

COLLECTORS_MAP = {
    "BinanceCollector": BinanceCollector,
    "BithumbCollector": BithumbCollector,
    "BybitCollector": BybitCollector,
    "UpbitCollector": UpbitCollector,
    "CoinoneCollector": CoinoneCollector
}

def run_collector_work(exchange_name, global_config, shutdown_event):
    "각 거래소 별 데이터 수집 및 카프카 전송 worker"
    logger = setup_default_logger("producer", "INFO")
    logger.info(f"{exchange_name} 수집기 워커 시작")
    ex_config = global_config["exchanges"][exchange_name]
    collector_class = COLLECTORS_MAP[ex_config["collector_class"]]
    collector = collector_class()
    logger.info(f"수집기 초기화 완료: {collector_class.__name__}")

    producer = KafkaProducer(
        bootstrap_servers=global_config["kafka"]["bootstrap_servers"],
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

    topic = ex_config["kafka_topic"]

    while not shutdown_event.is_set():
        try:
            data = collector.fetch_all()
            for symbol, item in data.items():
                if not ex_config["enabled"]:
                    continue
                key = symbol 
                value = item
                producer.send(topic, key=key, value=value)
                logger.debug(f"데이터 전송: {symbol}")
            producer.flush()
        except Exception as e:
            logger.exception(f"수집기 오류: {e}")
        
        time.sleep(ex_config["poll_interval_seconds"])
    
    producer.close()
    logger.info(f"{exchange_name} 수집기 워커 종료")

def main():
    with open("configs/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    threads = []
    shutdown_event = threading.Event()

    logger = setup_default_logger("producer", "INFO")
    logger.info("메인 프로그램 시작")

    for name, ex_config in config["exchanges"].items():
        if ex_config.get("enabled", False):
            thread = threading.Thread(
                target=run_collector_work,
                args=(name, config, shutdown_event),
                daemon=True
            )
            threads.append(thread)
            thread.start()
            logger.info(f"수집기 스레드 시작: {name}")
    
    logger.info("모든 수집기 스레드 시작")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt: 
        logger.info("종료 시스널 발생, 우아하게 종료")
        shutdown_event.set()
    finally:
        for thread in threads:
            thread.join()
        logger.info("모든 수집기 스레드 종료")

if __name__ == "__main__":
    main()
