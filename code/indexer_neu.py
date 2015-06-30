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


#----------------------------------------------------------------------
# From here on: Stemming / Stopword Recognition / Saving into Database
#----------------------------------------------------------------------


some_engine = create_engine(DB_URI, echo=DEBUG) 
Session = sessionmaker(bind=some_engine) 
session = Session()





def indexer(doc_id, sites):
	soup = BeautifulSoup(sites)
	for child in soup.body:
		if isinstance(child,Comment):
			child.extract()

	body_text = soup.body.getText()

	char_dict = {'?':'', '!':'', '-':'', ';':'', ':':'', '.':'', '...':'', '\n':' ', '/':'', '+':'', '<':'', '>':'', '}':'', '{':'', '=':'', ']':'', '[':'', ')':'', '(':'', '|':''}
	for i, j in char_dict.iteritems():
		body_text = body_text.replace(i, j)		
	word_list = body_text.lower().split()


	
	# save every word plus stem, count, etc. in the database/dictionary
	stop = stopwords.words('english') # Use english stopword list from nltk corpus

	word_pos = 0 # Counter for word position
	stemmer=PorterStemmer()
	length_website = 0 # Counter for text length
	
	dict_duplicate={}	
	for element in word_list:
		length_website=length_website+1	
		word_count = word_list.count(element)
		if element not in dict_duplicate.keys():
			dict_duplicate[element]=True
			try:
				word_stem = stemmer.stem(element)
				 # Number of the word in this text
				if element in stop:
					is_stop = 1
				else:
					is_stop = 0
				#word_insert = wordtable.insert().execute(word=element, stem=word_stem, stopword=is_stop, number=word_count)
				#word_id = word_insert.inserted_primary_key
				#wdf_word = log(word_count)/log(2) +1 / log (length_website) /log(2)
				#
				#relation.insert().execute(document_documentid=doc_id, wordlist_wordid=word_id[0], wdf=wdf_word)
				word_pos = word_pos+1
			except:
				pass
		else:
			pass
		# Number of the word in this text
			#wdf_word = log(word_count)/log(2) +1 / log (length_website) /log(2)
			#relation.insert().execute(document_documentid=doc_id, wordlist_wordid=word_id[0], wdf=wdf_word)


if __name__ == "__main__":	
	
	html_document = session.query(Document.id, Document.html_document).all()
	for element in html_document:
		
		indexer(element[0],element[1])


N = session.query(Document).count()
print N
words=session.query(Wordlist.word).all()
print words
for element in words:
	n = words.count(element)
	print n
	IDF = float(log(N/n))+1/log(2)
#wordtable.update().execute(idf=IDF) 

