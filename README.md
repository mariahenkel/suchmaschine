# suchmaschine
Wir programmieren eine "Unusability"-Suchmaschine. :)


General Usage
-------------
1. Switch to the `/code` subdirectory
2. Install all required packages using pip: `pip install -r requirements.txt`
3. Create a configfile named `config.py` and set settings accordingly to your needs. An example can be found in the same folder: `defaultconfig.py`
4. Create the database by running `python models.py`


Crawler Usage
-------------
1. Run `scrapy crawl basic_spider`


Unusability Usage
-----------------
1. Run `python unusability.py`


Indexer
-------
1. Run `python indexer.py`

Webinterface (The interface for the searchengine itself)
------------
1. Run `python smonkyinterface.py`


Note
----
All components (Crawler, Unusability, Indexer and Webinterface) have to be run in that order for the project to work correctly! **Wait for the Crawler to finish before you start anything else!**
