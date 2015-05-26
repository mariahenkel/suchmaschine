# -*- coding: utf-8 -*-
import csv
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from BeautifulSoup import BeautifulSoup
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from bs4 import BeautifulSoup, Comment



#llllllll
soup = BeautifulSoup(open("index.html"))
for child in soup.body:
    if isinstance(child,Comment):
        child.extract()

#soup.encode('utf-8')
#invalid_tags = ['b','div', 'i', 'p', 'ul', 'li', 'ol', 'h1', 'h2', 'h3', 'pre', 'code','a', 'blockquote', 'strong', 'em']

#BeautifulSoup(soupex, convertEntities=BeautifulSoup.HTML_ENTITIES)
#soup.html.replaceWith(u'<html>'+unicode('utf-8')+u'</html>')

#soups = BeautifulSoup.(soup.decode('utf-8','ignore'))


#test=soup.find('body')					
#for tag in invalid_tags: 
 #   for match in test.findAll(tag):
  #      match.replaceWithChildren()
body_texts = soup.body(text=True)



liste=[]
for element in body_texts:
	liste.append(element)



#for element in liste:
#	if element =="<body>" or "</body>":
#		liste.remove(element)
#	else:
#		pass

reine_textdatei=" ".join(liste).lower()


with open("extrahier.txt", "a") as datei:
	for element in reine_textdatei:
		datei.write(element)
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
