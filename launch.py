from configparser import ConfigParser
from argparse import ArgumentParser

from utils.server_registration import get_cache_server
from utils.config import Config
from crawler import Crawler

from crawler_data import Crawler_Data

def main(config_file, restart):
    CRAWLER_DATA = Crawler_Data()
    
    try:
        cparser = ConfigParser()
        cparser.read(config_file)
        config = Config(cparser)
        config.cache_server = get_cache_server(config, restart)
        crawler = Crawler(config, restart, CRAWLER_DATA)
        crawler.start()
    except:
        pass
    
    CRAWLER_DATA.get_final_report()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--restart", action="store_true", default=False)
    parser.add_argument("--config_file", type=str, default="config.ini")
    args = parser.parse_args()
    main(args.config_file, args.restart)
