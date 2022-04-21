import re
import nltk
from urllib.parse import urlparse
from collections import defaultdict, deque
from simhash import Simhash

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
        self.hash_queue = deque()
        
    def visited_page(self, url):
        return url in self.visited_pages
    
    def analyze(self, url, soup):
        ''' 
        Tokenizer found on https://stackoverflow.com/questions/46057942/how-to-get-the-text-tokens-when-using-beautifulsoup
        '''
        #tested out different websites, and determined that 90% was good since similar dates were above 90
        #source: bitwise calculator inspo https://www.geeksforgeeks.org/count-set-bits-in-an-integer/
        
        hash_val = Simhash(soup.get_text()).value
        
        print(hash_val)
        #1011011111101100000111111110100111011000110101000001000001000, 1656625361583768072
        #1011011111101100000111111110100111011000110101000001000011000, 1656625361583768088
        for hv in self.hash_queue:
            if self.calculate_similarity(hv, hash_val) >= 0.9:
                print("reached here")
                return False
        
        if len(self.hash_queue) >= 100:
            self.hash_queue.popleft()
        
        self.hash_queue.append(hash_val)
        
        
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
            # Add each lower case version of the tokens into the tokens list
            token = token.lower()
            # Find all the tokens within a word
            t = re.findall("[a-zA-Z0-9]+", token)
            for token in t:
                if token not in STOPWORDS and len(token) > 1:
                    # tokens.append(token)
                    self.words[token] += 1
            
        # update ics.uci.edu subdomain count
        parsed = urlparse(url)
        
        if re.match(r"((.*\.)*ics\.uci\.edu.*)", parsed.netloc) and parsed.path:
            self.subdomains[parsed.netloc].add(parsed.path)
            
        return True
        
    
    def print_visited_pages(self):
        print(f'unique pages:{len(self.visited_pages)}\n')
        '''
        print(f'longest page:{self.longest_page}\n')
        #print(self.words)
        sorted_words = sorted(self.words, key=lambda w: -self.words[w])[:50]
        print(f'sorted words: {sorted_words}\n')
        print(f'subdomains: {self.subdomains}\n')
        
        #============I added here
        subdomain_tuples = sorted([(key, len(self.subdomains[key])) for key in self.subdomains], key = lambda x : x)
        
        print(f'tuples of subdomains and number: {subdomain_tuples}\n')
        '''
        
        
    def calculate_similarity(self, num1, num2):
        #calculate similarity percentage
        
        n = 0
        count = 0
        while (num1 or num2):
            #if both ends are equal to each other
            #&1 returns a 1 if the last bit is 1 and returns 0 if last bit is 0
            if num1&1 == num2&1:
                count += 1
            num1 >>= 1
            num2 >>= 1
            n += 1
            
        return count / n
        
        
        