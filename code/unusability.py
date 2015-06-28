# -*- coding: utf-8 -
import operator
import urllib2
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

from config import DB_URI, DEBUG
from threading import Thread

Base = declarative_base()
queue = Queue.Queue()


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
            bad_fonts = False
        else:
            bad_fonts = True
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
        marquee_counter += 1
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
    bad_structure = True
    structure_tags = [
        "h1", "h2", "h3", "h4", "h5", "h6", "header", "nav", "div"]
    if len(soup.find_all([x for x in structure_tags])) > 15:
        bad_structure = False
    return bad_structure


def get_guestbook(html):
    if "guestbook" in html:
        guestbook = True
    else:
        guestbook = False
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
            r = requests.get(link, allow_redirects=False, timeout=1)
            if not str(r.status_code).startswith("2") and not str(r.status_code).startswith("3"):
                dead_links = 1
                queue.put(dead_links)
        except:
            dead_links = 1
            queue.put(dead_links)
            pass


def threads_links(soup):
    thread_list = []
    dead_links_counter = 0
    threads = 100
    links = []
    for link in soup.find_all('a'):
        if link.get("href"):
            if link.get('href').startswith("http"):
                links.append(link.get('href'))
    if len(links) < threads:
        threads = len(links)
    beg = 0
    if links:
        end = len(links) / threads
        while beg < len(links):
            t = Thread(target=get_dead_links, args=(soup, links[beg:end]))
            beg += len(links) / threads
            end += len(links) / threads
            t.start()
            thread_list.append(t)
    for thread in thread_list:
        thread.join()
    while not queue.empty():
        dead_links_counter += queue.get()
    return dead_links_counter


def get_music(soup):
    audiofile_endings = [".mp3", ".wav", ".wma", ".ogg", ".mid"]
    autoplay_loop_strings = ["autoplay", "loop", ".play("]
    audio = False
    auto_loop = False
    tag_content = []
    for tag in soup.find_all(True):
        tag_content.append(tag)
    if any([extension in str(tag_content) for extension in audiofile_endings]):
        audio = True
        if any([item in str(tag_content) for item in autoplay_loop_strings]):
            auto_loop = True

    return audio, auto_loop


def get_flash(soup):
    flash_endings = [".swf", ".fla", ".flv", ".swc"]
    flash = False
    tag_content = []
    for tag in soup.find_all(True):
        tag_content.append(tag)
    if any([extension in str(tag_content) for extension in flash_endings]):
        flash = True
    return flash


def get_popups(soup):
    popups = False
    if "window.open(" in str(soup.find_all("script")):
        popups = True
    return popups


def get_visitor_counter(soup):
    vis_counter = False
    with open("../data/visitor_counter_provider.txt", "r") as provider:
        visitor_sites = [line.lower().rstrip("\n") for line in provider]
    if any([site in str(soup.find_all("a")) for site in visitor_sites]):
        vis_counter = True
    return vis_counter


def get_distorted_images(url, soup, img_tags):
    distorted_image = 0
    for tag in img_tags:
        if "width" in str(img_tags) and "height" in str(img_tags):
            try:
                im = Image.open(urllib2.urlopen(url + tag.get("src")))
            except IOError:
                pass
            except TypeError:
                pass
            except urllib2.HTTPError:
                pass
            # hier kommt ab und zu InvalidURL, aber der nimmt den
            # ExceptionType nicht an..
            except:
                pass
            else:
                try:
                    if round(float(im.size[0]) / im.size[1], 2) != round(float(tag.get("width")) / float(tag.get("height")), 2):
                        distorted_image = 1
                        queue.put(distorted_image)
                except ZeroDivisionError:
                    pass


def threads_images(soup, url):
    thread_list = []
    amount_distorted_images = 0
    threads = 100
    img_tags = soup.find_all("img")
    if len(img_tags) < threads:
        threads = len(img_tags)
    beg = 0
    if img_tags:
        end = len(img_tags) / threads
        while beg < len(img_tags):
            t = Thread(
                target=get_distorted_images, args=(url, soup, img_tags[beg:end]))
            beg += len(img_tags) / threads
            end += len(img_tags) / threads
            t.start()
            thread_list.append(t)
    for thread in thread_list:
        thread.join()
    while not queue.empty():
        amount_distorted_images += queue.get()
    distorted_images = True if len(img_tags) != 0 and float(
        amount_distorted_images) / len(img_tags) > 0.05 else False
    return distorted_images


def get_w3c(url):
    w3c_link = "https://validator.w3.org/check?uri="
    check_url = urllib2.urlopen(w3c_link + url)
    if str(check_url.getcode()).startswith("2") or str(check_url.getcode()).startswith("3"):
        content = check_url.read()
        soup = BeautifulSoup(content)
        errors = soup.find("h3", class_="invalid")
        if errors is not None:
            errors_extracted = re.findall(r'\d+', str(errors.get_text()))
            errors_extracted = [int(x) for x in errors_extracted]
        else:
            errors_extracted = [0]
        return errors_extracted[0]
    else:
        pass


