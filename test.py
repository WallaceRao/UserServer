import requests
import numpy as np
import json
import base64
import time
import datetime
import wave
import sys    
import http.client

def register():
    conn = http.client.HTTPConnection('123.57.53.46:8081/register')
    data_format = "mp3" # only MP3 and pcm are supported 
    request_headers = {'Content-type': 'application/json'}
    foo = {
    'text': 'In addition to the specific generation tasks, \
            Amphion also includes several vocoders and evaluation metrics. \
            A vocoder is an important module for producing high-quality audio signals, \
            while evaluation metrics are critical for ensuring consistent metrics in \
            generation tasks.',
    'speaker_name': 'Cori Samuel',
    'mix_speaker_name': 'Phil Benson',
    'mix_degree': '1.0',
    'data_format':data_format}
    json_data = json.dumps(foo)
    start = time.time()
    res = conn.request("POST", "", json_data, request_headers)
    response = conn.getresponse()
    print("response:", response.status, response.reason)
    response_bytes = response.read()
    response_headers = response.getheaders()
    print("response_bytes:", response_bytes)
    print("response_headers:", response_headers)
  

if __name__ == "__main__":
    conn = http.client.HTTPConnection('127.0.0.1:8095')
    #conn = http.client.HTTPConnection('20f58e9a.r7.cpolar.top:80')
    data_format = "mp3" # only MP3 and pcm are supported 
    request_headers = {'Content-type': 'application/json'}
    foo = {
    'text': 'In addition to the specific generation tasks, \
            Amphion also includes several vocoders and evaluation metrics. \
            A vocoder is an important module for producing high-quality audio signals, \
            while evaluation metrics are critical for ensuring consistent metrics in \
            generation tasks.',
    'speaker_name': 'Cori Samuel',
    'mix_speaker_name': 'Phil Benson',
    'mix_degree': '1.0',
    'data_format':data_format}
    json_data = json.dumps(foo)
    start = time.time()
    res = conn.request("POST", "", json_data, request_headers)
    response = conn.getresponse()
    print(response.status, response.reason)
    response_bytes = response.read()
    response_headers = response.getheaders()
    json_obj = json.loads(response_bytes)
    
    err_msg = ""
    if "err_msg" in json_obj.keys():
        err_msg = json_obj["err_msg"]
    if "data" not in json_obj.keys():
        print("no data field returned, error msg:", err_msg)
        sys.exit(1)
    data_str = json_obj["data"]
    decoded_binary = base64.b64decode(data_str)
    samples = None
    if data_format == "pcm":
        samples = np.frombuffer(decoded_binary, dtype=np.int16)
        print("samples count:", len(samples))
        print(f'Time Used: {time.time() - start}, audio duration: {len(samples) / 24000}')
        pcm_bytes = samples.tobytes()
        with wave.open("./result.wav", "wb") as out_f:
            out_f.setnchannels(1)
            out_f.setsampwidth(2)
            out_f.setframerate(24000)
            out_f.writeframesraw(pcm_bytes)
    else:
        print(f'Time Used: {time.time() - start}, received mp3 bytes: {len(decoded_binary)}')
        with open("./result.mp3", "wb") as file:
            file.write(decoded_binary)