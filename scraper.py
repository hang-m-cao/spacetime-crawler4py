import re
from crawler_data import Crawler_Data
from urllib.parse import urlparse
from bs4 import BeautifulSoup

DEBUG = True

CRAWLER_DATA = Crawler_Data()
#COUNT = 0

def scraper(url, resp):
    
    links = extract_next_links(url, resp)
    valid_links = [link for link in links if is_valid(link)]
    
    # for link in valid_links:
    #     print(link)

    CRAWLER_DATA.print_visited_pages()
    return [] # change to valid links to crawl

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    
    if resp.status != 200:
        return []

    parsed_url = urlparse(resp.url)
    
    # get all links from html page
    links = []
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    
    #--------------------- COMMENTED OUT TEMPORARILY
    CRAWLER_DATA.analyze(url, soup)
    
    # convert to absolute
    # determine if link is relative (attach current URL) or absolute (leave as is)
    for link in set(soup.find_all('a')):
       
        href = link.get('href')
        
        abs_link = ''
        
        # eliminate '/' and fragments
        if (not href or len(href) <= 1 or href[0] == '#'):
            continue
            
        if (href.startswith('mailto')):
            continue
        
        # if DEBUG:
        #     print(href)
            
        # same scheme but different domain
        if (href.startswith('//')):
            abs_link = f'{parsed_url.scheme}://{href}'
        
        # going up directories
        elif (href.startswith('..')):
            up_dire_count = href.count('..')
            href_match = re.search(r"(../)+(.*)")
            paths = parsed_url.path.split('/')
            parent = f'{parsed_url.scheme}://{parsed_url.netloc}'
            
            # goes up too many directories
            if up_dire_count >= len(paths):
                abs_link = parent
            else:
                abs_link = f"{parent}/{'/'.join(paths[:-up_dire_count])}/{href_match.group(2)}"
        
        # different domain
        elif (href.startswith('http')):
            abs_link = href
        
        # relative url
        # check if href has /
        elif (href.startswith('/')):
            abs_link = resp.url + href
        else:
            abs_link = f"{resp.url}/{href}"
        
        # remove fragments if any
        final_link = urlparse(abs_link)._replace(fragment="").geturl()
        links.append(final_link)
        
#         if DEBUG:
#             print('======================== FINAL LINK:', final_link)
        
    #------------------DELETE
    links.append('https://today.uci.edu/department/information_computer_sciences/')
    
    return links

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    
    # check if URL has been crawled
    # check if within allowed domains
    # check for traps
    try:
        
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        if not re.match(r"((.*\.)*ics\.uci\.edu.*)|"
                        + r"((.*\.)*cs\.uci\.edu.*)|"
                        + r"((.*\.)*informatics\.uci\.edu.*)|"
                        + r"((.*\.)*stat\.uci\.edu.*)|" 
                        + r"(today\.uci\.edu\/department\/information_computer_sciences\/.*)",
                       parsed.netloc + parsed.path):
            return False
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()):
            return False
        
    
        if CRAWLER_DATA.visited_page(url):
            return False
        
        return True

    except TypeError:
        print ("TypeError for ", parsed)
        raise
