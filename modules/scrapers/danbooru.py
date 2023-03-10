import io
import mimetypes
import gzip
import time

# import requests
import httpx
from bs4 import BeautifulSoup


class Scraper:

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
        "Host": "danbooru.donmai.us"
    }

    image_headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
        "Host": "cdn.donmai.us",
    }

    def get_posts(self, url, parallel, args):
        body = httpx.Client(http2=True).get(url, headers=self.headers).content
        soup = BeautifulSoup(body, 'html.parser')
        links = []
        for link in soup.find_all('a', {"class": "post-preview-link"}):
            links.append('https://danbooru.donmai.us' + link.attrs['href'])
        return links

    def get_post(self, url, parallel, args):
        try:
            with httpx.Client(http2=True) as client:
                time.sleep(1 if parallel else 0)
                body = client.get(url, headers=self.headers).text
                soup = BeautifulSoup(body, 'html.parser')
                image_url = soup.find('li', {'id': 'post-info-size'}).contents[1].attrs['href']
                meta = {'image_name': url.split('/')[-1].split('?')[0]}
                tags = soup.find('section', {'class': 'image-container note-container'}).attrs['data-tags'].split()
                meta['tags'] = tags
                response = client.get(image_url, headers=self.image_headers)
                if response.status_code == 200:
                    meta['ext'] = mimetypes.guess_extension(response.headers['content-type'])
                    stream = io.BytesIO(response.content)
                    return stream, meta
                else:
                    print(f'Got {response.status_code} for {image_url}')

        except Exception as e:
            return None, None

    def next_page(self, url, parallel, args):
        body = httpx.Client(http2=True).get(url, headers=self.headers).text
        soup = BeautifulSoup(body, 'html.parser')
        paginator = soup.find('a', {'class': 'paginator-next'})
        try:
            return 'https://danbooru.donmai.us' + paginator.attrs['href']
        except AttributeError:
            return None
