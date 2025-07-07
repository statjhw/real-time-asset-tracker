from base_collector import BaseCollector
import requests
import json
import time

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
            timestamp = int(round(time.time() * 1000))
            if response.status_code == 200:
                return json.loads(response.text), timestamp
            else:
                raise Exception(f"API 호출 실패: {response.status_code}")
        except Exception as e:
            print(e)
            return None
        
    def fetch_all(self) -> dict:
        try:
            tickers = {} 
            data, timestamp = self.collect()
            for item in data:
                tickers[item['symbol']] = {
                    "symbol": item['symbol'],
                    "price": item['price'],
                    "timestamp": timestamp
                }
            return tickers
        except Exception as e:
            print(e)
            return None
    
if __name__ == "__main__":
    collector = BinanceCollector()
    collector.pretty_print(collector.fetch_all())