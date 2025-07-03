class BaseCollector:
    def __init__(self, name: str, description: str, url: str, api_key: str = None):
        self.name = name
        self.description = description
        self.url = url 
        self.api_key = api_key

    def collect(self) -> dict :
        pass