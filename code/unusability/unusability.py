# -*- coding: utf-8 -
import urllib
import re
from bs4 import BeautifulSoup


with open ("beispiel2.txt", "r") as html_file:
    html = html_file.read().lower()

##########
# Fonts  #
########## 

def find_bad_fonts(html):
    with open ("bad_fonts.txt", "r") as fonts_file:
        bad_fonts_list = [line.rstrip("\n") for line in fonts_file]
    bad_fonts_counter = 0
    for font in bad_fonts_list:
        font_pattern = r"<(.)*font(.*)"+font+"(.)*>"
        result = re.findall(font_pattern, html)
        bad_fonts_counter += len(result)
    if bad_fonts_counter == 0:
        bad_fonts = 0
    else:
        bad_fonts = 1
    return bad_fonts

# Noch nicht fertig, zählt alle Schriftartenänderungen (also auch doppelte)
def font_amount(html):
    fonts = []
    font_pattern = r"<font.* face=['\"]?.*?['\"]?.*?>"
    result = re.findall(font_pattern, html)
    font_counter = 0
    for font in result:
        font_counter += 1
    return font_counter

def get_html_textanimation(html_page):
    marquee_amount = re.findall("<marquee(.)*</marquee>", str(html_page))  
    return len(marquee_amount)

##########
# Colors #
########## 

# Aktuelles Problem: Sucht auch im Text
def find_bad_colors(html):
    with open("bad_colors.txt", "r") as colors_file:
        bad_colors_list = [line.rstrip("\n") for line in colors_file]
    color_counter = 0
    for color in bad_colors_list:
        if color in html:
            color_counter += 1
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


print "Bad Fonts (yes/no): ", find_bad_fonts(html)
print "Bad Colors: ", find_bad_colors(html)
print "Font Amount: ", font_amount(html)
print "Marquee: ", get_html_textanimation(html)
print "Gif Amount: ", get_gifs(html)
print "W3C Fehler: ", count_w3c_errors("http://prosieben.de")



