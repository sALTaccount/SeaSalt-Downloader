import argparse
import importlib
import logging
import shutil
import signal
import sys

parser = argparse.ArgumentParser(description='A generic, modular scraper')

parser.add_argument('-u', '--url', required=True)
parser.add_argument('-s', '--scraper', nargs='+', required=True)
parser.add_argument('-f', '--filter', nargs='+', required=True)
parser.add_argument('-o', '--saver', nargs='+', required=True)
parser.add_argument('-p', '--preproc', nargs='+')

args = parser.parse_args()

ctrl_c = False


def handler(signum, frame):
    global ctrl_c
    if ctrl_c:
        print(f"system: forcefully exiting...")
        sys.exit(1)
    print(f"system: ctrl+c was pressed (press ctrl+c again to force quit). exiting gracefully...")
    ctrl_c = True


signal.signal(signal.SIGINT, handler)


def lazy_import(name):
    spec = importlib.util.find_spec(name)
    loader = importlib.util.LazyLoader(spec.loader)
    spec.loader = loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    loader.exec_module(module)
    return module


scraper = lazy_import('modules.scrapers.' + args.scraper[0])
filt = lazy_import('modules.filters.' + args.filter[0])
saver = lazy_import('modules.saver.' + args.saver[0])
processor = lazy_import('modules.preproc.' + args.preproc[0]) if args.preproc else None

cur_url = args.url
to_scrape = scraper.Scraper.get_posts(scraper, cur_url)
if to_scrape:
    while True:
        while to_scrape:
            if ctrl_c:
                sys.exit()
            image, meta = scraper.Scraper.get_post(scraper, to_scrape.pop())
            image, meta = filt.Filt.filt(filt, image, meta, args.filter[1:])
            if processor:
                image, meta = processor.Processor.process(processor, image, meta, args.preproc[1:])
            if image and meta:
                saver.Saver.save(saver, image, meta, args.saver[1:])
                print('Saved', meta['image_name'])
        cur_url = scraper.Scraper.next_page(scraper, cur_url)
        print('Navigating to', cur_url)
        to_scrape = scraper.Scraper.get_posts(scraper, cur_url)
        if not to_scrape:
            break
else:
    print('No posts found!')
print('Finished!')
