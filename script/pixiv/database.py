from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Date, String, Float, Index, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Author(Base):
    __tablename__ = 'authors'
    __table_args__ = (
        Index('author_id', 'author_id'),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    author_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    is_del = Column(Boolean, nullable=False)


class Tag(Base):
    __tablename__ = 'tags'
    __table_args__ = (
        Index('name', 'name'),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    work_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    is_del = Column(Boolean, nullable=False)


class Work(Base):
    __tablename__ = 'works'
    __table_args__ = (
        Index('work_id', 'work_id'),
        Index('work_type', 'type'),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    work_id = Column(String, nullable=False)
    author_id = Column(String, nullable=False)
    upload_date = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    count = Column(Integer, nullable=False)
    is_del = Column(Boolean, nullable=False)
    type = Column(String, nullable=False)


class Illusts(Base):
    __tablename__ = 'illusts'
    __table_args__ = (
        Index('illust_id', 'illust_id'),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    work_id = Column(String, nullable=False)
    source = Column(String, nullable=False)
    path = Column(String, nullable=False)
    is_del = Column(Boolean, nullable=False)


class Novels(Base):
    __tablename__ = 'novels'
    id = Column(Integer, primary_key=True, autoincrement=True)
    work_id = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    path = Column(String, nullable=False)
    is_del = Column(Boolean, nullable=False)
