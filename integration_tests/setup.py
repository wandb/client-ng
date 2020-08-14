import MySQLdb

import os

default_user = {
    'email': 'local-integration-tests@wandb.com',
    'username': 'local-integrations',
    'name': 'Ada Lovelace',
    'password': 'perceptron',
    'auth_id': 'FAKE_AUTH_ID',
    'api_key': 'FAKE_API_KEY'
}

def new_user(db, user_info):
    username = user_info['username']
    email = user_info['email']
    name = user_info['name']
    auth_id = user_info['auth_id']
    api_key = user_info['api_key']

    cursor = db.cursor()

    cursor.execute('''INSERT INTO subscriptions
        (created_at,
         updated_at,
         name,
         `limits`,
         `usage`,
         start_date,
         end_date
        )
        VALUES
        (NOW(),
         NOW(),
         "subscription",
         "{}",
         "{}",
         NOW(),
         NOW()
        )
    ''')
    db.commit()
    subscription_id = cursor.lastrowid

    cursor.execute('''INSERT INTO entities
        (created_at,
         updated_at,
         name,
         photo_url,
         subscription_id
        )
        VALUES
        (NOW(),
         NOW(),
         "%s",
         '',
         %d
        )
    ''' % (username, subscription_id))
    db.commit()
    entity_id = cursor.lastrowid

    cursor.execute('''INSERT INTO users
        (created_at,
         updated_at,
         auth_id,
         username,
         name,
         email,
         photo_url,
         default_entity_id,
         admin
        )
        VALUES
        (NOW(),
         NOW(),
         "%s",
         "%s",
         "%s",
         "%s",
         "",
         %d,
         0
        )
    ''' % (auth_id, username, name, email, entity_id))
    db.commit()
    user_id = cursor.lastrowid

    cursor.execute('''INSERT INTO users_auth0
        (user_id,
         auth_id
        )
        VALUES
        (%d,
         "%s"
        )
    ''' % (user_id, auth_id))
    db.commit()

    cursor.execute('''INSERT INTO api_keys
        (`key`,
         user_id
        )
        VALUES
        ("%s",
         %d
        )
    ''' % (api_key, user_id))
    db.commit()

def get_user_id(db):
    cursor = db.cursor()

    cursor.execute("SELECT id FROM users u WHERE u.email='local-integration-tests@wandb.com'")
    row = cursor.fetchone()
    if row == None:
        return None
    return row[0]

def get_user_name(db):
    cursor = db.cursor()

    cursor.execute("SELECT id FROM users u WHERE u.name='local-integration-tests@wandb.com'")
    row = cursor.fetchone()
    if row == None:
        return None
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
    uid = get_user_id(db)
    if uid == None:
        new_user(db, default_user)
        uid = get_user_id(db)
    api_key = get_api_key(db, uid)
    return {"WANDB_API_KEY": api_key,
            "WANDB_BASE_URL": "http://localhost:8080",
            "WANDB_USERNAME": default_user['username']}


def set_user_envs():
    for k, v in get_user_envs().items():
        os.environ[k] = v

# returns a bash string to evaluate
if __name__ == "__main__":
    bash_str = "export"
    for k,v in get_user_envs().items():
        bash_str += (" " + k + "=" + '"' + v + '"')
    print(bash_str)

