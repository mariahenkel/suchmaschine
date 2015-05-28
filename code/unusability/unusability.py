# -*- coding: utf-8 -
import urllib
import re
from bs4 import BeautifulSoup
import requests
#from models import Document
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
#from config import DB_URI, DEBUG

#Base = declarative_base()


# Zum Testen:

with open ("beispiel2.txt", "r") as html_file:
    html = html_file.read().lower()
    html_wo_comments = re.sub("<!--.*?>", "", html) # war für beispiel2.txt nötig
    soup = BeautifulSoup(html_wo_comments)


##########
# Fonts  #
########## 

def find_bad_fonts():
    tag_attrs_lists = [] 
    tag_attrs = [] 
    for tag in soup.find_all(True):
        tag_attrs_lists.append(tag.attrs.values())
    for list in tag_attrs_lists:
        for element in list:
            tag_attrs.append(element)          

    with open("bad_fonts.txt", "r") as fonts_file:
        bad_fonts_list = [line.rstrip("\n") for line in fonts_file]      
        bad_fonts_counter = 0
        for font in bad_fonts_list:
            if any(font in s for s in tag_attrs):
                #print font
                bad_fonts_counter += 1
        if bad_fonts_counter == 0:
            bad_fonts = 0
        else:
            bad_fonts = 1
	# bad_fonts
    return bad_fonts
    
    #write_font_existing = Document(font_existing=find_bad_fonts())
    #session.add(write_font_existing)
    #session.commit()
	
def font_amount():
    tag_attrs_lists = [] 
    tag_attrs = [] 
    for tag in soup.find_all(True):
        tag_attrs_lists.append(tag.attrs.values())
    for list in tag_attrs_lists:
        for element in list:
            tag_attrs.append(element)   
                
    with open("fonts.txt", "r") as fonts_file: # Liste von Wikipedia - wäre auch möglich, alle font tags auszulesen und auszuwerten
        fonts_list = [line.lower().rstrip("\n") for line in fonts_file]      
        fonts_counter = 0
        for font in fonts_list:
            if any(font in s for s in tag_attrs):
                #print font
                fonts_counter += 1
    return fonts_counter
    
###############
# Animationen #
###############

def get_html_textanimation(html_page):
    marquee_amount = re.findall("<marquee(.)*</marquee>", str(html))  
    return len(marquee_amount)

##########
# Colors #
########## 

def find_bad_colors():
    tag_attrs_lists = [] # Jeder einzelne Tag hat eigene Liste
    tag_attrs = [] # Alle Attribute in einer Liste
    for tag in soup.find_all(True):
        tag_attrs_lists.append(tag.attrs.values())
    for list in tag_attrs_lists:
        for element in list:
            tag_attrs.append(element)          

    with open("bad_colors.txt", "r") as colors_file:
        bad_colors_list = [line.rstrip("\n") for line in colors_file]      
        color_counter = 0
        for color in bad_colors_list:
            if any(color in s for s in tag_attrs):
                color_counter += 1
                #print color
    return color_counter


##########
# Gifs   #
########## 

def get_gifs ():
    #gif_amount = re.findall("<(.)*\.gif.*?>", str(html))
    #return len(gif_amount)
    tag_attrs_lists = [] 
    tag_attrs = [] 
    for tag in soup.find_all(True):
        tag_attrs_lists.append(tag.attrs.values())
    for list in tag_attrs_lists:
        for element in list:
            tag_attrs.append(element)
    return str(tag_attrs).count(".gif")
    
    
    
##################
# Seitenstruktur #
##################

def bad_site_structure():
    h_tags = ["h1","h2","h3","h4","h5","h6"]
    return bool(soup.find_all([x for x in h_tags]))
    
        
##########
# W3C    #
########## 

def count_w3c_errors (url):
    w3c_link = "https://validator.w3.org/check?uri="
    check_url = urllib.urlopen(w3c_link+url)
    content = check_url.read()
    soup = BeautifulSoup(content)
    errors= soup.find("h3" ,class_ = "invalid")
    errors_extracted = re.findall(r'\d+', str(errors.get_text()))
    errors_extracted = [int(x) for x in errors_extracted]
    return errors_extracted[0]

##########
# Other  #
########## 


def find_guestbook():
    if "guestbook" in html:
        guestbook = 1
    else:
        guestbook = 0
    return guestbook


def find_phrases():
    with open("phrases.txt", "rb") as phrases_file:
        phrases_list = [line.rstrip("\n\r") for line in phrases_file]
    phrases_counter = 0 
    for phrase in phrases_list:
        if phrase in html:
            phrases_counter += 1
            #print phrase
    return phrases_counter

def find_dead_links():
    links = []
    for link in soup.find_all('a'):
        if link.get("href"):
            # Mit dem http wird sichergestellt, dass keine internen Links geprüft werden
            # Muss ich nochmal gucken, ob ich das auch noch hinkrieg, sonst kommt es immer zu Fehlern
            if link.get('href').startswith("http"):
                links.append(link.get('href')) 
    dead_links = 0
    for index, link in enumerate(links):
        try:
            r = requests.get(link)
            if str(r.status_code).startswith("4"):
                dead_links += 1      
        except:
            dead_links +=1

    return dead_links
    
##########
# Musik    #
########## 

def music():
    auto_loop = False
    check_audio_tag = soup.find_all("audio")
    if "autoplay" in str(check_audio_tag):
        auto_loop = True
    elif "loop" in str(check_audio_tag):
        auto_loop = True
    
    music_result = len(check_audio_tag),auto_loop
    return music_result #Für das Schreiben in die Datenbank einfach mit Index zugreifen - [0] fuer das Attribut: Musik ist vorhanden, [1] fuer: Autoplay/Loop Attribut

def write():
    some_engine = create_engine(DB_URI, echo=DEBUG)
    Session = sessionmaker(bind=some_engine)    
    session = Session()

    write_document = Document(font_existing = bad_fonts), 
    font_number = fonts, textanimation = marquee, 
    colour = bad_colors, number_of_gifs = gifs, 
    w3c = w3c_errors, guestbook = gb,
    phrases = bad_phrases, deadlinks = dead_links

    session.add(write_document)
    session.commit()


"""
if __name__ == "__main__":
    # Hier muss ne for-Schleife hin, die alle Dokumente in der DB durchläuft
    #for homepage in datenbank:
    #    quellcode = code aus datenbank
    #    url = url aus datenbank
    with open (quellcode, "r") as html_file:
        html = html_file.read().lower()
        html_wo_comments = re.sub("<!--.*?>", "", html) # war für beispiel2.txt nötig
        soup = BeautifulSoup(html_wo_comments)
        
        bad_fonts = find_bad_fonts()
        bad_colors = find_bad_colors()
        fonts = font_amount()
        gb = find_guestbook()
        bad_phrases = find_phrases()
        dead_links = find_dead_links()
        mmarquee = get_html_textanimation()
        gifs = get_gifs()
        w3c_errors = count_w3c_errors(url)

        write()

"""


# Zum Testen:
"""
print "Schlechte Schriftarten ja/nein: ", find_bad_fonts()
print "Schlechte Farben: ", find_bad_colors()
print "Anzahl Schriftarten: ", font_amount()
print "Guestbook ja/nein:", find_guestbook(html)
print "Schlechte Phrasen: ", find_phrases(html)
print "Tote Links: ", find_dead_links()


print "W3C Fehler: ", count_w3c_errors("http://prosieben.de")
"""
#print "Gif Amount: ", get_gifs()
#print "Marquee: ", get_html_textanimation(html)
#print "Anzahl H-Tags: ", bad_site_structure()
print "Music: ", music()
