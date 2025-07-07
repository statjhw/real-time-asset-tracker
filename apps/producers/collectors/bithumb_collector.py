from base_collector import BaseCollector
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
            timestamp = data["data"]["date"]
            for ticker, items in data["data"].items():
                if ticker == "date":
                    continue
                tickers[ticker] = {
                    "symbol": ticker,
                    "price": items["closing_price"],
                    "opening_price": items["opening_price"], 
                    "min_price": items["min_price"],
                    "max_price": items["max_price"],
                    "units_traded": items["units_traded"],
                    "acc_trade_value": items["acc_trade_value"],
                    "prev_closing_price": items["prev_closing_price"],
                    "units_traded_24H": items["units_traded_24H"],
                    "acc_trade_value_24H": items["acc_trade_value_24H"],
                    "fluctate_24H": items["fluctate_24H"],
                    "fluctate_rate_24H": items["fluctate_rate_24H"],
                    "timestamp": timestamp
                }
            return tickers

        except Exception as e:
            print(e)
            return None
        
if __name__ == "__main__":
    collector = BithumbCollector()
    collector.pretty_print(collector.fetch_all())