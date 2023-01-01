import mimetypes

import requests
from bs4 import BeautifulSoup


class Scraper:

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0"
    }

    def get_posts(self, url):
        body = requests.get(url, headers=self.headers).text
        soup = BeautifulSoup(body, 'html.parser')
        links = []
        for link in soup.find_all('a', {"class": "post-preview-link"}):
            links.append('https://danbooru.donmai.us' + link.attrs['href'])
        return links

    def get_post(self, url):
        try:
            body = requests.get(url, headers=self.headers).text
            soup = BeautifulSoup(body, 'html.parser')
            image_url = soup.find('li', {'id': 'post-info-size'}).contents[1].attrs['href']
            meta = {'image_name': url.split('/')[-1].split('?')[0]}
            tags = soup.find('section', {'class': 'image-container note-container'}).attrs['data-tags'].split()
            meta['tags'] = tags
            r = requests.get(image_url, stream=True, headers=self.headers)

            if r.status_code == 200:
                r.raw.decode_content = True
                meta['ext'] = mimetypes.guess_extension(r.headers['content-type'])
                return r.raw, meta
            else:
                print(f'Got {r.status_code} for {url}')
        except Exception as e:
            return None, None

    def next_page(self, url):
        body = requests.get(url, headers=self.headers).text
        soup = BeautifulSoup(body, 'html.parser')
        paginator = soup.find('a', {'class': 'paginator-next'})
        try:
            return 'https://danbooru.donmai.us' + paginator.attrs['href']
        except AttributeError:
            return None