def get_factor(bad_fonts, bad_colors, fonts, marquee, gifs, bad_structure,
               gb, phrases, dead_links, audio, audio_loop, images, flash, popups, counter, w3):
    bad_fonts_max = 8
    bad_colors_max = 8
    font_amount_max = 5
    marquee_max = 7
    gifs_max = 10
    bad_structure_max = 3
    guestbook_max = 3
    phrases_max = 4
    dead_links_max = 7
    audio_max = 10
    audio_loop_max = 6
    images_max = 8
    flash_max = 6
    popups_max = 7
    counter_max = 3
    w3c_max = 5

    bad_fonts_value = bad_fonts_max if bad_fonts == True else 0
    bad_colors_value = bad_colors_max if bad_colors > bad_colors_max else bad_colors
    font_amount_value = font_amount_max if fonts > font_amount_max else fonts
    marquee_value = marquee_max if marquee * \
        0.7 > marquee_max else marquee * 0.7
    gif_value = gifs_max if float(
        gifs) / gifs_max > gifs_max else float(gifs) / gifs_max
    bad_structure_value = bad_structure_max if bad_structure == True else 0
    guestbook_value = guestbook_max if gb == True else 0
    phrases_value = phrases_max if phrases * \
        2 > phrases_max else phrases * 2
    dead_links_value = dead_links_max if dead_links * \
        0.7 > dead_links_max else dead_links * 0.7
    audio_value = audio_max if audio == True else 0
    audio_loop_value = audio_loop_max if audio_loop == True else 0
    images_value = images_max if images == True else 0
    flash_value = flash_max if flash == True else 0
    popups_value = popups_max if popups == True else 0
    counter_value = counter_max if counter == True else 0
    w3c_value = w3c_max if float(w3) / 20 > w3c_max else float(w3) / 20
    score = bad_fonts_value + bad_colors_value + font_amount_value + marquee_value + gif_value + bad_structure_value + guestbook_value + \
        phrases_value + dead_links_value + audio_value + audio_loop_value + \
        images_value + flash_value + popups_value + counter_value
    return score


some_engine = create_engine(DB_URI, echo=DEBUG)
Session = sessionmaker(bind=some_engine)
session = Session()
websites = session.query(
    Document.html_document, Document.url, Document.overall_score).yield_per(100)
num_of_websites = session.query(Document).count()


def overall(websites, website_dict):
    for site in websites:
        if site[2] != None:
            pass
        else:
            html = site[0]
            url = site[1]
            soup = BeautifulSoup(html)
            tags = get_tags(soup)
            bad_fonts = get_bad_fonts(tags)
            bad_colors = get_bad_colors(tags)
            fonts = get_font_amount(tags)
            marquee = get_html_textanimation(soup)
            gifs = get_gifs(tags)
            bad_structure = get_site_structure(soup)
            gb = get_guestbook(html)
            phrases = get_phrases(html)
            dead_links = threads_links(soup)
            audio = get_music(soup)[0]
            audio_loop = get_music(soup)[1]
            images = threads_images(soup, url)
            flash = get_flash(soup)
            popups = get_popups(soup)
            counter = get_visitor_counter(soup)
            w3 = get_w3c(url)
            unusability = get_factor(bad_fonts, bad_colors, fonts, marquee,
                                     gifs, bad_structure, gb, phrases, dead_links, audio, audio_loop,
                                     images, flash, popups, counter, w3)
            website_dict['url'] = url
            website_dict['font_existing'] = bad_fonts
            website_dict['colour'] = bad_colors
            website_dict['font_number'] = fonts
            website_dict['textanimation'] = marquee
            website_dict['number_of_gifs'] = gifs
            website_dict['pagestructure'] = bad_structure
            website_dict['guestbook'] = gb
            website_dict['phrases'] = phrases
            website_dict['deadlinks'] = dead_links
            website_dict['backgroundmusic'] = audio
            website_dict['musicloop'] = audio_loop
            website_dict['picture_distorted'] = images
            website_dict['flash'] = flash
            website_dict['popups'] = popups
            website_dict['hitcounter'] = counter
            website_dict['w3c'] = w3
            website_dict['overall_score'] = unusability
            websites_data.append(website_dict)


def get_unusability(websites):
    thread_list = []
    threads = 99
    beg = 0
    if num_of_websites < threads:
        threads = num_of_websites
    end = num_of_websites / threads
    while beg < num_of_websites:
        website_dict = {}
        t = Thread(target=overall, args=([websites[beg:end], website_dict]))

        beg += num_of_websites / threads
        end += num_of_websites / threads
        t.start()
        thread_list.append(t)

    for thread in thread_list:
        thread.join()
    return websites_data

websites_data = []

beg, end = -50, 0
while end < num_of_websites:
    beg += 50
    end += 50
    if end > num_of_websites:
        end = num_of_websites
    websites_data = get_unusability(websites[beg:end])
    for website in websites_data:
        for x in website.items():
            update = session.query(Document).filter(Document.url == website.items()[
                5][1]).update({k: v for k, v in website.items()})
            session.commit()
    print "Seite %s bis %s in die DB geschrieben" % (beg + 1, end)
    websites_data = []
