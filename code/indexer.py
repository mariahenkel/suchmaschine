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
#from models import Wordlist, Document

# Encoding for the file
reload(sys)
sys.setdefaultencoding("utf-8")

# Establish connection, load all necessary tables
engine = create_engine(config.DB_URI, echo=True)
metadata = MetaData(bind=engine)
wordtable = Table("wordlist", metadata, autoload=True)
webpage = Table("document", metadata, autoload=True) # webpage = "document" from the database

# Loading the source code from the database
s = select([webpage.c.html_document]) # wepage is a variable for document (see comment above), c = column, html_document = html sourcecode from document in the database
result = s.execute()

# Jede Ergebniszeile (row) ist eine Liste mit einem Inhalt (item).
# Momentan wird nur das letzte Ergebnis benutzt, weil die Schleife nicht mit dem Rest verbunden ist.
for row in result:
	for item in row:
		site = item

# Opening the site/file
#soup = BeautifulSoup(open("index.html")) # Testversion with a cusom file
soup = BeautifulSoup(site)

# Deleting all comments in the html file/site
for child in soup.body:
    if isinstance(child,Comment):
        child.extract()

# Deliver the site text via beautifulsoup and create a word list for further processing
body_text = soup.body.getText()

# Deleting punctuation characters
# Könnte man noch andersherum machen: If not in a.....z: replace
char_dict = {'?':'', '!':'', '-':'', ';':'', ':':'', '.':'', '...':'', '\n':' ', '/':'', '+':'', '<':'', '>':'', '}':'', '{':'', '=':'', ']':'', '[':'', ')':'', '(':'', '|':''}
for i, j in char_dict.iteritems():
    body_text = body_text.replace(i, j)

# Split string into words and transform to lowercase text
word_list = body_text.lower().split( ) 



#----------------------------------------------------------------------
# From here on: Stemming / Stopword Recognition / Saving into Database
#----------------------------------------------------------------------

stop=stopwords.words('english') # Use english stopword list from nltk corpus
rdict={} # Testversion that writes into a dictionary

word_pos = 0 # Counter for word position
stemmer=PorterStemmer()

# save every word plus stem, count, etc. in the database/dictionary
for element in word_list:
	try:
		word_stem = stemmer.stem(element)
		word_count=word_list.count(element)
		if element in stop:
			is_stop = 1
		else:
			is_stop = 0
		#rdict[word_pos]=[element,word_stem,is_stop,word_count] # testversion saves into a dictionary
		#Wordlist: id, word, stem, stopword, number, idf # structure of wordlist table
		wordtable.insert().execute(word=element, stem=word_stem, stopword=is_stop, number=word_pos, idf=word_count)
		# Position plus one
		word_pos = word_pos+1
	except:
		pass

#print rdict # Testversion prints dictionary
