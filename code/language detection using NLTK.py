import nltk
import urllib2
#http://pymotw.com/2/urllib2/
#http://www.pythonforbeginners.com/python-on-the-web/how-to-use-urllib2-in-python/
import re
import unicodedata

ENGLISH_STOPWORDS = set(nltk.corpus.stopwords.words('english'))
NON_ENGLISH_STOPWORDS = set(nltk.corpus.stopwords.words()) - ENGLISH_STOPWORDS

STOPWORDS_DICT = {lang: set(nltk.corpus.stopwords.words(lang)) for lang in nltk.corpus.stopwords.fileids()}

def get_language(text):
    words = set(nltk.wordpunct_tokenize(text.lower()))
    return max(((lang, len(words & stopwords)) for lang, stopwords in STOPWORDS_DICT.items()), key=lambda x: x[1])[0]


def checkEnglish(text):
    if text is None:
        return 0
    else:
        text = unicode(text, errors='replace')
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')
        text = text.lower()
    words = set(nltk.wordpunct_tokenize(text))
    if len(words & ENGLISH_STOPWORDS) > len(words & NON_ENGLISH_STOPWORDS):
        return 1
    else:
        return 0


def getPage(url):
    if not url.startswith("http://"):
        url = "http://" + url
    print "Checking the site ", url
    req = urllib2.Request(url)
    try:
        response = urllib2.urlopen(req)
        rstPage = response.read()
    except urllib2.HTTPError, e:
        rstPage = None
    except urllib2.URLError, e:
        rstPage = None
    except Exception, e:
        rstPage = None
    return rstPage


def getPtag(webPage):
    if webPage is None:
        return None
    else:
        rst = re.search(r'<p\W*(.+)\W*</p>', webPage)
        if rst is not None:
            return rst.group(1)
        else:
            return rst


def getDescription(webPage):
    if webPage is None:
        return None
    else:
        des = re.search(r'<meta\s+.+\"[Dd]escription\"\s+content=\"(.+)\"\s*/*>', webPage)
        if des is not None:
            return des.group(1)
        else:
            return des


def checking(url):
    pageText = getPage(url)
    if pageText is not None:
        if checkEnglish(getDescription(pageText)) == 1:
            return '1'
        elif checkEnglish(getPtag(pageText)) == 1:
            return '1'
        elif checkEnglish(pageText) == 1:
            return '1'
        else:
            return '0'
    else:
        return 'NULL'

if __name__ == "__main__":
    f = open('sample_domain_list.txt').readlines()
    s = open('newestResult.txt', "w")
    for line in f[:20]:
        url = line.split(',')[1][1:-1]
        check = checking(url)
        s.write(url + ',' + check)
        s.write('\n')
        print check

#    f.close()
    s.close()
