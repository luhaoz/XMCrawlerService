# import requests
# requests.adapters.DEFAULT_RETRIES = 5 # 增加重连次数
# s = requests.session()
# s.keep_alive = False # 关闭多余连接
# s.get('https://www.pixiv.net/') # 你需要的网址

from sqlalchemy import create_engine

# DB_CONN_URI_DEFAULT = "mysql+pymysql://root:scrapy_db@localhost:3306"
# engine_default = create_engine(DB_CONN_URI_DEFAULT)
# conn = engine_default.connect()
# conn.execute("COMMIT")
# NEW_DB_NAME = "pixiv"
# conn.execute("CREATE DATABASE %s" % NEW_DB_NAME)
# conn.close()
