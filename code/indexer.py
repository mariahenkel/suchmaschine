# -*- coding: utf-8 -*-

import sys

# Die folgende Zeile führt unter Linux zu einer Fehlermeldung. Bitte ggf. (ent)kommentieren.
#from BeautifulSoup import BeautifulSoup

from bs4 import BeautifulSoup, Comment # BeautifulSoup und Comment
from nltk.corpus import stopwords # Stoppwortliste
from nltk.stem import PorterStemmer # Stemmer

# Encoding für die Datei
reload(sys)
sys.setdefaultencoding("utf-8")

# Öffnen der Datei/Seite
soup = BeautifulSoup(open("index.html"))

# Entfernen der Kommentare
for child in soup.body:
    if isinstance(child,Comment):
        child.extract()

# Übergabe des Textes und Erstellung einer Wortliste zur Weiterverarbeitung
body_text = soup.body.getText()

#Es müssen noch Satzzeichen und andere Störfaktoren entfert werden
char_dict = {'?':'', '!':'', '-':'', ';':'', ':':'', '.':'', '...':'', '\n':' '}
for i, j in char_dict.iteritems():
    body_text = body_text.replace(i, j)


word_list = body_text.lower().split( ) 



#---------------------------------------------------------  
# Ab hier Stemming / Stoppworterkennung
#---------------------------------------------------------

#Anzahl der Worte, Stoppwortmarkierung und gestemmtes Wort werden angezeigt

stop=stopwords.words('english')
rdict={}

word_id = 0
stemmer=PorterStemmer()

for element in word_list:
	try:
		word_stem = stemmer.stem(element)
		word_count=word_list.count(element)
		if element in stop:
			is_stop = True
		else:
			is_stop = False
		rdict[word_id]=[element,word_count,is_stop,word_stem]
		word_id = word_id+1
	except:
		pass

print rdict
