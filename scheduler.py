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

            url_queue.update_visited({wd[url_type] for url_type in database.URL_TYPES if wd.get(url_type)})
            i += 1
    except queue.Empty:
        print('Empty')
    pass


class UrlQueue:

    def __init__(self):
        self.urls = set()
        self.domain_access_dict = dict()
        self.visited_urls = set()
        pass

    def add_visited(self, url):
        self.visited_urls.add(url)
        self.urls = self.urls - self.visited_urls
        pass

    def update_visited(self, urls):
        self.visited_urls.update(urls)
        self.urls = self.urls - self.visited_urls
        pass

    def add(self, url):
        if url not in self.visited_urls:
            self.urls.add(url)
        pass

    def update(self, urls):
        for url in urls:
            self.add(url)
        pass

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
