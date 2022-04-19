import re
import nltk
from urllib.parse import urlparse
from collections import defaultdict

# nltk.download('punkt')

STOPWORDS = set()
with open('stopwords.txt', 'r') as file:
    # source: https://stackoverflow.com/questions/12330522/how-to-read-a-file-without-newlines
    lines = file.read().splitlines()
    STOPWORDS = set(lines)


class Crawler_Data:
    def __init__(self):
        self.visited_pages = set()
        self.longest_page = ""
        self.longest_num_words = 0
        self.words = defaultdict(int)
        self.subdomains = defaultdict(set)
        
    def visited_page(self, url):
        return url in self.visited_pages
    
    def analyze(self, url, soup):
        ''' 
        Tokenizer found on https://stackoverflow.com/questions/46057942/how-to-get-the-text-tokens-when-using-beautifulsoup
        '''
        # add to unique pages found
        self.visited_pages.add(url)
        
        # tokenize the page
        text_tokens = nltk.tokenize.word_tokenize(soup.get_text())
        
        # update longest page
        if len(text_tokens) > self.longest_num_words:
            self.longest_num_words = len(text_tokens)
            self.longest_page = url
            
        # update word dictionary
        for token in text_tokens:
            token = token.lower()
            if token not in STOPWORDS and len(token) > 1:
                self.words[token] += 1
            
        # update ics.uci.edu subdomain count
        parsed = urlparse(url)
        
        if re.match(r"((.*\.)*ics\.uci\.edu.*)", parsed.netloc):
            self.subdomains[parsed.netloc].add(parsed.path)
        
    
    def print_visited_pages(self):
        print(f'unique pages:{len(self.visited_pages)}')
        print(f'longest page:{self.longest_page}')
        #print(self.words)
        sorted_words = sorted(self.words, key=lambda w: -self.words[w])[:50]
        print(f'sorted words: {sorted_words}')
        print(f'subdomains: {self.subdomains}')
        
        
        