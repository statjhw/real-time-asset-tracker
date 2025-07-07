from base_collector import BaseCollector
import requests
import json

class CoinoneCollector(BaseCollector):
    def __init__(self):
        super().__init__(
            name="Coinone",
            description="코인원 코인 시세 수집",
            url="https://api.coinone.co.kr/public/v2/ticker_utc_new/KRW",
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
    def fetch_all(self) -> dict:
        try:
            tickers = {}    
            data = self.collect()
            for item in data["tickers"]:
                tickers[item["target_currency"]] = {
                    "symbol": item["target_currency"],
                    "price": item["last"],
                    "quote_currency": item["quote_currency"],
                    "high": item["high"],
                    "low": item["low"],
                    "timestamp": item["timestamp"]
                }
            return tickers
        except Exception as e:
            print(e)
            return None
if __name__ == "__main__":
    collector = CoinoneCollector()
    collector.pretty_print(collector.fetch_all())