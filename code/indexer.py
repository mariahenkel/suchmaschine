# -*- coding: utf-8 -*-

import sys

# Die folgende Zeile führt unter Linux zu einer Fehlermeldung. Bitte ggf. (ent)kommentieren.
#from BeautifulSoup import BeautifulSoup

from bs4 import BeautifulSoup, Comment # BeautifulSoup und Comment
from nltk.corpus import stopwords # Stoppwortliste
from nltk.stem import PorterStemmer # Stemmer

#SQLAlchemy
from sqlalchemy import create_engine, select
from sqlalchemy import MetaData, Table
import config
from models import Wordlist, Document

# Encoding für die Datei
reload(sys)
sys.setdefaultencoding("utf-8")

#Verbindung herstellen, Tabellen laden
engine = create_engine(config.DB_URI, echo=True)
metadata = MetaData(bind=engine)
wordtable = Table("wordlist", metadata, autoload=True)
webpage = Table("document", metadata, autoload=True)

# Nimm den Quelltext aus der Datenbank
s = select([webpage.c.html_document]) 
result = s.execute()
 
# Jede Ergebniszeile (row) ist eine Liste mit einem Inhalt (item).
# Momentan wird nur das letzte Ergebnis benutzt, weil die Schleife nicht mit dem Rest verbunden ist.
# Nächste Aufgabe: Modularisierung!!!
for row in result:
	for item in row:
		site = item

# Öffnen der Datei/Seite
#soup = BeautifulSoup(open("index.html")) # Testversion
soup = BeautifulSoup(site)

# Entfernen der Kommentare
for child in soup.body:
    if isinstance(child,Comment):
        child.extract()

# Übergabe des Textes und Erstellung einer Wortliste zur Weiterverarbeitung
body_text = soup.body.getText()

#Es müssen noch Satzzeichen und andere Störfaktoren entfert werden
# Könnte man noch andersherum machen: If not in a.....z: replace
# Man könnte für ./?/! einen end_of_sentence_indicator einbauen und so die Sätze zählen
char_dict = {'?':'', '!':'', '-':'', ';':'', ':':'', '.':'', '...':'', '\n':' ', '/':'', '+':'', '<':'', '>':'', '}':'', '{':'', '=':'', ']':'', '[':'', ')':'', '(':'', '|':''}
for i, j in char_dict.iteritems():
    body_text = body_text.replace(i, j)

#Den String aus dem Body-Text aufteilen in einzelne Wörter und alles klein schreiben
word_list = body_text.lower().split( ) 



#----------------------------------------------------------------------
# Ab hier Stemming / Stoppworterkennung / Einspeisung in die Datenbank
#----------------------------------------------------------------------

#Dokument-ID???, Wort, Wort-Stamm, Stoppwort(0/1), Position, Anzahl (für WDF/IDF)

stop=stopwords.words('english')
rdict={}

word_pos = 0
stemmer=PorterStemmer()

for element in word_list:
	try:
		word_stem = stemmer.stem(element)
		word_count=word_list.count(element)
		if element in stop:
			is_stop = 1
		else:
			is_stop = 0
		rdict[word_pos]=[element,word_stem,is_stop,word_count]
		#Daten einfügen
		#Wordlist: id, word, stem, stopword, number, idf
		#wordtable.insert().execute(word=element, stem=word_stem, stopword=is_stop, number=word_pos, idf=word_count)
		# Position weiterzählen
		word_pos = word_pos+1
	except:
		pass

print rdict # Zum Testen
