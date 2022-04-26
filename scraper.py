import re
from crawler_data import Crawler_Data
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
import pickle 

def scraper(url, resp, crawler_data):
    links = extract_next_links(url, resp, crawler_data)
    return links

def extract_next_links(url, resp, crawler_data):
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    
    print(url)
    
    if resp.status != 200 or resp.raw_response == None:
        print("not 200 or no content")
        return []
    
    parsed_url = urlparse(resp.url.strip())
    
    # for later joining url and href
    # Determines if we should be looking for a file in the current directory or add on to the directory
    if "." not in parsed_url.path and url[-1] != '/':
        url += '/'
    
    # get all links from html page using <a href>
    links = set()
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    
    # checking of site has a canonical/preferred link in the head of the document
    # if it does, don't index current site and add canonical link if valid
    # returns links to stop furthering
    if soup.head:
        canonical = soup.head.find("link", {"rel": "canonical"})
        if canonical:
            canonical_href = canonical.get('href')
            if parse_href(url, canonical_href, links):
                print('go to canonical:', canonical_href)
                return links 
    
    # for <meta name="robot"> content
    # if content contains any in the set, don't scrap page
    # source: https://www.contentkingapp.com/academy/meta-robots-tag/#noindex
    for robot in soup.find_all("meta", {"name": "robots"}):
        content = robot.get("content")
        # if there are specified keywords and those keywords are nofollow, noindex, and/nor none, do not index page
        if (content and len(set(re.split(',|, ', content)).intersection({'nofollow', 'noindex', 'none'})) > 0):
            print("told not to crawl")
            return []
            
    # analyze returns False if content is highly similar to previously crawled page
    if not crawler_data.analyze(url, soup):
        print("highly similar or content length issue")
        return []

    for link in set(soup.find_all('a')):

        href = link.get('href')
        rel = link.get('rel')
        
        # href link is not authorized by source page
        if rel == "nofollow":
            continue
        
        parse_href(url, href, links)
  
    return links

def parse_href(url, href, links):
    '''
    Given href from <a>, add the absolute link defragmented to set of links
    Returns if there is no href, it is a mailto link or has fragments
    '''
    # eliminate null, mailto, and fragments
    if (not href or href.startswith('mailto') or href[0] == '#'):
        return False

    # join to convert to absolute
    # determine if link is relative (attach current URL) or absolute (leave as is)
    abs_link = urljoin(url, href)
    
    # remove fragments if any
    final_link = urlparse(abs_link)._replace(fragment="").geturl()
   
    if final_link and is_valid(final_link):
        links.add(final_link)
        return True
    return False


def is_valid(url):
    '''
    Decide whether to crawl this url or not. 
    Return True is URL can be crawled
    Checks scheme, domain, queries, and file extensions.
    Also checks for traps (repeating directories or not allowed by robots.txt)
    '''
    try:
        parsed = urlparse(url)
        
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        # check if within allowed domains
        if not re.match(r"((.*\.)*ics\.uci\.edu.*)|"
                        + r"((.*\.)*cs\.uci\.edu.*)|"
                        + r"((.*\.)*informatics\.uci\.edu.*)|"
                        + r"((.*\.)*stat\.uci\.edu.*)|" 
                        + r"(today\.uci\.edu\/department\/information_computer_sciences\/.*)",
                       parsed.netloc + parsed.path):
            return False
        
        # invalid if url has any of specified query or a query parameter with no value
        if re.match(r"&?(ical=|share=|api=|replytocom=)"
                    + r"|(&?(.+)=)$|(&?(.+)=)&(.*)$", parsed.query):
            return False
        
        # file types to ignore
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico|img|war"
            + r"|png|tiff?|mid|mp2|mp3|mp4|mpg"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1|img|war|apk"
            + r"|thmx|mso|arff|rtf|jar|csv|lif"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz"
            + r"|m|bam|ppsx|pps|odc)$", parsed.path.lower()):
            return False
        
        # check for repeating directories
        # source:https://support.archive-it.org/hc/en-us/articles/208332963-Modify-your-crawl-scope-with-a-Regular-Expression
        if re.match(r"^.*?(\/.+?\/).*?\1.*$|^.*?\/(.+?\/)\2.*$", url.lower()):
            return False
        
        # checking robots.txt to see if allowed to crawl url
        # open pickle file to check if domain has a parser
        robot_pickle = "data/robots.p"
        robot_parsers = {}
        try:
            # open the pickle file and return the data
            with open(robot_pickle, 'rb') as file:
                robot_parsers = pickle.load(file)
        except:
            # has not made robot parser file
            pass
        
        if not parsed.netloc in robot_parsers:
            try:
                rp = RobotFileParser()
                rp.set_url(f"{parsed.scheme}://{parsed.netloc}/robots.txt")
                rp.read()

                robot_parsers[parsed.netloc] = rp
            except:
                print("there was an error reading for:", url)
                robot_parsers[parsed.netloc] = None
            
            # dump data to pickle file
            with open(robot_pickle, 'wb') as file:
                pickle.dump(robot_parsers, file)
        
        parser = robot_parsers[parsed.netloc]
        if parser:
            return parser.can_fetch("*", url)
        return True
        
    except TypeError:
        print ("TypeError for ", parsed)
        raise

