from .base_collector import BaseCollector
import requests
import json

class BithumbCollector(BaseCollector):
    def __init__(self):
        super().__init__(
            name="Bithumb",
            description="빗썸 코인 시세 수집",
            url="https://api.bithumb.com/public/ticker/ALL_KRW",
        )

    def collect(self) -> dict:
        try:
            response = requests.get(self.url, timeout=10)
            if response.status_code == 200:
                return json.loads(response.text)
            else:
                raise Exception(f"API 호출 실패: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Bithumb API 오류: {e}")
            return None
    
    def fetch_all(self) -> dict:
        try: 
            tickers = {}
            data = self.collect()
            if data is None:
                return None
                
            timestamp = data["data"]["date"]
            for ticker, items in data["data"].items():
                if ticker == "date":
                    continue
                tickers[ticker] = {
                    "exchange": "bithumb",
                    "symbol": ticker,
                    "price": items["closing_price"],
                    "timestamp": timestamp
                }
            return tickers

        except Exception as e:
            print(f"Bithumb 데이터 처리 오류: {e}")
            return None
        
if __name__ == "__main__":
    collector = BithumbCollector()
    collector.pretty_print(collector.fetch_all())