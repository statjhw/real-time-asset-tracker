from .base_collector import BaseCollector
import requests
import json

class UpbitCollector(BaseCollector):
    def __init__(self):
        super().__init__(
            name="Upbit",
            description="업비트 코인 시세 수집",
            url="https://api.upbit.com/v1/market/all",
        )
        self.market_url = "https://api.upbit.com/v1/ticker?markets="
    
    def tickers(self) -> list:
        response = requests.get(self.url)
        if response.status_code == 200:
            markets = response.json()
            # market 필드만 추출하여 티커 리스트 반환
            tickers = [market['market'] for market in markets]
            return tickers
        else:
            raise Exception(f"API 호출 실패: {response.status_code}")
    
    def collect(self) -> dict:
        try:
            tickers = self.tickers()
            if not tickers:
                raise Exception("티커 목록을 가져올 수 없습니다")
            
            # 주요 마켓만 선택 (URL 길이 제한을 위해)
            major_tickers = [ticker for ticker in tickers if ticker.startswith('KRW-')][:50]  # 상위 50개만
            
            url = self.market_url + ",".join(major_tickers)
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return json.loads(response.text)
            else:
                raise Exception(f"API 호출 실패: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Upbit API 오류: {e}")
            return None
    def fetch_all(self) -> dict:
        try: 
            tickers = {}
            data = self.collect()
            if data is None:
                return None
                
            for item in data:
                tickers[item["market"]] = {
                    'symbol': item["market"],
                    'price': item["trade_price"],
                    'opening_price': item["opening_price"],
                    'high_price': item["high_price"],
                    'low_price': item["low_price"],
                    'prev_closing_price': item["prev_closing_price"],
                    'change': item["change"],
                    'change_price': item["change_price"],
                    'change_rate': item["change_rate"],
                    'timestamp': item["timestamp"]
                }
            return tickers
        except Exception as e:
            print(f"Upbit 데이터 처리 오류: {e}")
            return None
if __name__ == "__main__":
    collector = UpbitCollector()
    collector.pretty_print(collector.fetch_all())