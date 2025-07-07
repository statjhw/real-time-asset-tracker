import json

class BaseCollector:
    def __init__(self, name: str, description: str, url: str, api_key: str = None):
        self.name = name
        self.description = description
        self.url = url 
        self.api_key = api_key

    def pretty_print(self,data):
        print(json.dumps(data, indent=2, ensure_ascii=False))

    def collect(self) -> dict :
        pass

    def fetch_all(self) -> dict:
        pass
