import re
from crawler_data import Crawler_Data
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

def scraper(url, resp, crawler_data):
    links = extract_next_links(url, resp, crawler_data)
    return links

def extract_next_links(url, resp, crawler_data):
    # Implementation required.
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
    
    # get all links from html page using <a href>
    links = set()
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    
    # for <meta name="robot"> content
    # if content contains any in the set, don't scrap page
    # source: https://www.contentkingapp.com/academy/meta-robots-tag/#noindex
    for robot in soup.find_all("meta", {"name": "robots"}):
        content = robot.get("content")
        if (content and set(content.split(",")).issubset({'nofollow', 'noindex', 'noarchive', 'none'})):
            print("told not to crawl")
            return []
    
    # analyze returns False if content is highly similar to previously crawled page
    if not crawler_data.analyze(url, soup):
        print("highly similar")
        return []

    for link in set(soup.find_all('a')):

        href = link.get('href')
        rel = link.get('rel')
        
        # href link is not authorized by source page
        if rel == "nofollow":
            continue
        
        # eliminate '/' and fragments
        if (not href or len(href) <= 1 or href[0] == '#'):
            continue
            
        if (href.startswith('mailto')):
            continue
            
        # Determines if we should be looking for a file in the current directory or add on to the directory
        if "." not in parsed_url.path and url[-1] != '/':
            url += '/'
        
        # join to convert to absolute
        # determine if link is relative (attach current URL) or absolute (leave as is)
        abs_link = urljoin(url, href)
        
        # remove fragments if any
        final_link = urlparse(abs_link)._replace(fragment="").geturl()
        
        if is_valid(final_link, crawler_data):
            links.add(final_link)

    return links

def is_valid(url, crawler_data):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        
        if re.match(r"&?(ical=|share=|api=|replytocom=)", parsed.query):
            return False
        
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
        
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico|img|war"
            + r"|png|tiff?|mid|mp2|mp3|mp4|mpg"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1|img|war|apk"
            + r"|thmx|mso|arff|rtf|jar|csv|lif"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|m)$", parsed.path.lower()):
            return False
        
        # check for repeating directories
        # source:https://support.archive-it.org/hc/en-us/articles/208332963-Modify-your-crawl-scope-with-a-Regular-Expression
        if re.match(r"^.*?(\/.+?\/).*?\1.*$|^.*?\/(.+?\/)\2.*$", url.lower()):
            return False
        
        return True

    except TypeError:
        print ("TypeError for ", parsed)
        raise
