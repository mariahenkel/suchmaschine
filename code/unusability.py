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
    bad_structure = 1
    structure_tags = ["h1","h2","h3","h4","h5","h6","header", "nav", "p", "div"] # p muss wahrscheinlich raus, zuviel benutzt
    if len(soup.find_all([x for x in structure_tags]))>10:
        bad_structure = 0
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
    audio = 0
    auto_loop = 0
    tag_content = []
    for tag in soup.find_all(True):
        tag_content.append(tag)
    if any([extension in str(tag_content) for extension in audiofile_endings]):
        audio = 1
        if any([item in str(tag_content) for item in autoplay_loop_strings]):
            auto_loop = 1
            
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
    distorted_images = 1 if len(img_tags) != 0 and float(distorted_counter)/len(img_tags)>0.1 else 0
    #print "Es sind %s von %d Bildern verzerrt" % (distorted_counter,len(img_tags))
    return distorted_images
    
def get_flash(soup):
    flash_endings = [".swf",".fla",".flv",".swc"]
    flash = 0
    tag_content = []
    for tag in soup.find_all(True):
        tag_content.append(tag)
    if any([extension in str(tag_content) for extension in flash_endings]):
        flash = 1
    return flash
    
def get_popups(soup):
    popups=0
    if "window.open(" in str(soup.find_all("script")):
        popups = 1
    return popups
    
def visitor_counter(soup):
    vis_counter = 0
    with open("../data/visitor_counter_provider.txt", "r") as provider: 
        visitor_sites = [line.lower().rstrip("\n") for line in provider]
    if any([site in str(soup.find_all("a")) for site in visitor_sites]):
        vis_counter = 1
    return vis_counter



some_engine = create_engine(DB_URI, echo=DEBUG)
Session = sessionmaker(bind=some_engine)    
session = Session()
websites = session.query(Document.html_document, Document.url).all()

# Daten werden in die DB geschrieben, momentan noch sehr langsam
websites_data = []
"""
for website in websites:
    website_dict = {}
    html = website[0].lower()
    url = website[1]    
    soup = BeautifulSoup(html)
    tags = get_tags(soup)
    website_dict['url'] = url
    website_dict['font_existing'] = find_bad_fonts(tags)
    website_dict['colour'] = find_bad_colors(tags)
    website_dict['font_number'] = font_amount(tags)
    website_dict['textanimation'] = get_html_textanimation(soup)
    website_dict['number_of_gifs'] = get_gifs(tags)
    website_dict['pagestructure'] = bad_structure =  bad_site_structure(soup)
    website_dict['w3c'] = count_w3c_errors(url)
    website_dict['guestbook'] =  find_guestbook(html)
    website_dict['phrases'] = find_phrases(html)
    website_dict['deadlinks'] = find_dead_links(soup)
    website_dict['backgroundmusic'] = music(soup)[0]
    website_dict['musicloop'] = music(soup)[1]
    website_dict['picture_distorted'] = distorted_images(url, soup)
    website_dict['flash'] = get_flash(soup)
    website_dict['popups'] = get_popups(soup)
    website_dict['hitcounter'] = visitor_counter(soup)
    websites_data.append(website_dict)

for website in websites_data:
    for k,v in website.items():
        if k == 'url':
            url = v
        update = session.query(Document).filter(Document.url == url).update({k:v})
    session.commit()
"""
# Zum Testen

# Läuft Datenbank durch, gibt alles aus
for website in websites:
    html = website[0].lower()
    url = website[1]
    soup = BeautifulSoup(html)
    tags = get_tags(soup)
    print url
    print "Schlechte Schriftarten ja/nein: ", find_bad_fonts(tags)
    print "Schlechte Farben: ", find_bad_colors(tags)
    print "Anzahl Schriften: ", font_amount(tags)
    print "Marquee: ", get_html_textanimation(soup)
    print "Gif Amount: ", get_gifs(tags)
    print "Bad Structure: ", bad_site_structure(soup)
    print "W3C Fehler: ", count_w3c_errors(url)
    print "Guestbook ja/nein:", find_guestbook(html)
    print "Schlechte Phrasen: ", find_phrases(html)
    print "Tote Links: ", find_dead_links(soup)
    print "Background music?", music(soup)[0]
    print "Autoloop", music(soup)[1]
    print "Sind Bilder verzerrt?", distorted_images(url, soup)
    print "Flash vorhanden?", get_flash(soup)
    print "Popups? ", get_popups(soup)
    print "Visitor Counter? ", visitor_counter(soup)
    print "------------------------------"



# Zum Testen mit txt Datei, ohne DB:
"""
with open ("../data/beispiel2.txt", "r") as html_file:
    html = html_file.read().lower()
    soup = BeautifulSoup(html)
    tags = get_tags(soup)
   
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
