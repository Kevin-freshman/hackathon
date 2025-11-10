import time
import hmac
import hashlib
import requests
import logging

logger = logging.getLogger(__name__)

class RoostooClient:
    def __init__(self, api_key, api_secret, base_url="https://api.roostoo.com"):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")

    def _sign_and_request(self, method, path, params=None):
        """
        Roostoo API 核心请求方法
        """
        if params is None:
            params = {}

        timestamp = str(int(time.time() * 1000))
        body = ""
        if method == "GET":
            query_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
            payload = f"{timestamp}{method}{path}{query_str}"
        else:
            body = json.dumps(params)
            payload = f"{timestamp}{method}{path}{body}"

        # 计算签名
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        headers = {
            "X-ROOSTOO-APIKEY": self.api_key,
            "X-ROOSTOO-TIMESTAMP": timestamp,
            "X-ROOSTOO-SIGNATURE": signature,
            "Content-Type": "application/json"
        }

        url = self.base_url + path
        logger.debug(f"[Roostoo] {method} {url} | params={params}")

        if method == "GET":
            resp = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            resp = requests.post(url, headers=headers, json=params)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        try:
            data = resp.json()
        except Exception:
            logger.error(f"Roostoo 返回非 JSON: {resp.text}")
            data = {"Success": False, "ErrMsg": resp.text}

        return data

    def get_balance(self):
        res = self._sign_and_request("GET", "/v3/balance")
        if not res.get("Success"):
            logger.warning(f"get_balance 失败: {res.get('ErrMsg')}")
            return {}
        wallet = res.get("SpotWallet", {})
        flat = {asset: info["Free"] for asset, info in wallet.items()}
        return flat

    def faucet(self):
        return self._sign_and_request("POST", "/v3/faucet")
