# -*- coding: utf-8 -*-

import sys

# Die folgende Zeile führt unter Linux zu einer Fehlermeldung. Bitte ggf. (ent)kommentieren.
#from BeautifulSoup import BeautifulSoup

from bs4 import BeautifulSoup, Comment # Import BeautifulSoup und Comment
from nltk.corpus import stopwords # Import Stopword list
from nltk.stem import PorterStemmer # Import Stemmer

#SQLAlchemy imports
from sqlalchemy import create_engine, select
from sqlalchemy import MetaData, Table
import config
from math import log
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.orm import sessionmaker 
from config import DB_URI, DEBUG 
from models import Wordlist, Document, ConsistsOf
#from models import wordlist, document
#from database import db_session

# Encoding for the file
reload(sys)
sys.setdefaultencoding("utf-8")

# Establish connection, load all necessary tables
engine = create_engine(config.DB_URI, echo=True)
metadata = MetaData(bind=engine)
wordtable = Table("wordlist", metadata, autoload=True)
webpage = Table("document", metadata, autoload=True)
relation = Table("consists_of", metadata, autoload=True)

Base = declarative_base()

# Loading the source code from the database
#s = select([webpage.c.html_document]) 
#result = s.execute()
#for line in result:
#	print line

# Jede Ergebniszeile (row) ist eine Liste mit einem Inhalt (item).
# Momentan wird nur das letzte Ergebnis benutzt, weil die Schleife nicht mit dem Rest verbunden ist.
#for row in result:
#	for item in row:
#		site = item

# Opening the site/file
#soup = BeautifulSoup(open("index.html")) # Testversion with a cusom file
#soup = BeautifulSoup (site)

# Deleting all comments in the html file/site
#for child in soup.body:
 #   if isinstance(child,Comment):
  #      child.extract()

# Deliver the site text via beautifulsoup and create a word list for further processing
#body_text = soup.body.getText()

# Deleting punctuation characters
# Könnte man noch andersherum machen: If not in a.....z: replace
#char_dict = {'?':'', '!':'', '-':'', ';':'', ':':'', '.':'', '...':'', '\n':' ', '/':'', '+':'', '<':'', '>':'', '}':'', '{':'', '=':'', ']':'', '[':'', ')':'', '(':'', '|':''}
#for i, j in char_dict.iteritems():
 #   body_text = body_text.replace(i, j)

# Split string into words and transform to lowercase text
#word_list = body_text.lower().split( ) 

#----------------------------------------------------------------------
# From here on: Stemming / Stopword Recognition / Saving into Database
#----------------------------------------------------------------------

#stop=stopwords.words('english') # Use english stopword list from nltk corpus
#rdict={} # Testversion that writes into a dictionary

#word_pos = 0 # Counter for word position
#stemmer=PorterStemmer()

#Ueberlegung:
#x=session.query(Document.id, document.html_document, document.url).all()
#for element in x:
#	try:

#		word_stem = stemmer.stem(element[1])
#		word_count=word_list.count(element)


#Funktion beautifulsoup erstellen mit bereinigung)
#
#java script 

def save_word(word_list):
# save every word plus stem, count, etc. in the database/dictionary
	stop=stopwords.words('english') # Use english stopword list from nltk corpus
	rdict={} # Testversion that writes into a dictionary
	word_pos = 0 # Counter for word position
	stemmer=PorterStemmer()

	for element in word_list:
		try:
			word_stem = stemmer.stem(element)
			word_count = word_list.count(element) # number of the word in this text
			if element in stop:
				is_stop = 1
			else:
				is_stop = 0
			rdict[word_pos]=[id,element,word_stem,is_stop,word_count] # testversion saves into a dictionary
			#Wordlist: id, word, stem, stopword, number, idf # structure of wordlist table
			

			wordtable.insert().execute(word=element, stem=word_stem, stopword=is_stop, number=word_pos, idf=word_count)
			
			# Position plus one
			word_pos = word_pos+1
		except:
			pass
	return rdict



###ab hier probiere ich im prinzip alles aus###
some_engine = create_engine(DB_URI, echo=DEBUG) 
Session = sessionmaker(bind=some_engine) 
session = Session()

def bodyextraction(sites):
	soup = BeautifulSoup(sites)
	for child in soup.body:
		if isinstance(child,Comment):
			child.extract()

	body_text = soup.body.getText()

	char_dict = {'?':'', '!':'', '-':'', ';':'', ':':'', '.':'', '...':'', '\n':' ', '/':'', '+':'', '<':'', '>':'', '}':'', '{':'', '=':'', ']':'', '[':'', ')':'', '(':'', '|':''}
	for i, j in char_dict.iteritems():
		body_text = body_text.replace(i, j)	
	
	word_list = body_text.lower().split()
	#print save_word(word_list)
	return save_word(word_list)
	
if __name__ == "__main__":
	dict={}
	x=session.query(Document.id, Document.html_document).all()
	
	for element in x:
		print element[0]
		if element[1] not in dict.values():
			b = bodyextraction(element[1])
			for element in x:
				x = element[1].split()
				for word in x:
					for x,y in dict1.items():
						if y == word:
							relation.insert().execute(document_documentid=element[0], wordlist_wordid=x)

			print "Document ID: ", element[0], "\nDict mit WordID, Word, Stem, Stopword, Anzahl: ", b, "\n"
			#dict[element[0]]=b
		else:
			pass

#	print dict
#dict={}
#dictcount={}
#length_website=0
#html_content=session.query(Document.id, Document.title).all()
#for element in html_content:
#	if element not in dict.keys():
#		dict[element[0]]=element[1]
#		print dict
#		length_website=length_website+1
#		dictcount[element[0]]=length_website
#	else:
#		pass
#print dictcount

#dict1={}
#words=session.query(Wordlist.id, Wordlist.word).all()
#for element in words:
#	if element not in dict1.keys():
#		dict1[element[0]]=str(element[1]).capitalize()
#	else:
#		pass

for element in html_content:
	x = element[1].split()
	for word in x:
		for x,y in dict1.items():
			if y == word:
				relation.insert().execute(document_documentid=element[0], wordlist_wordid=x)
				#print "Ja Wort kommt vor: ", word, ", ", "Dokument ID: ", element[0], ", ", "Word ID: ", x
#print rdict # Testversion prints dictionary