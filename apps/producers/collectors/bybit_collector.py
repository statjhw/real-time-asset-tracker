from .base_collector import BaseCollector
import requests
import json

class BybitCollector(BaseCollector):
    def __init__(self):
        super().__init__(
            name="Bybit",
            description="Bybit is a cryptocurrency exchange.",
            url="https://api.bybit.com/v5/market/tickers?category=spot",
        )
    def collect(self) -> dict:
        try:
            response = requests.get(self.url, timeout=10)
            if response.status_code == 200:
                return json.loads(response.text)
            else:
                raise Exception(f"API 호출 실패: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Bybit API 오류: {e}")
            return None
    def fetch_all(self) -> dict:
        try:
            ticker = {}
            data = self.collect()
            if data is None:
                return None
                
            timestamp = data["time"]
            for item in data["result"]["list"]:
                ticker[item["symbol"]] = {
                    "exchange": "bybit",
                    "symbol": item["symbol"],
                    "price": item["lastPrice"],
                    "timestamp": timestamp
                }
            return ticker
        except Exception as e:
            print(f"Bybit 데이터 처리 오류: {e}")
            return None

if __name__ == "__main__":
    collector = BybitCollector()
    collector.pretty_print(collector.fetch_all())