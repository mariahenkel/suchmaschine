# -*- coding: utf-8 -
import operator
import urllib
import re
import Queue
import time
from bs4 import BeautifulSoup
import requests
from models import Document
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from PIL import Image
import urllib
from defaultconfig import DB_URI, DEBUG
from threading import Thread

Base = declarative_base()
queue = Queue.Queue()
all_urls = []

def get_tags(soup):
    tag_attrs_lists = [] 
    tag_attrs = [] 
    for tag in soup.find_all(True):
        tag_attrs_lists.append(tag.attrs.values())
    for list in tag_attrs_lists:
        for element in list:
            tag_attrs.append(element) 
    return tag_attrs

def get_bad_fonts(tags):       
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
    
def get_font_amount(tags):
    with open("../data/fonts.txt", "r") as fonts_file: 
        fonts_list = [line.lower().rstrip("\n") for line in fonts_file]      
        fonts_counter = 0
        for font in fonts_list:
            if any(font in s for s in tags):
                fonts_counter += 1
    return fonts_counter
    
def get_html_textanimation(soup):
    marquee_counter = 0
    for tag in soup.find_all("marquee"):
        marquee_counter +=1
    return marquee_counter

def get_bad_colors(tags):    
    with open("../data/bad_colors.txt", "r") as colors_file:
        bad_colors_list = [line.rstrip("\n") for line in colors_file]      
        color_counter = 0
        for color in bad_colors_list:
            if any(color in s for s in tags):
                color_counter += 1
    return color_counter

def get_gifs(tags):
    return str(tags).count(".gif")
    
def get_site_structure(soup):
    bad_structure = 1
    structure_tags = ["h1","h2","h3","h4","h5","h6","header", "nav", "p", "div"] # p muss wahrscheinlich raus, zuviel benutzt
    if len(soup.find_all([x for x in structure_tags]))>10:
        bad_structure = 0
    return bad_structure

def get_guestbook(html):
    if "guestbook" in html:
        guestbook = 1
    else:
        guestbook = 0
    return guestbook

def get_phrases(html):
    with open("../data/phrases.txt", "rb") as phrases_file:
        phrases_list = [line.rstrip("\n\r") for line in phrases_file]
    phrases_counter = 0 
    for phrase in phrases_list:
        if phrase in html:
            phrases_counter += 1
    return phrases_counter

def get_dead_links(soup, links):
    dead_links = 0
    for index, link in enumerate(links):
        try:
            r = requests.get(link,allow_redirects=False)
            if not str(r.status_code).startswith("2") and not str(r.status_code).startswith("3"):
                dead_links = 1   
                queue.put(dead_links)
        except requests.exceptions.ConnectionError:
            dead_links = 1
            queue.put(dead_links)
        except requests.exceptions.ChunkedEncodingError: 
            pass
#der macht jetzt weiter aber dann kommt folgender Fehler: error: [Errno 10054] Eine vorhandene Verbindung wurde vom Remotehost geschlossen
#programm bricht nicht ab aber macht nicht weiter
        
def threads_links(soup):
    thread_list = []
    dead_links_counter = 0
    threads = 100
    links = []
    for link in soup.find_all('a'):
        if link.get("href"):
            if link.get('href').startswith("http"):
                links.append(link.get('href'))
    if len(links)<threads:   
        threads = len(links)
    beg = 0  
    if links:
        end = len(links)/threads
        while beg < len(links):
            t = Thread(target=get_dead_links, args=(soup,links[beg:end]))
            beg +=len(links)/threads
            end += len(links)/threads          
            t.start()
            thread_list.append(t)  
    for thread in thread_list:
        thread.join()    
    while not queue.empty():
        dead_links_counter += queue.get()
    return dead_links_counter

def get_music(soup):
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
    
def get_visitor_counter(soup):
    vis_counter = 0
    with open("../data/visitor_counter_provider.txt", "r") as provider: 
        visitor_sites = [line.lower().rstrip("\n") for line in provider]
    if any([site in str(soup.find_all("a")) for site in visitor_sites]):
        vis_counter = 1
    return vis_counter

