import os
from pathlib import Path

import pymysql
from dotenv import load_dotenv

# Load .env that sits next to this file (path-safe no matter the CWD)
load_dotenv(Path(__file__).with_name(".env"))


def get_conn():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "tlapp"),
        password=os.getenv("DB_PASSWORD", ""),  # must not be empty
        database=os.getenv("DB_NAME", "twinliquors"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )
