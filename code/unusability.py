# -*- coding: utf-8 -
import urllib
import re
from bs4 import BeautifulSoup
import requests
from models import Document
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from PIL import Image
import urllib
from config import DB_URI, DEBUG

Base = declarative_base()

def get_tags(soup):
    tag_attrs_lists = [] 
    tag_attrs = [] 
    for tag in soup.find_all(True):
        tag_attrs_lists.append(tag.attrs.values())
    for list in tag_attrs_lists:
        for element in list:
            tag_attrs.append(element) 
    return tag_attrs


def find_bad_fonts(tags):       
    with open("../data/bad_fonts.txt", "r") as fonts_file:
        bad_fonts_list = [line.rstrip("\n") for line in fonts_file]      
        bad_fonts_counter = 0
        for font in bad_fonts_list:
            if any(font in s for s in tags):
                bad_fonts_counter += 1
        if bad_fonts_counter == 0:
            bad_fonts = 0
        else:
            bad_fonts = 1
    return bad_fonts
    

def font_amount(tags):
    with open("../data/fonts.txt", "r") as fonts_file: # Liste von Wikipedia - wäre auch möglich, alle font tags auszulesen und auszuwerten
        fonts_list = [line.lower().rstrip("\n") for line in fonts_file]      
        fonts_counter = 0
        for font in fonts_list:
            if any(font in s for s in tags):
                fonts_counter += 1
    return fonts_counter
    

def get_html_textanimation(soup):
    marquee_amount = 0
    for tag in soup.find_all("marquee"):
        marquee_amount +=1
    return marquee_amount


def find_bad_colors(tags):    
    with open("../data/bad_colors.txt", "r") as colors_file:
        bad_colors_list = [line.rstrip("\n") for line in colors_file]      
        color_counter = 0
        for color in bad_colors_list:
            if any(color in s for s in tags):
                color_counter += 1
    return color_counter

def get_gifs(tags):
    return str(tags).count(".gif")
    
def bad_site_structure(soup):
    bad_structure = True
    structure_tags = ["h1","h2","h3","h4","h5","h6","header", "nav", "p", "div"] # p muss wahrscheinlich raus, zuviel benutzt
    if len(soup.find_all([x for x in structure_tags]))>10:
        bad_structure = False
    return bad_structure
    
def count_w3c_errors (url):
    w3c_link = "https://validator.w3.org/check?uri="
    check_url = urllib.urlopen(w3c_link+url)
    content = check_url.read()
    soup = BeautifulSoup(content)
    errors= soup.find("h3" ,class_ = "invalid")
    if errors is not None:
        errors_extracted = re.findall(r'\d+', str(errors.get_text()))
        errors_extracted = [int(x) for x in errors_extracted]
    else:
        errors_extracted = [0]
    return errors_extracted[0]

def find_guestbook(html):
    if "guestbook" in html:
        guestbook = 1
    else:
        guestbook = 0
    return guestbook


def find_phrases(html):
    with open("../data/phrases.txt", "rb") as phrases_file:
        phrases_list = [line.rstrip("\n\r") for line in phrases_file]
    phrases_counter = 0 
    for phrase in phrases_list:
        if phrase in html:
            phrases_counter += 1
    return phrases_counter

def find_dead_links(soup):
    links = []
    for link in soup.find_all('a'):
        if link.get("href"):
            if link.get('href').startswith("http"):
                links.append(link.get('href')) 
    dead_links = 0
    for index, link in enumerate(links):
        try:
            r = requests.get(link)
            if not str(r.status_code).startswith("2") and not str(r.status_code).startswith("3"):
                dead_links += 1   
        except requests.exceptions.ConnectionError:
            dead_links +=1
    return dead_links
    
def music(soup):
    audiofile_endings = [".mp3",".wav",".wma",".ogg",".mid"]
    autoplay_loop_strings = ["autoplay","loop",".play("]
    audio = False
    auto_loop = False
    tag_content = []
    for tag in soup.find_all(True):
        tag_content.append(tag)
    if any([extension in str(tag_content) for extension in audiofile_endings]):
        audio = True
        if any([item in str(tag_content) for item in autoplay_loop_strings]):
            auto_loop = True
            
    return audio,auto_loop
    
