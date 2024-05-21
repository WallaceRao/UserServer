import os
import json
import base64
import logging
import random
import numpy as np
import re
import time
from datetime import datetime
import uuid
from sqlite_utils import Database
from peewee import *
import datetime
import hashlib
from email_tool import send_email

tts_logger = logging.getLogger("user_service")

class DBTool(Object):
    def init(db_file):
        self.db = Database(db_file)
        if "user_info" not in self.db.table_names():
            tts_logger.info(f"no user_info table found, create a new one")
            self.user_info = self.db["user_info"]
                self.user_info.insert_all(
                    [{
                        "id": 1
                        "email": "raoyonghui0630@gmail.com",
                        "password": "123456",
                        "is_vip": False,
                        "vip_start_date": "1970-01-01",
                        "vip_end_date": "1970-01-01",
                    }],
                    pk="id",
                    not_null={"id", "name", "email", "password"},
                    defaults={"is_vip": False},
                )
        self.user_table = self.db["user_info"]
        self.email_code_dict = {}
        self.user_map = {}
        self.update_users()
    
    def update_users(self):
        self.user_map = {}
        try:
            for row in db.query("select * from user_info"):
                self.user_map[row["email"]] = row["password"]
        except Exception as e:
            tts_logger.info(f"got exception when update users, exception:{e}")
    
    def get_value_from_email(self, email, key):
        elf.user_map = {}
        try:
            for row in db.query("select * from user_info where email =" + email):
                if key is not in row.keys():
                    tts_logger.info(f"no key:{key} from the row:", row)
                    continue
                password = row[key]
                return True, password
        except Exception as e:
            tts_logger.info(f"got exception when get password, exception:{e}")
        return False, ""

    def verify_email_addr(self, email):
        err_msg = ""
        if email in self.user_info:
            err_msg = "Email has been registered"
            return False, err_msg
        return True, err_msg

     def verify_email_code(self, email):
        err_msg = ""
        if email in self.user_info:
            err_msg = "Email has been registered"
            return False, err_msg
        subject = "Verification Code from Voice Training Service"
        verification_code = str(random.randint(100000,999999))
        body = "Your verification code is " + verification_code
        sender = "voicetrainingservice@gmail.com"
        password = "VoiceTrainingService123"
        send_email(subject, email, body, sender, password)
        self.email_code_dict[email] = verification_code
        return True, err_msg
        
    def register(self, email, password, verification_code):
        err_msg = ""
        if email not in self.email_code_dict.keys():
            err_msg = "no verificatio code is sent to " + email
            return False, err_msg
        if verification_code != self.email_code_dict[email]:
            err_msg = "Incorrect verification code"
            return False, err_msg
        if len(password) < 6:
            err_msg = "Password should contain at least 6 characters"
            return False, err_msg
        try:
            self.user_info.insert(
                {
                    "email": email,
                    "password": password,
                    "is_vip": False
                }
            )
        except Exception as e:
            tts_logger.info(f"got exception when register email:{email}, exception:{e}")
            err_msg = "DB error"
            return False, err_msg
        self.update_users()
        return True, err_msg
    
    def login(self, email, password):
        err_msg = ""
        if email in self.user_info:
            if password == self.user_info["email"]:
                return True, err_msg
        err_msg = "Incorrect Email or Password"
        return False, err_msg
    
    def verify_access_token(self, email, token):
        err_msg = ""
        if email in self.user_info:
            password = self.user_info["email"]
            yesterday = date.today() - timedelta(days=1)
            tomorrow = date.today() + timedelta(days=1)
            today_str = datetime.today().strftime('%Y-%m-%d')
            yestoday_str = yesterday.strftime('%Y-%m-%d')
            tomorrow_str = tomorrow.strftime('%Y-%m-%d')
            days = [yestoday_str, today_str, tomorrow_str]
            password = self.user_info[email]
            for day in days:
                before_base64 = password + "+" + day
                before_base64_bytes = before_base64.encode("utf8")
                base64_bytes = base64.b64encode(before_base64_bytes)
                base64_string = base64_bytes.decode("utf8")
                if token == base64_string:
                    return True, err_msg
        err_msg = "Incorrect Email or Token"
        return False, err_msg
        
    def update_password(self, email, old_password, new_password):
        if email not in self.user_info:
            err_msg = "Incorrect email address or password"
            return False, err_msg 
        password = self.user_info["email"]
        if old_password != password:
            err_msg = "Incorrect email address or password"
            return False, err_msg
        if len(new_password) < 6:
            err_msg = "Password should contain at least 6 characters"
            return False, err_msg
        try:
            row_id = self.get_value_from_email(email, "id")
            self.db["user_info"].update(row_id, {"password": new_password})
            self.user_map[email] = new_password
        except Exception as e:
            tts_logger.info(f"got exception when update password for email:{email}, exception:{e}")
            err_msg = "DB error"
            return False, err_msg
        return True, err_msg
    
    def reset_password(self, email, verification_code, new_password):
        # call verify_email_code first to get the verification code
        if email not in self.email_code_dict:
            err_msg = "Incorrect email address"
            return False, err_msg
        expect_verification_code = self.email_code_dict[email]
        if expect_verification_code != verification_code:
            err_msg = "Incorrect verification code"
            return False, err_msg
        if len(new_password) < 6:
            err_msg = "Password should contain at least 6 characters"
            return False, err_msg
        try:
            row_id = self.get_value_from_email(email, "id")
            self.db["user_info"].update(row_id, {"password": new_password})
            self.user_map[email] = new_password
        except Exception as e:
            tts_logger.info(f"got exception when update password for email:{email}, exception:{e}")
            err_msg = "DB error"
            return False, err_msg
        return True, err_msg
