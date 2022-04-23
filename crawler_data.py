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
        self.hash_queue = self.load_pickle('hash_queue.p', self.hash_queue)
        
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
        self.dump_pickle('hash_queue.p', self.hash_queue)
            
        
        # tokenize the page
        text_tokens = nltk.tokenize.word_tokenize(soup.get_text())
        
        # get longest page from pickle
        self.longest_page = self.load_pickle('longest_page.p', self.longest_page)
        
        # update longest page
        if len(text_tokens) > self.longest_page[1]:
            self.longest_page[1] = len(text_tokens)
            self.longest_page[0] = url
            
            self.dump_pickle('longest_page.p', self.longest_page)


        # get dict of common words from pickle
        self.words = self.load_pickle('words.p', self.words)
            
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
        self.dump_pickle('words.p', self.words)

        # update ics.uci.edu subdomain count
        parsed = urlparse(url)
        
        if re.match(r"((.*\.)*ics\.uci\.edu.*)", parsed.netloc) and parsed.path:
            # get subdomains from pickle
            self.subdomains = self.load_pickle('subdomains.p', self.subdomains)
            self.subdomains[parsed.netloc].add(parsed.path)
            self.dump_pickle('subdomains.p', self.subdomains)
            
        return True

    def load_pickle(self, file_name, data_var):
        try:
            # open the pickle file and return the data
            with open(f"data/{file_name}", 'rb') as file:
                return pickle.load(file)
        except:
            # if there was an error (file not found), return the original data
            return data_var

    def dump_pickle(self, file_name, data_var):
        with open(f'data/{file_name}', 'wb') as file:
            pickle.dump(data_var, file)

    def get_final_report(self):
        self.longest_page = self.load_pickle('longest_page.p', self.longest_page)
        print(f'longest page: {self.longest_page}\n')

        self.words = self.load_pickle('words.p', self.words)
        sorted_words = sorted(self.words, key=lambda w: -self.words[w])[:50]
        print(f'sorted words: {sorted_words}\n')
        
        self.subdomains = self.load_pickle('subdomains.p', self.subdomains)
        subdomains_sorted = sorted([(key, len(self.subdomains[key])) for key in self.subdomains], key = lambda x : x)
        print(f'tuples of subdomains and number: {subdomains_sorted}\n')
        
        num_lines = sum(1 for line in open('finalLink.txt'))
        print(f"unique pages: {num_lines}")

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
        
        
        