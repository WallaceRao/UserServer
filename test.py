import requests
import numpy as np
import json
import base64
import time
import datetime
import wave
import sys    
import http.client

def request_verification_code():
    conn = http.client.HTTPConnection('123.57.53.46:8081')
    request_headers = {'Content-type': 'application/json'}
    foo = {
        'email': 'raoyonghui0630@gmail.com',
    }
    json_data = json.dumps(foo)
    start = time.time()
    res = conn.request("POST", "/request_verification_code", json_data, request_headers)
    response = conn.getresponse()
    print("response:", response.status, response.reason)
    response_bytes = response.read()
    response_headers = response.getheaders()
    print("response_bytes:", response_bytes)
    print("response_headers:", response_headers)
  

def register():
    conn = http.client.HTTPConnection('123.57.53.46:8081')
    request_headers = {'Content-type': 'application/json'}
    foo = {
        'email': 'raoyonghui0630@gmail.com',
        'password': '123456',
        'verification_code': '641943',
    }
    json_data = json.dumps(foo)
    start = time.time()
    res = conn.request("POST", "/register", json_data, request_headers)
    response = conn.getresponse()
    print("response:", response.status, response.reason)
    response_bytes = response.read()
    response_headers = response.getheaders()
    print("response_bytes:", response_bytes)
    print("response_headers:", response_headers)
  

if __name__ == "__main__":
    #request_verification_code()
    register()
