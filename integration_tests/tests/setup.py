#!/usr/bin/python3

import requests
import MySQLdb

import os


def ensure_user():
    # Add default local user
    data = {'email': 'local@wandb.com', 'password': 'perceptron'}
    requests.put('http://localhost:8083/api/users', data=data)


def get_api_key():
    # mysql_uri = "mysql://wandb_local:wandb_local@127.0.0.1:3306/wandb_local"
    db = MySQLdb.connect(
        host="127.0.0.1",
        port=3306,
        user="wandb_local",
        passwd="wandb_local",
        db="wandb_local")

    cursor = db.cursor()

    cursor.execute("SELECT id FROM users u WHERE u.email='local@wandb.com'")
    row = cursor.fetchone()
    uid = row[0]
    cursor.execute(f"SELECT a.key FROM api_keys a WHERE a.user_id={uid}")
    row = cursor.fetchone()

    api_key = row[0]
    return api_key


def set_user_envs():
    os.environ["WANDB_API_KEY"] = get_api_key()
    os.environ["WANDB_BASE_URL"] = "http://localhost:9000"
    os.environ["WANDB_USERNAME"] = "local"
