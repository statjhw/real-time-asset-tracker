from base_collector import BaseCollector
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
            response = requests.get(self.url)
            if response.status_code == 200:
                return json.loads(response.text)
            else:
                raise Exception(f"API 호출 실패: {response.status_code}")
        except Exception as e:
            print(e)
            return None

if __name__ == "__main__":
    collector = BybitCollector()
    print(collector.collect())