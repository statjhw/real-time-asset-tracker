from base_collector import BaseCollector
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
            self.market_url = self.market_url + ",".join(tickers)
            response = requests.get(self.market_url)
            if response.status_code == 200:
                return json.loads(response.text)
            else:
                raise Exception(f"API 호출 실패: {response.status_code}")
        except Exception as e:
            print(e)
            return None
    
if __name__ == "__main__":
    collector = UpbitCollector()
    print(collector.collect())