import mimetypes

import requests
from bs4 import BeautifulSoup


class Scraper:
    def get_posts(self, url):
        body = requests.get(url).text
        soup = BeautifulSoup(body, 'html.parser')
        links = []
        for link in soup.find_all('a', {"class": "post-preview-link"}):
            links.append('https://aibooru.online' + link.attrs['href'])
        return links

    def get_post(self, url):
        try:
            body = requests.get(url).text
            soup = BeautifulSoup(body, 'html.parser')
            image_url = soup.find('li', {'id': 'post-info-size'}).contents[1].attrs['href']
            image_url = 'https://aibooru.online' + image_url
            meta = {'image_name': url.split('/')[-1].split('?')[0]}
            tags = soup.find('section', {'class': 'image-container note-container'}).attrs['data-tags'].split()
            meta['tags'] = tags
            r = requests.get(image_url, stream=True)

            if r.status_code == 200:
                r.raw.decode_content = True
                meta['ext'] = mimetypes.guess_extension(r.headers['content-type'])
                return r.raw, meta
            else:
                print(f'Got {r.status_code} for {url}')
        except Exception as e:
            return None, None

    def next_page(self, url):
        body = requests.get(url).text
        soup = BeautifulSoup(body, 'html.parser')
        paginator = soup.find('a', {'class': 'paginator-next'})
        try:
            return 'https://aibooru.online' + paginator.attrs['href']
        except AttributeError:
            return None
