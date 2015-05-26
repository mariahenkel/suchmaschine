# -*- coding: utf-8 -*-

from sqlalchemy import (Column, Boolean, Integer, Text,
                        ForeignKey, String, Float, BLOB)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import DB_URI, DEBUG
Base = declarative_base()


class Document(Base):

    """
    Class Document
    """
    __tablename__ = "document"
    id = Column(Integer, primary_key=True)
    url = Column(String(500))
    title = Column(Text)
    ranking = Column(Float)
    html_document = Column(Text)
    thumbnail = Column(BLOB)
    number_of_gifs = Column(Integer)
    backgroundmusic = Column(Boolean)
    musicloop = Column(Boolean)
    font_existing = Column(Boolean)
    font_number = Column(Integer)
    fontformat = Column(Boolean)
    pagestructure = Column(Boolean)
    colour = Column(Integer)
    textanimation = Column(Integer)
    phrases = Column(Integer)
    picture_distorted = Column(Integer)
    deadlinks = Column(Integer)
    hitcounter = Column(Boolean)
    guestbook = Column(Boolean)
    advertising = Column(Integer)
    shoutbox = Column(Boolean)
    htmlversion = Column(Integer)
    w3c = Column(Integer)
    popups = Column(Boolean)
    flash = Column(Boolean)
    overall_score = Column(Float)
    wordlists = relationship("ConsistsOf", backref="document")


class Wordlist(Base):

    """
 Class wordlist

"""
    __tablename__ = "wordlist"
    id = Column(Integer, primary_key=True)
    word = Column(String(50))
    stem = Column(String(50))
    stopword = Column(Boolean)
    number = Column(Integer)
    idf = Column(Float)


class ConsistsOf(Base):

    """
 Relation ConsistsOf

"""
    __tablename__ = "consists_of"
    sentenceno = Column(Integer)
    position = Column(Integer)
    stopword = Column(Integer)
    wdf = Column(Float)
    document_documentid = Column(
        Integer, ForeignKey("document.id"), primary_key=True)
    wordlist_wordid = Column(
        Integer, ForeignKey("wordlist.id"), primary_key=True)
    wordlist = relationship("Wordlist", backref="document_assocs")

if __name__ == "__main__":
    engine = create_engine(DB_URI, echo=DEBUG)
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
