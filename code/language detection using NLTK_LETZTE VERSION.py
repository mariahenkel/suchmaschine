from nltk.corpus import stopwords   # stopwords to detect language
from nltk import wordpunct_tokenize # function to split up our words
from sys import stdin               # how else should we get our input :)
import re			# import regex 

def get_language_likelihood(website):
    """Return a dictionary of languages and their likelihood of being the 
    natural language of the input text
    """
    """ expression will filter everything between <script></script> tags and remove the tags as well """
    regex = re.compile(r"<script[^>]*>(.*?)</script>", re.IGNORECASE|re.DOTALL)
    website = regex.sub(website, "")
 
   """ tokenize lower case web source """
    website = website.lower()
    words = wordpunct_tokenize(website)
   
    candidates = {}
    for language in stopwords._fileids:
        candidates[language] = len(set(words) & set(stopwords.words(language)))
                
    return candidates
 
def get_language(input_text):
    """Return the most likely language of the given text
    """
 
    likelihoods = get_language_likelihood(input_text)
    
    return sorted(likelihoods, key=likelihoods.get, reverse=True)[0]
""" len(set(input_words) &
                set(stopwords.words(language)))
if __name__ == '__main__':
	with open ("test.txt", "r") as filex:
		read = filex.read().lower()
		
		
		#input_text = " ".join([x for x in stdin.readlines()])

	
	resultdict = {}
	.. {1:"german", 2:"english",...} #so sieht das aus
	sqlanfrage = (id,get_all_htmls, sqalchemy) (1,htmlseite)
	
	for seite in sqlanfrage:
		sprachergebnis = get_language(seite)
		resultdict[sqlanfrage[0]] = sprachergebnis
"""	
		
	
	
	
	
print get_language("Stadt Land Fenster")
print get_language_likelihood("hallo ein wort bla bla")

