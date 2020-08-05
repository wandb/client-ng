import requests
import MySQLdb

import os

def ensure_user():
    # Add default local user
    data = {'email': 'local@wandb.com', 'password': 'perceptron'}
    requests.put('http://localhost:8080/api/users', data=data)

def get_user_id(db):
    cursor = db.cursor()

    cursor.execute("SELECT id FROM users u WHERE u.email='local@wandb.com'")
    row = cursor.fetchone()
    return row[0]

def db_connection():
    # mysql_uri = "mysql://wandb_local:wandb_local@127.0.0.1:3306/wandb_local"
    # db = MySQLdb.connect(host="127.0.0.1",port=3306,user="wandb_local",passwd="wandb_local",db="wandb_local")
    db = MySQLdb.connect(
        host="127.0.0.1",
        port=3306,
        user="wandb_local",
        passwd="wandb_local",
        db="wandb_local")

    return db


def get_api_key(db, uid):
    cursor = db.cursor()

    cursor.execute(f"SELECT a.key FROM api_keys a WHERE a.user_id={uid}")
    row = cursor.fetchone()

    api_key = row[0]
    return api_key

def get_user_envs():
    db = db_connection()
    ensure_user()
    uid = get_user_id(db)
    api_key = get_api_key(db, uid)
    return {"WANDB_API_KEY": api_key,
            "WANDB_BASE_URL": "http://localhost:8080",
            "WANDB_USERNAME": "local"}


def set_user_envs():
    for k, v in get_user_envs().items():
        os.environ[k] = v

# returns a bash string to evaluate
if __name__ == "__main__":
    bash_str = "export"
    for k,v in get_user_envs().items():
        bash_str += (" " + k + "=" + '"' + v + '"')
    print(bash_str)

