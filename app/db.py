import os
from pathlib import Path

import pymysql
from dotenv import load_dotenv

# Load .env that sits next to this file
load_dotenv(Path(__file__).with_name(".env"))


def get_conn():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        user=os.getenv("DB_USER", "tlapp"),
        password=os.getenv("DB_PASSWORD", "apppass"),
        database=os.getenv("DB_NAME", "twinliquors"),
        port=3306,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )
