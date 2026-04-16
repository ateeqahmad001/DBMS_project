import logging
from pathlib import Path
import pymysql
from config import Config

logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent.parent
CA_PATH = BASE_DIR / "certs" / "ca.pem"


# def get_db():
#     return pymysql.connect(
#         host=Config.MYSQL_HOST,
#         user=Config.MYSQL_USER,
#         password=Config.MYSQL_PASSWORD,
#         database=Config.MYSQL_DB,
#         port=Config.MYSQL_PORT,
#         cursorclass=pymysql.cursors.DictCursor,
#         autocommit=True
#     )

def get_db():
    connect_args = dict(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        port=Config.MYSQL_PORT, 
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
        connect_timeout=10,
        read_timeout=30,
        write_timeout=30,
    )

    if Config.MYSQL_SSL:
        if not CA_PATH.exists():
            logger.error(f"Aiven CA certificate not found: {CA_PATH}")
            raise FileNotFoundError(f"Aiven CA certificate not found: {CA_PATH}")
        connect_args["ssl"] = {
            "ca": str(CA_PATH),
            "check_hostname": False 
        }

    try:
        return pymysql.connect(**connect_args)
    except pymysql.MySQLError as exc:
        logger.error(f"Database connection failed: {exc}")
        raise
