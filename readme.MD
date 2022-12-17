# SeaSalt Downloader

SeaSalt Downloder is a modular downloader for any site you can make a module for.

## Features
 * Supports custom websites
 * Supports custom filters
 * Supports custom saving methods
 * Synchronous and Asynchronous download (TODO)

## Included Modules:
* Scrapers
   * Danbooru (`danbooru`)
   * Safebooru (`safebooru`)
* Filters
   * No Filter (`no_filter`)
   * Tag filter (`tag_filter`)
* Savers
   * Folder with no metadata (`folder_no_meta`)

## Usage
```commandline
python main.py -u <url> \
--scraper <scraper name> optional<scraper args> \
--filter <filter name> optional<filter args> \
--saver <saver name> optional<saver args>
```
For example, to scrape all images of Shirakami Fubuki from Safebooru, while filtering out any posts that have the `1girl` tag, and saving to a folder called `Fubuki with friends` while discarding metadata:
```commandline
python main.py -u "https://safebooru.org/index.php?page=post&s=list&tags=shirakami_fubuki+" \
--scraper safebooru \
--filter tag_filter 1girl \
--saver folder_no_meta "Fubuki with friends"
```
## Writing Modules

### Scrapers
Each scraper must be a python file that contains a class `Scraper`

The scraper class must implement the following methods
```py
    def get_posts(self, url):
        # URL is a page containing posts
        # Must return a list of URLs to posts on the page
        
    def get_post(self, url):
        # URL is a URL to a post
        # Return a tuple in which t[0] is a stream to the image
        # and t[1] is the image metadata
        #
        # The metadata must be a dictionary containing the following items:
        #   'image_name', the file name (no extension)
        #   'ext', the file extension
        #   'tags', the tags for the image
        # Other metadata can be added to the dictionary, but it is not
        # guaranteed support by existing modules
        
    def next_page(self, url):
        # URL is a URL to the current page
        # Return a URL to the next page
```
You are free to implement variables, imports, and other functions into your `Scraper` class as well
### Filters
Each filter must be a python file the contains a class `Filt`

The `Filt` class must implement a method named `filt`
```py
    def filt(self, image, meta, args):
        # image is an image stream
        # meta is the image metadata (as defined in the scraper section)
        # args are the optional arguments provided by the user
        # return a tuple containing (image, meta)
        # or return (None, None) to filter out the image
```
You are free to implement variables, imports, and other functions into your `Filt` class as well

### Savers
Each saver must be a python file that contains a class `Save`

Your `save` class must implement a method named `save`
```py
class Saver:
    def save(self, image, meta, args):
        # image is a stream to the image
        # meta is the image metadata (as defined in the scraper section)
        # args are the optional arguments provided by the user
```
You are free to implement variables, imports, and other functions into your `Saver` class as well

## TODO
Features
* Make readme more accurate
* Implement async
* Setup exit handler

Modules
* Zerochan scraper
* Pixiv scraper
* Resize saver
* Biggest square saver