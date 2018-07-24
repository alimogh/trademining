#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created by bu on 2018-01-17
"""
from __future__ import unicode_literals
import time
import hashlib
import json as complex_json
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from config import *

urllib3.disable_warnings(InsecureRequestWarning)
http = urllib3.PoolManager(timeout=urllib3.Timeout(connect=1, read=2))


class RequestClient(object):
    __headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'
    }

    def __init__(self, headers={}):
        self.access_id = api_key      # replace
        self.secret_key = api_secret     # replace
        self.url = 'https://api.coinex.com'
        self.headers = self.__headers
        self.headers.update(headers)

    @staticmethod
    def get_sign(params, secret_key):
        sort_params = sorted(params)
        data = []
        for item in sort_params:
            data.append(item + '=' + str(params[item]))
        str_params = "{0}&secret_key={1}".format('&'.join(data), secret_key)
        str_params = str_params.encode('utf-8')
        token = hashlib.md5(str_params).hexdigest().upper()
        return token

    def set_authorization(self, params):
        params['access_id'] = self.access_id
        params['tonce'] = int(time.time()*1000)
        self.headers['AUTHORIZATION'] = self.get_sign(params, self.secret_key)

    def request(self, method, url, params={}, data='', json={}):
        method = method.upper()
        if method in ['GET', 'DELETE']:
            self.set_authorization(params)
            result = http.request(method, url, fields=params, headers=self.headers)
        else:
            if data:
                json.update(complex_json.loads(data))
            self.set_authorization(json)
            encoded_data = complex_json.dumps(json).encode('utf-8')
            result = http.request(method, url, body=encoded_data, headers=self.headers)
        return result


def get_account():
    request_client = RequestClient()
    response = request_client.request('GET', '{url}/v1/balance/'.format(url=request_client.url))


def order_pending(market_type):
    request_client = RequestClient()
    params = {
        'market': market_type
    }
    response = request_client.request(
            'GET',
            '{url}/v1/order/pending'.format(url=request_client.url),
            params=params
    )


def order_finished(market_type, page, limit):
    request_client = RequestClient()
    params = {
        'market': market_type,
        'page': page,
        'limit': limit
    }
    response = request_client.request(
            'GET',
            '{url}/v1/order/finished'.format(url=request_client.url),
            params=params

    )
    data = complex_json.loads(response.data)
    return data



def put_market():
    request_client = RequestClient()

    data = {
            "amount": "1",
            "type": "sell",
            "market": "CETBCH"
        }

    response = request_client.request(
            'POST',
            '{url}/v1/order/market'.format(url=request_client.url),
            json=data,
    )


def cancel_order(id, market):
    request_client = RequestClient()
    data = {
        "id": id,
        "market": market,
    }

    response = request_client.request(
            'DELETE',
            '{url}/v1/order/pending'.format(url=request_client.url),
            params=data,
    )
    return response.data

def getdifficult():
    request_client = RequestClient()
    data = {

    }

    response = request_client.request(
            'GET',
            '{url}/v1/order/mining/difficulty'.format(url=request_client.url),
            data=data,
    )
    data = complex_json.loads(response.data)['data']['difficulty']
    return float(data)