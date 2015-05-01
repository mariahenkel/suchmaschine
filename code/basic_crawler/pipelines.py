# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import config
from models import Document


# function which creates a new connection to the database
def db_connect():
    return create_engine(config.DB_URI, convert_unicode=True)


# helpful function to avoid integrity errors as found at
# http://stackoverflow.com/a/2587041/2175370
def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        return instance


class InvertaPipeline(object):

    """Pipeline for the spider.
    Creates an connection and session for the database
    using db_connect() and adds a crawled webpage item to the database.
    The session is closed afterwards."""

    def __init__(self):
        engine = db_connect()
        self.Session = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=engine))

    def process_item(self, item, spider):
        session = self.Session()
        try:
            page = get_or_create(session, Document, url=item["link"])
            session.flush()
            page.html_document = item["body"]
            page.title = item["title"]
            session.commit()
        except Exception as e:
            print e
            session.rollback()
            raise
        finally:
            session.close()
        return item
