import io
import mimetypes
import time

# import requests
import httpx
from bs4 import BeautifulSoup


class Scraper:
    LISTING_QUERY_HASH = '69cba40317214236af40e7efa697781d'
    POST_QUERY_HASH = 'b3055c01b4b222b8a47dc12b090e4e64'
    headers = {
        "X-IG-App-ID": "936619743392459",  # App ID of Web Instagram
    }
    per_page = 24

    user_id = None
    start_cursor = None

    def get_posts(self, url, parallel, args):
        if not self.user_id:
            # get user ID from username
            name = url.split('instagram.com/')[-1].split('/')[0]
            url = f'https://www.instagram.com/api/v1/users/web_profile_info/?username={name}'
            response = httpx.Client(http2=True).get(url, headers=self.headers).json()
            self.user_id = response['data']['user']['id']
        if self.start_cursor:
            url = f'https://www.instagram.com/graphql/query/?query_hash={self.LISTING_QUERY_HASH}&variables={{"id":"{self.user_id}","first":{self.per_page},"after":"{self.start_cursor}"}}'
        else:
            url = f'https://www.instagram.com/graphql/query/?query_hash={self.LISTING_QUERY_HASH}&variables={{"id":"{self.user_id}","first":{self.per_page}}}'
        response = httpx.Client(http2=True).get(url, headers=self.headers).json()
        self.start_cursor = response['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']
        return [f"https://www.instagram.com/p/{node['node']['shortcode']}/" for node in response['data']['user']['edge_owner_to_timeline_media']['edges']]

    def get_post(self, url, parallel, args):
        if parallel:
            time.sleep(1)
        try:
            with httpx.Client(http2=True) as client:
                if url.endswith('/'):
                    url = url[:-1]
                url = url.replace('https://www.instagram.com/p/', 'https://www.instagram.com/graphql/query/?query_hash=' + self.POST_QUERY_HASH + '&variables={"shortcode":"') + '"}'
                response = client.get(url, headers=self.headers).json()
                meta = {'image_name': response['data']['shortcode_media']['shortcode']}
                image_url = response['data']['shortcode_media']['display_url']
                response = client.get(image_url, headers=self.headers)
                if response.status_code == 200:
                    meta['ext'] = mimetypes.guess_extension(response.headers['content-type'])
                    stream = io.BytesIO(response.content)
                    return stream, meta
                else:
                    print(f'Got {response.status_code} for {image_url}')
        except Exception as e:
            print(e)
            return None, None

    def next_page(self, url, parallel, args):
        # We handle pagination in get_posts to avoid extra requests
        if self.start_cursor:
            return url
        else:
            return None
