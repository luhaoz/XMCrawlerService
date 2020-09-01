from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Date, String, Float, Index, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.mysql import insert
from sqlalchemy import MetaData
import hashlib
from sqlalchemy.dialects.mysql import LONGTEXT, MEDIUMINT
metadata = MetaData()

AuthorTable = Table(
    "authors",
    metadata,
    Column("primary", String(255), nullable=False, primary_key=True),
    Column("id", String(255), nullable=False),
    Index("id_index", "id"),
    Column("name", String(255), nullable=False),
    Index("name_index", "name"),
    Column("is_del", Boolean, nullable=False, default=False),
    Index("is_del_index", "is_del"),

)

TagTable = Table(
    "tags",
    metadata,
    Column("primary", String(255), nullable=False, primary_key=True),
    Column("id", String(255), nullable=False),
    Index("id_index", "id"),
    Column("work_id", String(255), nullable=False),
    Index("work_id_index", "work_id"),
    Column("name", String(255), nullable=False),
    Index("name_index", "name"),
    Column("is_del", Boolean, nullable=False, default=False),
    Index("is_del_index", "is_del"),
)

WorkTable = Table(
    "works",
    metadata,
    Column("primary", String(255), nullable=False, primary_key=True),
    Column("id", String(255), nullable=False),
    Index("id_index", "id"),
    Column("author_id", String(255), nullable=False),
    Index("author_id_index", "author_id"),

    Column("name", String(255), nullable=False),
    Index("name_index", "name"),

    Column("description", Text, nullable=False),

    Column("upload_date", Integer, nullable=False),
    Column("count", Integer, nullable=False),

    Column("type", String(255), nullable=False),
    Index("type_index", "type"),

    Column("is_del", Boolean, nullable=False, default=False),
    Index("is_del_index", "is_del"),
)

IllustTable = Table(
    "illusts",
    metadata,
    Column("primary", String(255), nullable=False, primary_key=True),
    Column("id", String(255), nullable=False),
    Index("id_index", "id"),

    Column("work_id", String(255), nullable=False),
    Index("work_id_index", "work_id"),

    Column("source", String(255), nullable=False),
    Column("path", String(255), nullable=False),

    Column("is_del", Boolean, nullable=False, default=False),
    Index("is_del_index", "is_del"),
)

NovelTable = Table(
    "novels",
    metadata,
    Column("primary", String(255), nullable=False, primary_key=True),
    Column("id", String(255), nullable=False),
    Index("id_index", "id"),

    Column("work_id", String(255), nullable=False),
    Index("work_id_index", "work_id"),

    Column("content", LONGTEXT, nullable=False),
    Column("path", String(255), nullable=False),

    Column("is_del", Boolean, nullable=False, default=False),
    Index("is_del_index", "is_del"),
)

# _db_host = "localhost"
_db_host = "172.16.238.10"


class Database(object):
    _engine = None
    _session = None

    @classmethod
    def engine(cls):
        if cls._engine is None:
            cls._engine = create_engine("mysql+pymysql://root:scrapy_db@%s:3306" % _db_host)
        return cls._engine

    @classmethod
    def init(cls, database_name):
        engine_default = cls.engine()
        conn = engine_default.connect()
        conn.execute("COMMIT")
        conn.execute("CREATE DATABASE IF NOT EXISTS %s" % database_name)
        conn.close()
        cls._engine = create_engine("mysql+pymysql://root:scrapy_db@%s:3306/%s" % (_db_host, database_name))
        cls.create_table()

    @classmethod
    def create_table(cls):
        metadata.create_all(cls.engine())

    @classmethod
    def session(cls):
        if cls._session is None:
            Session = sessionmaker(bind=cls.engine())
            cls._session = Session()
        return cls._session
