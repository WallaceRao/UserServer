from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import multiprocessing
import threading

import argparse
from argparse import ArgumentParser
import os
import json
import base64
import logging

import re
import time
import uuid
from db_tool import DBTool

tts_logger = logging.getLogger("user_service")
tts_logger.setLevel(logging.INFO)
log_path = "/user_service/user_service.log"
handler = logging.FileHandler(log_path, mode='a')
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
handler.setFormatter(formatter)
tts_logger.addHandler(handler)
db_instance = DBTool()
db_instance.init("/root/UserServer/user.db")

class Handler(SimpleHTTPRequestHandler):
    def send_post_response(self, response_str):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Content-Length", str(len(response_str.encode("UTF-8"))))
        self.end_headers()
        self.wfile.write(response_str.encode("UTF-8"))
    
    def register(self, json_obj):
        global db_instance
        err_msg = ""
        if "email" not in json_obj.keys():
            err_msg = "no email info provided"
        if "password" not in json_obj.keys():
            err_msg = "no password info provided"
        if "verification_code" not in json_obj.keys():
            err_msg = "no verification_code info provided"
        if len(err_msg):
            response_str = json.dumps({"err_msg": err_msg, "succeed": "false"})
            self.send_post_response(response_str)
            return 0
        email = json_obj["email"]
        password = json_obj["password"]
        verification_code = json_obj["verification_code"]
        ret, err_msg = db_instance.register(email, password, verification_code)
        succeed = "true"
        if not ret:
            succeed = "false"
        response_str = json.dumps({"err_msg": err_msg, "succeed": succeed})
        self.send_post_response(response_str)
        return 0
    
    def request_verification_code(self, json_obj):
        global db_instance
        err_msg = ""
        if "email" not in json_obj.keys():
            err_msg = "no email info provided"
        if len(err_msg):
            response_str = json.dumps({"err_msg": err_msg, "succeed": "false"})
            self.send_post_response(response_str)
            return 0
        email = json_obj["email"]
        ret, err_msg = db_instance.verify_email_code(email)
        succeed = "true"
        if not ret:
            succeed = "false"
        response_str = json.dumps({"err_msg": err_msg, "succeed": succeed})
        self.send_post_response(response_str)
        return 0
    
    def login(self, json_obj):
        global db_instance
        err_msg = ""
        if "email" not in json_obj.keys():
            err_msg = "no email info provided"
        if "password" not in json_obj.keys():
            err_msg = "no password info provided"
        if len(err_msg):
            response_str = json.dumps({"err_msg": err_msg, "succeed": "false"})
            self.send_post_response(response_str)
            return 0
        email = json_obj["email"]
        password = json_obj["password"]
        ret, err_msg = db_instance.login(email, password)
        succeed = "true"
        if not ret:
            succeed = "false"
        response_str = json.dumps({"err_msg": err_msg, "succeed": succeed})
        self.send_post_response(response_str)
        return 0
    
    def logout(self, json_obj):
        global db_instance
        # nothing to do
        return 0
    
    def reset_password(self, json_obj):
        global db_instance
        err_msg = ""
        if "email" not in json_obj.keys():
            err_msg = "no email info provided"
        if "password" not in json_obj.keys():
            err_msg = "no password info provided"
        if "verification_code" not in json_obj.keys():
            err_msg = "no verification_code info provided"
        if len(err_msg):
            response_str = json.dumps({"err_msg": err_msg, "succeed": "false"})
            self.send_post_response(response_str)
            return 0
        email = json_obj["email"]
        password = json_obj["password"]
        verification_code = json_obj["verification_code"]
        ret, err_msg = db_instance.reset_password(email, verification_code, password)
        succeed = "true"
        if not ret:
            succeed = "false"
        response_str = json.dumps({"err_msg": err_msg, "succeed": succeed})
        self.send_post_response(response_str)
        return 0
    
    def update_password(self, json_obj):
        global db_instance
        err_msg = ""
        if "email" not in json_obj.keys():
            err_msg = "no email info provided"
        if "old_password" not in json_obj.keys():
            err_msg = "no old_password info provided"
        if "new_password" not in json_obj.keys():
            err_msg = "no new_password info provided"
        if len(err_msg):
            response_str = json.dumps({"err_msg": err_msg, "succeed": "false"})
            self.send_post_response(response_str)
            return 0
        email = json_obj["email"]
        old_password = json_obj["old_password"]
        new_password = json_obj["new_password"]
        ret, err_msg = db_instance.update_password(email, old_password, new_password)
        succeed = "true"
        if not ret:
            succeed = "false"
        response_str = json.dumps({"err_msg": err_msg, "succeed": succeed})
        self.send_post_response(response_str)
        return 0
    
    def do_GET(self):
        # no GET mehod supported
        self.send_error(404, "File not found:" + self.path)

    def do_POST(self):
        data_string = self.rfile.read(int(self.headers['Content-Length']))
        req_id = str(uuid.uuid4().fields[-1])[:5]
        tts_logger.info(f"received a user request:{data_string}, req_id:{req_id}")
        json_obj = json.loads(data_string)
        if self.path == "/register":
            self.register(json_obj)
        if self.path == "/login":
            self.login(json_obj)
        if self.path == "/logout":
            self.logout(json_obj)
        if self.path == "/request_verification_code":
            self.request_verification_code(json_obj)
        if self.path == "/reset_password":
            self.reset_password(json_obj)
        if self.path == "/update_password":
            self.update_password(json_obj)
        tts_logger.info(f"finished to process tts request:{data_string}, req_id:{req_id}")

def run():
    server = ThreadingHTTPServer(('0.0.0.0', 8081), Handler)
    server.serve_forever()

if __name__ == '__main__':
    run()

