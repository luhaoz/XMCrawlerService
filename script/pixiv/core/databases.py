from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Date, String, Float, Index, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Illust(Base):
    __tablename__ = 'illusts'
    __table_args__ = (
        Index('illusts_illust_id', 'illust_id'),
        Index('illust_type', 'type'),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    illust_id = Column(String, nullable=False)
    author_id = Column(String, nullable=False)
    count = Column(Integer, nullable=False)
    upload_date = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    type = Column(String, nullable=False)


class Author(Base):
    __tablename__ = 'authors'
    __table_args__ = (
        Index('author_id', 'author_id'),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    author_id = Column(String, nullable=False)
    name = Column(String, nullable=False)


class Tag(Base):
    __tablename__ = 'tags'
    __table_args__ = (
        Index('name', 'name'),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    illust_id = Column(String, nullable=False)
    name = Column(String, nullable=False)


class ResourceIllust(Base):
    __tablename__ = 'resources_illust'
    __table_args__ = (
        Index('resources_illust_illust_id', 'illust_id'),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    illust_id = Column(String, nullable=False)
    source = Column(String, nullable=False)
    path = Column(String, nullable=False)


class ResourceNovels(Base):
    __tablename__ = 'resources_novel'
    __table_args__ = (
        Index('resources_novel_illust_id', 'illust_id'),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    illust_id = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    path = Column(String, nullable=False)
