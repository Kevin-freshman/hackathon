# horus_client.py
import requests
import os
from dotenv import load_dotenv
from loguru import logger

load_dotenv()
HORUS_API_KEY = os.getenv("HORUS_API_KEY", "")
HORUS_BASE_URL = "https://api-horus.com"  # 假设 URL，根据 PDF 调整

class HorusClient:
    def __init__(self):
        if not HORUS_API_KEY:
            raise ValueError("HORUS_API_KEY not set in .env")
        self.session = requests.Session()
        self.session.headers.update({"API-KEY": HORUS_API_KEY, "Content-Type": "application/json"})

    def _request(self, endpoint, params=None):
        url = HORUS_BASE_URL + endpoint
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if not data.get("success", True):
                raise ValueError(f"Horus error: {data.get('message')}")
            return data["data"]
        except Exception as e:
            logger.error(f"Horus API error: {e}")
            raise

    def get_market_price(self, pair="BTC/USD", limit=100, start_time=None, end_time=None):
        """获取价格历史，作为 K 线数据"""
        params = {"pair": pair, "limit": limit}
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        return self._request("/market/price", params)

    def get_defi_tvl(self, chain=None, protocol=None, limit=100):
        """获取 TVL 数据，作为额外信号"""
        params = {"limit": limit}
        if chain:
            params["chain"] = chain
        if protocol:
            params["protocol"] = protocol
        return self._request("/defi/tvl", params)

    def get_transaction_count(self, chain=None, limit=100):
        """获取交易数量"""
        params = {"limit": limit}
        if chain:
            params["chain"] = chain
        return self._request("/transaction/count", params)