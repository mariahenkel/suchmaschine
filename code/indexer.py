# -*- coding: utf-8 -*-
# 
#import csv
# Encoding für die Datei
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
# Die folgende Zeile führt unter Linux zu einer Fehlermeldung. Bitte ggf. (ent)kommentieren.
#from BeautifulSoup import BeautifulSoup
# Import von BS und Comment 
from bs4 import BeautifulSoup, Comment
# Stoppwortliste
from nltk.corpus import stopwords
# Stemmer
from nltk.stem import PorterStemmer

# Öffnen der Datei/Seite
soup = BeautifulSoup(open("index.html"))
# Entfernen der Kommentare
for child in soup.body:
    if isinstance(child,Comment):
        child.extract()

# Übergabe des Bodys
body_texts = soup.body(text=True)

# Listenerstellung
liste=[]
for element in body_texts:
	liste.append(element)

# Liste entfernen???
reine_textdatei=" ".join(liste).lower()

# Datei öffnen und mit Daten füllen
with open("extrahier.txt", "a") as datei:
	for element in reine_textdatei:
		datei.write(element)

#---------------------------------------------------------  
# Ab hier Stemming / Stoppworterkennung
#---------------------------------------------------------

#Worte extrahieren 
liste=[]
with open("extrahier.txt", "r") as datei:
	worteextrahieren=datei.read().split()
	#print worteextrahieren


#-----------------------------------------------------------
#Anzahl der Worte, Stoppwortmarkierung und gestemmtes Wort werden angezeigt

stop=stopwords.words('english')
dict={}

for element in worteextrahieren:
	try:
		if element not in dict.keys():
			stemmer=PorterStemmer()
			gestemmtes_wort= stemmer.stem(element)

			if element in stop:
				dict[element]=[1,True, gestemmtes_wort]
			else:
				dict[element]=[1,False, gestemmtes_wort]
		else:
			haufigkeit=worteextrahieren.count(element)
			if element in stop:
				dict[element]=[haufigkeit, True, gestemmtes_wort]
			else:
				dict[element]=[haufigkeit, False, gestemmtes_wort]
	except:
		pass

print dict
