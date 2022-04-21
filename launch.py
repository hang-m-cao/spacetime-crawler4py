from configparser import ConfigParser
from argparse import ArgumentParser

from utils.server_registration import get_cache_server
from utils.config import Config
from crawler import Crawler

from crawler_data import Crawler_Data


def main(config_file, restart):
    
    #we added
    CRAWLER_DATA = Crawler_Data()
    
    cparser = ConfigParser()
    cparser.read(config_file)
    config = Config(cparser)
    config.cache_server = get_cache_server(config, restart)
    crawler = Crawler(config, restart, CRAWLER_DATA)
    #crawler = Crawler(config, restart)
    crawler.start()
    CRAWLER_DATA.print_visited_pages()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--restart", action="store_true", default=False)
    parser.add_argument("--config_file", type=str, default="config.ini")
    args = parser.parse_args()
    main(args.config_file, args.restart)
