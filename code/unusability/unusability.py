# -*- coding: utf-8 -
import urllib
import re
from bs4 import BeautifulSoup
import requests


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
    return bad_fonts

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

def get_html_textanimation(html_page):
    marquee_amount = re.findall("<marquee(.)*</marquee>", str(html_page))  
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

def get_gifs (html_page):
    gif_amount = re.findall("<(.)*\.gif.*?>", str(html_page))
    return len(gif_amount)

        
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


# Sucht jetzt einfach im kompletten Code, aber dass guestbook einfach so in nem anderen Kontext vorkommt eher unwahrscheinlich?
def find_guestbook(html):
    if "guestbook" in html:
        guestbook = 1
    else:
        guestbook = 0
    return guestbook


def find_phrases(html):
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


print "Schlechte Schriftarten ja/nein: ", find_bad_fonts()
print "Schlechte Farben: ", find_bad_colors()
print "Anzahl Schriftarten: ", font_amount()
print "Guestbook ja/nein:", find_guestbook(html)
print "Schlechte Phrasen: ", find_phrases(html)
print "Tote Links: ", find_dead_links()
print "Marquee: ", get_html_textanimation(html)
print "Gif Amount: ", get_gifs(html)
print "W3C Fehler: ", count_w3c_errors("http://prosieben.de")



