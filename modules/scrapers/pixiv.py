import io
import json
import mimetypes
import gzip
import time

# import requests
import httpx
import requests
from bs4 import BeautifulSoup


class Scraper:

    headers = {
        # "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
        "User-Agent": "testagent",
        "Host": "www.pixiv.net",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "DNT": "1"
    }

    headers_image = {
        "User-Agent": "testagent",
        "Host": "i.pximg.net",
        "Accept": "*/*",
        "DNT": "1",
        "Referer": "https://www.pixiv.net/"
    }

    def __init__(self):
        self.profile_id = None
        self.illustrations = None
        self.cur_post_idx = 0
        self.sleep_delay = 1
        self.posts_per_page = 20
        self.reached_end = False

    def get_posts(self, url, parallel, args):
        if not self.illustrations:
            if not self.profile_id:
                self.profile_id = url.replace('https://www.pixiv.net/en/users/', '').split('/')[0]
            url = f"https://www.pixiv.net/ajax/user/{self.profile_id}/profile/all"
            response = httpx.Client(http2=True).get(url, headers=self.headers).json()
            self.illustrations = list(response['body']['illusts'].keys())
        if self.cur_post_idx + self.posts_per_page >= len(self.illustrations):
            illustrations = self.illustrations[self.cur_post_idx:]
            self.reached_end = True
        else:
            illustrations = self.illustrations[self.cur_post_idx:self.cur_post_idx + self.posts_per_page]
        self.cur_post_idx += self.posts_per_page
        return [f"https://www.pixiv.net/en/artworks/{illustration}" for illustration in illustrations]

    def get_post(self, url, parallel, args):
        try:
            response = requests.get(url)
            time.sleep(1 if parallel else 0)
            body = response.text
            soup = BeautifulSoup(body, 'html.parser')
            web_meta = soup.find_all('meta', {'name': 'preload-data'})[0]
            meta_json = json.loads(web_meta.attrs['content'])
            image_url = list(meta_json['illust'].items())[0][1]['urls']['original']
            r = requests.get(image_url, headers=self.headers_image, stream=True)
            meta = {'image_name': url.split('/')[-1]}
            if r.status_code == 200:
                r.raw.decode_content = True
                meta['ext'] = mimetypes.guess_extension(r.headers['content-type'])
                return r.raw, meta
            else:
                print(f'Got {r.status_code} for {url}')
        except Exception as e:
            print(f'Got exception {e} for {url}')
            return None, None

    def next_page(self, url, parallel, args):
        return None if self.reached_end else url

