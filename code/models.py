# -*- coding: utf-8 -*-

from sqlalchemy import (Column, Boolean, Integer, Text,
                        ForeignKey, String, Float)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from defaultconfig import DB_URI, DEBUG
Base = declarative_base()

# Definition of database classes
# Class Document


class Document(Base):
    __tablename__ = "document"
    id = Column(Integer, primary_key=True)
    url = Column(String(2000))
    title = Column(Text)
    ranking = Column(Float)
    language = Column(String(3))
    html_document = Column(Text)
    number_of_gifs = Column(Integer)
    backgroundmusic = Column(Boolean)
    musicloop = Column(Boolean)
    font_existing = Column(Boolean)
    font_number = Column(Integer)
    pagestructure = Column(Boolean)
    colour = Column(Integer)
    textanimation = Column(Integer)
    phrases = Column(Integer)
    picture_distorted = Column(Integer)
    deadlinks = Column(Integer)
    hitcounter = Column(Boolean)
    guestbook = Column(Boolean)
    w3c = Column(Integer)
    popups = Column(Boolean)
    flash = Column(Boolean)
    overall_score = Column(Float)
    wordlists = relationship("ConsistsOf", backref="document")

# Class Wordlist


class Wordlist(Base):
    __tablename__ = "wordlist"
    id = Column(Integer, primary_key=True)
    word = Column(String(50))
    stem = Column(String(50))
    stopword = Column(Boolean)
    number = Column(Integer)
    idf = Column(Float)

# Class/Relation ConsistsOf


class ConsistsOf(Base):
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