def distorted_images(url, soup):
    distorted_counter = 0
    img_tags =  soup.find_all("img")
    for tag in img_tags:
        if "width" in str(tag) and "height" in str(tag):
            try:
                im=Image.open(urllib.urlopen(url+tag.get("src")))
            except IOError:
                print "Error opening image..."
            else:   
                try:
                    if round(float(im.size[0])/im.size[1],2) != round(float(tag.get("width"))/float(tag.get("height")),2):
                        distorted_counter += 1
                except ZeroDivisionError:
                    pass
    distorted_images = True if len(img_tags) != 0 and float(distorted_counter)/len(img_tags)>0.1 else False
    print "Es sind %s von %d Bildern verzerrt" % (distorted_counter,len(img_tags))
    return distorted_images
    
def get_flash(soup):
    flash_endings = [".swf",".fla",".flv",".swc"]
    flash = False
    tag_content = []
    for tag in soup.find_all(True):
        tag_content.append(tag)
    if any([extension in str(tag_content) for extension in flash_endings]):
        flash = True
    return flash
    
def get_popups(soup):
    popups=False
    if "window.open(" in str(soup.find_all("script")):
        popups = True
    return popups
    
def visitor_counter(soup):
    vis_counter = False
    with open("../data/visitor_counter_provider.txt", "r") as provider: 
        visitor_sites = [line.lower().rstrip("\n") for line in provider]
    if any([site in str(soup.find_all("a")) for site in visitor_sites]):
        vis_counter = True
    return vis_counter



some_engine = create_engine(DB_URI, echo=DEBUG)
Session = sessionmaker(bind=some_engine)    
session = Session()
websites = session.query(Document.html_document, Document.url).all()

"""
# Läuft Datenbank durch, speichert alles in Variablen (muss dann noch in die DB)
for website in websites:
    html = website[0].lower()
    url = website[1]
    soup = BeautifulSoup(html)
    tags = get_tags(soup)
    bad_fonts = find_bad_fonts(tags)
    bad_colors = find_bad_colors(tags)
    fonts = font_amount(tags)
    #marquee = get_html_textanimation(soup)
    gifs = get_gifs(tags)
    bad_structure =  bad_site_structure(soup)
    #w3c = count_w3c_errors(url)
    gb =  find_guestbook(html)
    phrases = find_phrases(html)
    dead_links = find_dead_links(soup)
    audio = music(soup)[0]
    auto_loop = music(soup)[1]
    #images = distorted_images(url, soup)
    flash = get_flash(soup)
    popups = get_popups(soup)
    counter = visitor_counter(soup)

"""


# Läuft Datenbank durch, gibt alles aus

for website in websites:
    html = website[0].lower()
    url = website[1]
    soup = BeautifulSoup(html)
    tags = get_tags(soup)
    print url
    print "Schlechte Schriftarten ja/nein: ", find_bad_fonts(tags)
    print "Schlechte Farben: ", find_bad_colors(tags)
    fonts = font_amount(tags)
    print "Marquee: ", get_html_textanimation(soup)
    print "Gif Amount: ", get_gifs(tags)
    print "Bad Structure: ", bad_site_structure(soup)
    print "W3C Fehler: ", count_w3c_errors(url)
    print "Guestbook ja/nein:", find_guestbook(html)
    print "Schlechte Phrasen: ", find_phrases(html)
    #print "Tote Links: ", find_dead_links(soup)
    print "Background music?", music(soup)[0]
    print "Autoloop", music(soup)[1]
    print "Sind Bilder verzerrt?", distorted_images(url, soup)
    print "Flash vorhanden?", get_flash(soup)
    print "Popups? ", get_popups(soup)
    print "Visitor Counter? ", visitor_counter(soup)
    print "------------------------------"

# Zum Testen mit txt Datei, ohne DB:



with open ("../data/beispiel2.txt", "r") as html_file:
    html = html_file.read().lower()
    soup = BeautifulSoup(html)
    tags = get_tags(soup)
    
"""    
url = "http://www.theworldsworstwebsiteever.com/"
print "Sind Bilder verzerrt?", distorted_images(url, soup)
print "Schlechte Schriftarten ja/nein: ", find_bad_fonts(tags)
print "Schlechte Farben: ", find_bad_colors(tags)
print "Anzahl Schriftarten: ", font_amount(tags)
print "Marquee: ", get_html_textanimation(soup)
print "Gif Amount: ", get_gifs(tags)
print "Bad Structure: ", bad_site_structure(soup)
print "W3C Fehler: ", count_w3c_errors(url)
print "Guestbook ja/nein:", find_guestbook(html)
print "Schlechte Phrasen: ", find_phrases(html)
print "Tote Links: ", find_dead_links(soup)
print "Background music?", music(soup)[0]
print "Musik Autoloop", music(soup)[1]

print "Flash vorhanden?", get_flash(soup)
print "Popups? ", get_popups(soup)
print "Visitor Counter? ", visitor_counter(soup)

"""
