import os
from dotenv import load_dotenv
load_dotenv()
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'my-secret-key')
    MYSQL_HOST = os.environ.get('DB_HOST', 'localhost')
    MYSQL_USER = os.environ.get('DB_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('DB_PASSWORD', '')
    MYSQL_DB = os.environ.get('DB_NAME', 'gyanpustak')
    MYSQL_PORT = int(os.environ.get('DB_PORT', 3306))
    MYSQL_SSL = os.environ.get('DB_SSL', 'false').lower() == 'true'
