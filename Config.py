# coding=utf8
import pickle
from datetime import datetime


class LocalConfig:
    def __init__(self):
        self.rss_config = {}
        self.target_group = "DO not milk"

    def first_init(self):
        self.update_rss_time("https://www.google.com/alerts/feeds/15854071947442795714/643669568502323902")
        self.update_rss_time("https://www.google.com/alerts/feeds/15854071947442795714/12450745865747729626")

    def update_rss_time(self, rss_url,
                        rss_last_time=datetime.strptime("1992-09-09 10:10:00.000", "%Y-%m-%d %H:%M:%S.%f")):
        self.rss_config[rss_url] = rss_last_time

    def get_rss_last_time(self, rss_url):
        if rss_url not in self.rss_config:
            self.rss_config[rss_url] = datetime.strptime("1992-09-09 10:10:00.000", "%Y-%m-%d %H:%M:%S.%f")
        return self.rss_config[rss_url]


def save_to_file(config: LocalConfig):
    pickle.dump(config, open("config.pkl", "wb"))


def read_from_file():
    try:
        return pickle.load(open("config.pkl", "rb"))
    except:
        return LocalConfig()
