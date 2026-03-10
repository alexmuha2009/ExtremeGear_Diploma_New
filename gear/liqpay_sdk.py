import base64
import hashlib
import json
import requests

class LiqPay(object):
    def __init__(self, public_key, private_key, host='https://www.liqpay.ua/api/'):
        self._public_key = public_key
        self._private_key = private_key
        self._host = host

    def cnb_form(self, params):
        params = self._prepare_params(params)
        data = self.cnb_data(params)
        signature = self.cnb_signature(params)
        return data, signature

    def cnb_signature(self, params):
        params = self._prepare_params(params)
        payload = self._private_key + self.cnb_data(params) + self._private_key
        return self.str_to_sign(payload)

    def cnb_data(self, params):
        params = self._prepare_params(params)
        return base64.b64encode(json.dumps(params).encode('utf-8')).decode('utf-8')

    def str_to_sign(self, str):
        return base64.b64encode(hashlib.sha1(str.encode('utf-8')).digest()).decode('utf-8')

    def _prepare_params(self, params):
        params['public_key'] = self._public_key
        return params