# roostoo_client.py
import requests
import hashlib
import hmac
import time
from loguru import logger

BASE_URL = "https://mock-api.roostoo.com"
API_KEY = "s2L7kP8bN4oV1wT5gC0lY3mH6qJ9rA7fT2uD5pI8nS3xW0zK1eB4jX9vM0yU6t"
SECRET = "H2kN7pQ1wE5rT9yUiO3aS8dF0gJ4hKlZ6xC2vBnM5qW7eRtY1uI9oPaS3dF6gJ0h"

def now_ts():
    return int(time.time() * 1000)

def generate_signature(params):
    query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items()) if v is not None])
    return hmac.new(SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()

class RoostooClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"RST-API-KEY": API_KEY})

    def _sign_and_request(self, method, endpoint, params=None, data=None):
        params = params or {}
        data = data or {}
        all_params = {**params, **data, "timestamp": now_ts()}
        signature = generate_signature(all_params)
        headers = {"MSG-SIGNATURE": signature}
        url = BASE_URL + endpoint

        try:
            if method == "GET":
                response = self.session.get(url, params=all_params, headers=headers)
            else:
                response = self.session.post(url, data=all_params, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"API 请求失败: {endpoint} | {response.text if 'response' in locals() else str(e)}")
            raise

    def get_server_time(self):
        return self._sign_and_request("GET", "/v3/serverTime")

    def get_exchange_info(self):
        return self._sign_and_request("GET", "/v3/exchangeInfo")

    def get_balance(self):
        return self._sign_and_request("GET", "/v3/balance")

    def place_order(self, pair, side, quantity, price=None):
        payload = {
            "pair": pair,
            "side": side.upper(),
            "quantity": int(quantity),
            "type": "MARKET" if price is None else "LIMIT"
        }
        if price is not None:
            payload["price"] = float(price)
        return self._sign_and_request("POST", "/v3/place_order", data=payload)

    def cancel_order(self, pair, order_id=None):
        payload = {"pair": pair}
        if order_id:
            payload["order_id"] = order_id
        return self._sign_and_request("POST", "/v3/cancel_order", data=payload)

    def query_order(self, pair=None, order_id=None, pending_only=None):
        payload = {}
        if pair:
            payload["pair"] = pair
        if order_id:
            payload["order_id"] = order_id
        if pending_only is not None:
            payload["pending_only"] = pending_only
        return self._sign_and_request("POST", "/v3/query_order", data=payload)

    def pending_count(self):
        return self._sign_and_request("GET", "/v3/pending_count")