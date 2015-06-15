# -*- coding: utf-8 -*-
from os import path, pardir

# enable debug mode (verbose database, detailed logs etc.)
DEBUG = False

# General settings
BOT_NAME = "basic_crawler"
# SPIDER_MODULES = ["basic_crawler.spiders"]
# NEWSPIDER_MODULE = "basic_crawler.spiders"
SPIDER_MODULES = ["basic_crawler.spiders.basic_spider_unusability"]
NEWSPIDER_MODULE = "basic_crawler.spiders.basic_spider_unusability"
ITEM_PIPELINES = {"basic_crawler.pipelines.InvertaPipeline": 1}

# Settings to speed things up a bit (also see
# http://doc.scrapy.org/en/0.24/topics/broad-crawls.html)
AUTOTHROTTLE_ENABLED = True
REDIRECT_MAX_TIMES = 3
CONCURRENT_REQUESTS = 100
RETRY_ENABLED = False
DOWNLOAD_TIMEOUT = 30
DEPTH_LIMIT = 1
COOKIES_ENABLED = False

AJAXCRAWL_ENABLED = True
# Less verbose output and use of a logfile
LOG_LEVEL = "INFO"
LOG_FILE = path.join(pardir, "logs", "basic_crawler.log")

# database address
DB_URI = path.join("sqlite:///", pardir, "data", "search.db")

# URL to alexa top1m dataset
TOP1M_PATH = "http://s3.amazonaws.com/alexa-static/top-1m.csv.zip"
# Limit the number of websites to crawl from the alexa dataset
TOP1M_LIMIT = 100000

# path to textfile with additional websites
TXT_PATH = path.join(pardir, "data", "uglysites.txt")

# Generation of secret keys according to the instructions from the Flask documentary.
# http://flask.pocoo.org/docs/quickstart/#sessions
SECRET_KEY = '\xca%6\xa4}\xb2K\xd4L\x94{\x08\xf5 \x06\xeaD\x89\xd2\xc9\x10\xcb\xcd4'

#Is already included
"""# Information about the database
DB_URI = 'sqlite:///search.db'"""

