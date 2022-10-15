import datetime
import queue
import urllib.parse

import database
import downloader


def run(init_url):
    url_queue = UrlQueue()
    url_queue.add(init_url)

    try:
        i = 0
        while i < 1000:
            wd = downloader.get_website_data(url_queue.get())

            print(f'[{wd["code"]}] {wd.get("c_url", wd.get("r_url", wd["s_url"]))}')

            if wd.get('links'):
                url_queue.update(wd['links'])

            database.write_website_data(wd)
            i += 1
    except queue.Empty:
        print('Empty')
    pass


class UrlQueue:

    def __init__(self):
        self.urls = set()
        self.domain_access_dict = dict()
        pass

    def add(self, item):
        self.urls.add(item)

    def update(self, iterable):
        self.urls.update(iterable)

    def get(self):
        for url in self.urls:
            domain_split = urllib.parse.urlsplit(url).netloc.split('.')

            domain = ''
            if len(domain_split) >= 2:
                domain = domain_split[-2]
            else:
                domain = '.'.join(domain_split)

            if self.domain_access_dict.get(domain, datetime.datetime.min) < datetime.datetime.now():
                self.domain_access_dict[domain] = datetime.datetime.now() + datetime.timedelta(seconds=30)
                self.urls.remove(url)
                return url
        raise queue.Empty()