def get_distorted_images(url, soup,img_tags):
    distorted_image = 0
    for tag in img_tags:
        if "width" in str(img_tags) and "height" in str(img_tags):
            try:
                im=Image.open(urllib.urlopen(url+tag.get("src")))
            except IOError:
                pass
                #print "Error opening image...",url+tag.get("src")
            except TypeError:
                pass
            else:   
                try:
                    if round(float(im.size[0])/im.size[1],2) != round(float(tag.get("width"))/float(tag.get("height")),2):
                        distorted_image = 1 
                        queue.put( distorted_image)
                except ZeroDivisionError:
                    pass
    
def threads_images(soup):
    thread_list = []
    amount_distorted_images = 0
    threads = 100
    img_tags = soup.find_all("img")
    if len(img_tags)<threads:   
        threads = len(img_tags)
    beg = 0
    if img_tags:
        end = len(img_tags)/threads
        while beg < len(img_tags):
            t = Thread(target=get_distorted_images, args=(url,soup,img_tags[beg:end]))
            beg +=len(img_tags)/threads
            end += len(img_tags)/threads
            t.start()
            thread_list.append(t)
    for thread in thread_list:
        thread.join()
    while not queue.empty():
        amount_distorted_images += queue.get()
    distorted_images = 1 if len(img_tags) != 0 and float(amount_distorted_images)/len(img_tags)>0.01 else 0
    return distorted_images
     
def get_w3c_errors(all_urls,w3c_errors):
    w3c_link = "https://validator.w3.org/check?uri="
    for url in all_urls:
        
        check_url = urllib.urlopen(w3c_link+url)
        content = check_url.read()
        soup = BeautifulSoup(content)
        errors= soup.find("h3" ,class_ = "invalid")
        if errors is not None:
            errors_extracted = re.findall(r'\d+', str(errors.get_text()))
            errors_extracted = [int(x) for x in errors_extracted]
        else:
            errors_extracted = [0]
        w3c_errors[url] = errors_extracted[0]

def get_w3c(url):
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
        
        
def threads_w3c(all_urls):
    thread_list = []
    threads = 100
    beg = 0
    w3c_errors = {}
    if len(all_urls)<threads:   
        threads = len(all_urls)
    end = len(all_urls)/threads
    if all_urls:
        while beg < len(all_urls):
            t = Thread(target=get_w3c_errors, args=([all_urls[beg:end],w3c_errors]))
            beg +=len(all_urls)/threads
            end += len(all_urls)/threads
            t.start()
            thread_list.append(t)
    for thread in thread_list:
        thread.join()
    return sorted(w3c_errors.items(), key=operator.itemgetter(0))
 

some_engine = create_engine(DB_URI, echo=DEBUG)
Session = sessionmaker(bind=some_engine)    
session = Session()
websites = session.query(Document.html_document, Document.url).all()
websites_data = []


#Zeilen 272-328 = Alle Funktion + w3c mit Threads
#########################################################################################################
"""
for url in websites:
    all_urls.append(url[1])
    
overall_w3c_errors_of_all_sites =  threads_w3c(all_urls)

for website,w3c in zip(sorted(websites,key=operator.itemgetter(1)),overall_w3c_errors_of_all_sites):
    website_dict = {}
    html = website[0].lower()
    url = website[1]
    soup = BeautifulSoup(html)
    all_urls.append(url)
    tags = get_tags(soup)
    bad_fonts = get_bad_fonts(tags)
    bad_colors = get_bad_colors(tags)
    fonts = get_font_amount(tags)
    marquee = get_html_textanimation(soup)
    gifs = get_gifs(tags)
    bad_structure =  get_site_structure(soup)
    gb =  get_guestbook(html)
    phrases = get_phrases(html)
    dead_links = threads_links(soup)
    audio = get_music(soup)[0]
    audio_loop = get_music(soup)[1]
    images = threads_images(soup)
    flash = get_flash(soup)
    popups = get_popups(soup)
    counter = get_visitor_counter(soup)
    
    
    factor = bad_fonts*4+bad_colors+fonts+gifs*0.5+marquee*2 
    +bad_structure*2+gb*2+phrases+dead_links+audio*7 
    +audio_loop*3+images*3+flash*2+popups*3+counter*2+w3c[1]
    
    
    website_dict['url'] = url
    website_dict['font_existing'] = bad_fonts
    website_dict['colour'] = bad_colors
    website_dict['font_number'] = fonts
    website_dict['textanimation'] = marquee
    website_dict['number_of_gifs'] = gifs
    website_dict['pagestructure'] = bad_structure
    website_dict['guestbook'] =  gb
    website_dict['phrases'] = phrases
    website_dict['deadlinks'] = dead_links
    website_dict['backgroundmusic'] = audio
    website_dict['musicloop'] = audio_loop
    website_dict['picture_distorted'] = images
    website_dict['flash'] = flash
    website_dict['popups'] = popups
    website_dict['hitcounter'] = counter
    website_dict['overall_score'] = factor
    website_dict['w3c'] = w3c[1]
    websites_data.append(website_dict)
    print "rdy"

"""
##########################################################################################################


