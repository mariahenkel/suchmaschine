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

# TO DO: Es müssen noch Satzzeichen und andere Störfaktoren entfert werden!

# Übergabe des Textes und Erstellung einer Wortliste zur Weiterverarbeitung
body_text = soup.body.getText()
word_list = body_text.lower().split( ) # Hier geht die Reihenfolge verloren!!!

#---------------------------------------------------------  
# Ab hier Stemming / Stoppworterkennung
#---------------------------------------------------------

#Anzahl der Worte, Stoppwortmarkierung und gestemmtes Wort werden angezeigt

stop=stopwords.words('english')
dict={}

for element in word_list:
	try:
		if element not in dict.keys():
			stemmer=PorterStemmer()
			gestemmtes_wort= stemmer.stem(element)

			if element in stop:
				dict[element]=[1,True, gestemmtes_wort]
			else:
				dict[element]=[1,False, gestemmtes_wort]
		else:
			haufigkeit=word_list.count(element)
			if element in stop:
				dict[element]=[haufigkeit, True, gestemmtes_wort]
			else:
				dict[element]=[haufigkeit, False, gestemmtes_wort]
	except:
		pass

print dict
