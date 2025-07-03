from base_collector import BaseCollector
import requests
import json

class BinanceCollector(BaseCollector):
    def __init__(self):
        super().__init__(
            name="Binance",
            description="Binance is a cryptocurrency exchange.",
            url="https://api.binance.com/api/v3/ticker/price",
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
    collector = BinanceCollector()
    print(collector.collect())