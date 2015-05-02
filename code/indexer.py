# -*- coding: utf-8 -*-
import csv
from BeautifulSoup import BeautifulSoup
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

soup = BeautifulSoup(open("index.html"))
invalid_tags = ['b','div', 'i', 'p', 'ul', 'li', 'ol', 'h1', 'h2', 'h3', 'pre', 'code','a', 'blockquote', 'strong', 'em']


test=soup.find('body')					#momentanes Problem: Wenn der Code keine Tags hat, wird der Inhalt nicht übernommen
for tag in invalid_tags: 
    for match in test.findAll(tag):
        match.replaceWithChildren()

body=test


liste=[]
for element in body:
	liste.append(element)


for element in liste:
	if element =="<body>" or "</body>":
		liste.remove(element)
	else:
		pass

reine_textdatei=" ".join(liste).lower()


with open("extrahier.txt", "a") as datei:
	for element in reine_textdatei:
		datei.write(element)
#---------------------------------------------------------

#Worte extrahieren 
with open("extrahier.txt", "r") as datei:
	worteextrahieren=datei.read().split()
	#print worteextrahieren


#-----------------------------------------------------------
#Anzahl der Worte, Stoppwortmarkierung und gestemmtes Wort werden angezeigt

stop=stopwords.words('english')
dict={}

for element in worteextrahieren:
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

print dict
