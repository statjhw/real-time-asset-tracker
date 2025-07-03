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
        
if __name__ == "__main__":
    collector = CoinoneCollector()
    print(collector.collect())