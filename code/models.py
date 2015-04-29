# -*- coding: utf-8 -*-
from sqlalchemy import Column, Boolean, Integer, Text, ForeignKey, String, Float, BLOB
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
	
"""
 Klasse Dokument

"""

class Dokument(Base):
	__tablename__ = 'dokument'
	dokumentid = Column(Integer, primary_key=True)
	url = Column(String(500))
	titel = Column(String(100))
	ranking = Column(Float)
	quelltext = Column(Text)
	thumbnail = Column(BLOB)
	gifs = Column(Integer)
	musikhintergrund = Column(Boolean)
	musikloop= Column(Boolean)
	schriftart_vorhanden = Column(Boolean)
	schriftart_anzahl = Column(Integer)
	schriftformat = Column(Boolean)
	seitenstruktur = Column(Boolean)
	farbe = Column(Integer)
	textanimation = Column(Integer)
	phrasen = Column(Integer)
	bild_verzehrt = Column(Integer)
	fehlerlinks= Column(Integer)
	besucherzaehler = Column(Boolean)
	gaestebuch = Column(Boolean)
	werbung = Column(Integer)
	shoutbox = Column(Boolean)
	htmlversion = Column(Boolean)
	w3c = Column(Integer)
	popup = Column(Boolean)
	flash = Column(Boolean)
	overall_score = Column(Float)
	wortlisten = relationship('Besteht_aus', backref = 'dokument')
	
"""
 Klasse Wortliste

"""
	
class Wortliste(Base):
	__tablename__ = 'wortliste'
	wortid = Column(Integer, primary_key = True)
	wort = Column(String(50))
	wortstamm = Column(String(50))
	stoppwort = Column(Boolean)
	anzahl = Column(Integer)
	idf = Column(Float)

	
"""
 Relation besteht_aus 	

"""

class Besteht_aus(Base):
	__tablename__ = 'besteht_aus'
	satznr = Column(Integer)
	position = Column(Integer)
	stoppwort = Column(Integer)
	wdf = Column(Float)
	dokument_dokumentid = Column(Integer, ForeignKey('dokument.dokumentid'), primary_key = True)
	wortliste_wortid = Column(Integer, ForeignKey('wortliste.wortid'), primary_key = True)
	worliste = relationship('Wortliste', backref = 'dokument_assocs')
	
if __name__ == "__main__":
	engine = create_engine('sqlite:///search.db', echo=True)
	Session = sessionmaker(bind=engine)
	Base.metadata.create_all(bind=engine)
