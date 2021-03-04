from sqlalchemy import MetaData
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Date, String, Float, Index, Text, Boolean, select
from sqlalchemy.dialects.mysql import LONGTEXT, MEDIUMINT
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.engine import Engine
from typing import Optional, List
from core.persistence import CorePersistence
import os
import time
from core.util import md5
from .items import TaskMetaItem
from sqlalchemy.dialects.mysql import insert
from urllib.parse import urlparse, parse_qsl
from core.util import path_format

# from .utils import Space, Novel
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

    Column("description", Text, nullable=True),
    Column("upload_date", Integer, nullable=False),
    Column("type", String(255), nullable=False),
    Index("type_index", "type"),

    Column("is_del", Boolean, nullable=False, default=False),
    Index("is_del_index", "is_del"),
)
VideoTable = Table(
    "videos",
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


class IwaraPersistence(CorePersistence):
    def __init__(self, database_name):
        self.__engine: Optional[Engine] = None
        self.__database_name = database_name
        self.__init_database()

    def __init_database(self):
        _db_host = os.environ.get('MYSQL_SERVICE')
        _mysql_url = "mysql+pymysql://root:scrapy_db@%s:3306" % _db_host

        _engine = create_engine("%s/%s" % (_mysql_url, self.__database_name))
        if not database_exists(_engine.url):
            create_database(_engine.url)
        metadata.create_all(_engine)
        self.__engine = _engine
        return self.__engine

    def __enter__(self):
        pass
        # with self.__engine.connect() as _connect:
        #     return _connect

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def filter(self, ids: List, group: str):
        with self.__engine.connect() as _connect:
            _has = select([WorkTable.columns.id]).where(WorkTable.columns.id.in_(ids)).where(WorkTable.columns.is_del == 0).where(WorkTable.columns.type == group)
            # print(_has)
            _data = _connect.execute(_has)
            _has_ids = [item[0] for item in _data]
            print(_has_ids)
            _diff_ids = set(ids).difference(_has_ids)
            return _diff_ids

    def save(self, item: TaskMetaItem):
        with self.__engine.connect() as _connect:
            # author
            insert_session = insert(AuthorTable).values(
                primary="author_%s" % item['author']['id'],
                id=item['author']['id'],
                name=item['author']['name']
            )
            duplicate_key_session = insert_session.on_duplicate_key_update(
                is_del=False,
            )
            _connect.execute(duplicate_key_session)

            # works
            _time = time.mktime(time.strptime(item['upload_date'], "%Y-%m-%d %H:%M"))
            insert_session = insert(WorkTable).values(
                primary="works_%s" % item['id'],
                id=item['id'],
                name=item['title'],
                author_id=item['author']['id'],
                description=item['description'],
                upload_date=_time,
                type=item['type']
            )

            duplicate_key_session = insert_session.on_duplicate_key_update(
                is_del=False,
                upload_date=_time,
            )
            _connect.execute(duplicate_key_session)

            # video
            for _resource in item['sources']:
                _parse = urlparse(_resource)
                _query = dict(parse_qsl(_parse.query))
                _file = "%s%s" % (item['title'], os.path.splitext(_query['file'])[-1])

                resource_path = "/".join([
                    path_format(item['author']['name']),
                    path_format(item['title']),
                    _file
                ])
                insert_session = insert(VideoTable).values(
                    primary="video_%s_%s" % (item['id'], md5(_resource)),
                    id=md5(_resource),
                    work_id=item['id'],
                    source=_resource,
                    path=resource_path
                )

                # _item = request.meta['item']
                # _resource = request.meta['resource']
                # _parse = urlparse(_resource)
                # _query = dict(parse_qsl(_parse.query))
                # _file = "%s%s" % (_item['title'], os.path.splitext(_query['file'])[-1])
                #
                # resource_path = "/".join([
                #     path_format(_item['author']['name']),
                #     path_format(_item['title']),
                #     _file
                # ])

                duplicate_key_session = insert_session.on_duplicate_key_update(
                    is_del=False,
                )
                _connect.execute(duplicate_key_session)
