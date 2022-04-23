import re
import nltk
from urllib.parse import urlparse
from collections import defaultdict, deque
from simhash import Simhash
import pickle 

# nltk.download('punkt')

STOPWORDS = set()
with open('stopwords.txt', 'r') as file:
    # source: https://stackoverflow.com/questions/12330522/how-to-read-a-file-without-newlines
    lines = file.read().splitlines()
    STOPWORDS = set(lines)


class Crawler_Data:
    def __init__(self):
        self.longest_page = ["", 0]
        self.words = defaultdict(int)
        self.subdomains = defaultdict(set)
        self.hash_queue = deque()
        
    
    def analyze(self, url, soup):
        ''' 
        Tokenizer found on https://stackoverflow.com/questions/46057942/how-to-get-the-text-tokens-when-using-beautifulsoup
        '''
        #tested out different websites, and determined that 90% was good since similar dates were above 90
        #source: bitwise calculator inspo https://www.geeksforgeeks.org/count-set-bits-in-an-integer/
        
        hash_val = Simhash(soup.get_text()).value
        
        # get queue from pickle
        self.load_pickle('hash_queue.p', self.hash_queue)
        
        # calculate whether current doc is similar to previous 100 unique pages
        for hv in self.hash_queue:
            
            # if similar, don't consider page data in final report
            if self.calculate_similarity(hv, hash_val) >= 0.9:
                return False
        
        # add url page to queue, keep queue at 100
        if len(self.hash_queue) >= 100:
            self.hash_queue.popleft()
        
        self.hash_queue.append(hash_val)
        
        # pickle/store hash queue
        with open('data/hash_queue.p', 'wb') as hash_file:
            pickle.dump(self.hash_queue, hash_file)
            
        
        # tokenize the page
        text_tokens = nltk.tokenize.word_tokenize(soup.get_text())
        
        # get longest page from pickle
        self.load_pickle('longest_page.p', self.longest_page)
        
        # update longest page
        if len(text_tokens) > self.longest_page[1]:
            self.longest_page[1] = len(text_tokens)
            self.longest_page[0] = url
            
            with open('data/longest_page.p', 'wb') as long_page_file:
                pickle.dump(self.longest_page, long_page_file)


        # get dict of common words from pickle
        self.load_pickle('words.p', self.words)
            
        # update word dictionary
        for token in text_tokens:
            # Add each lower case version of the tokens into the tokens list
            token = token.lower()
            # Find all the tokens within a word
            t = re.findall("[a-zA-Z0-9]+", token)
            for token in t:
                if token not in STOPWORDS and len(token) > 2:
                    # tokens.append(token)
                    self.words[token] += 1
            
        # store words back using pickle
        with open('data/words.p', 'wb') as common_words:
            pickle.dump(self.words, common_words)


        # update ics.uci.edu subdomain count
        parsed = urlparse(url)
        
        if re.match(r"((.*\.)*ics\.uci\.edu.*)", parsed.netloc) and parsed.path:
            # get subdomains from pickle
            self.load_pickle('subdomains.p', self.subdomains)
            
            self.subdomains[parsed.netloc].add(parsed.path)

            with open('data/subdomains.p', 'wb') as subdomain_page:
                pickle.dump(self.subdomains, subdomain_page)
            
        return True
        
    def test_subdomain(self):
        print(self.subdomain)

        with open('data/subdomains.p', 'wb') as subdomain_page:
            pickle.dump({'1', '2', '3'}, subdomain_page)

        self.load_pickle('subdomains.p', self.subdomains)
        print(self.subdomains)

    def load_pickle(self, file_name, data_var):
        try:
            with open(f"data/{file_name}", 'rb') as file:
                data_var = pickle.load(file)
        except:
            pass

    def get_final_report(self):
        #print(f'unique pages: {len(self.visited_pages)}')
        print(f'longest page: {self.longest_page}')
        #print(self.words)
        #sorted_words = sorted(self.words, key=lambda w: -self.words[w])[:50]
        #print(f'sorted words: {sorted_words}\n')
        #print(f'subdomains: {self.subdomains}\n')
        subdomain_tuples = sorted([(key, len(self.subdomains[key])) for key in self.subdomains], key = lambda x : x)
        print(f'tuples of subdomains and number: {subdomain_tuples}\n')

    
    # calculate similarity percentage between two given decimal numbers
    # based on how many bits they have in the same position
    def calculate_similarity(self, num1, num2):
        # total number of bits
        n = 0 
        # count of bits in the same position
        count = 0 
        
        while (num1 or num2):
            # if both ends are equal to each other
            # &1 returns a 1 if the last bit is 1 and returns 0 if last bit is 0
            if num1&1 == num2&1:
                count += 1
            num1 >>= 1
            num2 >>= 1
            n += 1
            
        return count / n
        
        
        