#333-390 = Alles, aber w3c ohne Threads
x = 0
for website in websites:
    website_dict = {}
    html = website[0].lower()
    url = website[1]
    soup = BeautifulSoup(html)
    all_urls.append(url)
    tags = get_tags(soup)
    bad_fonts = get_bad_fonts(tags)
    bad_colors = get_bad_colors(tags)
    fonts = get_font_amount(tags)
    marquee = get_html_textanimation(soup)
    gifs = get_gifs(tags)
    bad_structure =  get_site_structure(soup)
    gb =  get_guestbook(html)
    phrases = get_phrases(html)
    dead_links = threads_links(soup)
    audio = get_music(soup)[0]
    audio_loop = get_music(soup)[1]
    images = threads_images(soup)
    flash = get_flash(soup)
    popups = get_popups(soup)
    counter = get_visitor_counter(soup)
    w3 = get_w3c(url)
    
    #factor = bad_fonts*4+bad_colors+fonts+gifs*0.5+marquee*2 
    #+bad_structure*2+gb*2+phrases+dead_links+audio*7 
    #+audio_loop*3+images*3+flash*2+popups*3+counter*2+w3c[1]
    
    factor = bad_fonts*4+bad_colors+fonts+gifs*0.5+marquee*2 
    +bad_structure*2+gb*2+phrases+dead_links+audio*7 
    +audio_loop*3+images*3+flash*2+popups*3+counter*2+w3
    
    website_dict['url'] = url
    website_dict['font_existing'] = bad_fonts
    website_dict['colour'] = bad_colors
    website_dict['font_number'] = fonts
    website_dict['textanimation'] = marquee
    website_dict['number_of_gifs'] = gifs
    website_dict['pagestructure'] = bad_structure
    website_dict['guestbook'] =  gb
    website_dict['phrases'] = phrases
    website_dict['deadlinks'] = dead_links
    website_dict['backgroundmusic'] = audio
    website_dict['musicloop'] = audio_loop
    website_dict['picture_distorted'] = images
    website_dict['flash'] = flash
    website_dict['popups'] = popups
    website_dict['hitcounter'] = counter
    website_dict['overall_score'] = factor
    #website_dict['w3c'] = w3c[1]
    website_dict['w3c'] = w3
    websites_data.append(website_dict)
    x+=1
    print x

for x in websites_data:
    print x

##########################################################################################################
for website in websites_data:
    for x in website.items():
  
        update = session.query(Document).filter(Document.url == website.items()[5][1]).update({k:v for k,v in website.items()})
        session.commit()
    print "rdy"


# Zum Testen
# Läuft Datenbank durch, gibt alles aus
"""
for website in websites:
    html = website[0].lower()
    url = website[1]
    all_urls.append(url)
    soup = BeautifulSoup(html)
    tags = get_tags(soup)
   
    #print url
    #print "Schlechte Schriftarten ja/nein: ", get_bad_fonts(tags)
    #print "Schlechte Farben: ", get_bad_colors(tags)
    #print "Anzahl Schriften: ", font_amount(tags)
    #print "Marquee: ", get_html_textanimation(soup)
    #print "Gif Amount: ", get_gifs(tags)
    #print "Bad Structure: ", bad_site_structure(soup)
    #print "W3C Fehler: ", count_w3c_errors(url)
    #print "Guestbook ja/nein:", get_guestbook(html)
    #print "Schlechte Phrasen: ", get_phrases(html)
    
    #print "Background music?", music(soup)[0]
    #print "Autoloop", music(soup)[1]
    #print "Sind Bilder verzerrt?", threads_images(soup)
    #print "Flash vorhanden?", get_flash(soup)
    #print "Popups? ", get_popups(soup)
    #print "Visitor Counter? ", visitor_counter(soup)
    print "------------------------------"


"""

