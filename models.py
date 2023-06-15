import json
from sqlalchemy import INT, FLOAT, String, Unicode, DateTime, UnicodeText, BOOLEAN, INTEGER, BIGINT, LargeBinary
from sqlalchemy import create_engine, Column, MetaData, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import enum
from logzero import logger

Base = declarative_base()
connection_string = 'sqlite:///divar_db.sqlite'


class PageStatus(enum.IntEnum):
    ReadyToCrawl = 0
    NoInfo = 50
    NoImage = 90
    Finished = 100
    NotFound = 404
    AccessDenied = 403
    ServerError = 500
    Problem = 666


class StatusException(Exception):
    def __init__(self, status_code):
        self.status_code = status_code


class Advertises(Base):
    __tablename__ = 'Advertises'
    Id = Column(INT, primary_key=True)
    Phone = Column(String, default=None)
    Title = Column(String, default=None)
    City = Column(String, default=None)
    NeighbourHood = Column(String, default=None)
    Rooms = Column(INT, default=None)
    Media = Column(String, default=None)
    AdvertiseUrl = Column(String, default=None)
    Descriptions = Column(String, default=None)
    Status = Column(INT, default=PageStatus.ReadyToCrawl)
    RetryCount = Column(INT, default=0)
    LastUpdate = Column(DateTime, default=datetime.utcnow())

    def __repr__(self):
        return f"ID: {self.Id}, Ad_title: {self.Title}"


class IranAdvertises(Base):
    __tablename__ = 'IranAdvertises'
    Id = Column(INT, primary_key=True)
    Phone = Column(String, default=None)
    Title = Column(String, default=None)
    City = Column(String, default=None)
    NeighbourHood = Column(String, default=None)
    Rooms = Column(INT, default=None)
    Media = Column(String, default=None)
    AdvertiseUrl = Column(String, default=None)
    Descriptions = Column(String, default=None)
    Status = Column(INT, default=PageStatus.ReadyToCrawl)
    RetryCount = Column(INT, default=0)
    LastUpdate = Column(DateTime, default=datetime.utcnow())

    def __repr__(self):
        return f"ID: {self.Id}, Ad_title: {self.Title}"


class VillaAdvertises(Base):
    __tablename__ = 'VillaAdvertises'
    Id = Column(INT, primary_key=True)
    Phone = Column(String, default=None)
    Title = Column(String, default=None)
    City = Column(String, default=None)
    NeighbourHood = Column(String, default=None)
    Rooms = Column(INT, default=None)
    Media = Column(String, default=None)
    AdvertiseUrl = Column(String, default=None)
    Descriptions = Column(String, default=None)
    Status = Column(INT, default=PageStatus.ReadyToCrawl)
    RetryCount = Column(INT, default=0)
    LastUpdate = Column(DateTime, default=datetime.utcnow())

    def __repr__(self):
        return f"ID: {self.Id}, Ad_title: {self.Title}"

def create_db():
    logger.info('Creating Database')
    engine = create_engine(connection_string)
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    create_db()
    # engine = create_engine(connection_string)
