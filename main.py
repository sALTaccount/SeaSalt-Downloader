
def scrape_one(param):
    try:
        scraper, filt, processor, saver, url = param
        image, meta = scraper.get_post(url)
        if image and meta:
            image, meta = filt.filt(image, meta, args.filter[1:])
        if processor and image and meta:
            image, meta = processor.process(image, meta, args.preproc[1:])
        if image and meta:
            saver.save(image, meta, args.saver[1:])
    except Exception as e:
        pass


if __name__ == '__main__':
    import os
    import argparse
    import importlib
    import signal
    import sys
    from p_tqdm import p_map
    from tqdm import tqdm

    parser = argparse.ArgumentParser(description='A generic, modular scraper')

    parser.add_argument('-u', '--url', required=True)
    parser.add_argument('-s', '--scraper', nargs='+', required=True)
    parser.add_argument('-f', '--filter', nargs='+', required=True)
    parser.add_argument('-o', '--saver', nargs='+', required=True)
    parser.add_argument('-p', '--preproc', nargs='+')
    parser.add_argument('-a', '--parallel', action='store_true')
    parser.add_argument('-b', '--batch_size')
    parser.add_argument('-t', '--threads')

    args = parser.parse_args()

    BATCH_SIZE = args.batch_size if args.batch_size else 10
    if args.parallel:
        NUM_THREADS = args.threads if args.threads else os.cpu_count()
        print(f'Using {NUM_THREADS} threads')

    ctrl_c = False

    def handler(signum, frame):
        global ctrl_c
        if ctrl_c and __name__ == '__main__':
            print(f"system: forcefully exiting...")
            sys.exit(1)
        if not ctrl_c and __name__ == '__main__':
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
    filt = lazy_import('modules.filters.' + args.filter[0]) if args.filter else None
    processor = lazy_import('modules.preproc.' + args.preproc[0]) if args.preproc else None
    saver = lazy_import('modules.saver.' + args.saver[0])

    scraper = scraper.Scraper()
    if args.filter:
        filt = filt.Filt()
    if args.preproc:
        processor = processor.Processor()
    saver = saver.Saver()

    if not args.parallel:
        cur_url = args.url
        to_scrape = scraper.get_posts(cur_url)
        if to_scrape:
            while True:
                while to_scrape:
                    if ctrl_c:
                        sys.exit()
                    scrape_one((scraper, filt, processor, saver, to_scrape.pop()))
                cur_url = scraper.next_page(cur_url)
                if not cur_url:
                    break
                print('Navigating to', cur_url)
                to_scrape = scraper.get_posts(cur_url)
        else:
            print('No posts found!')
        print('Finished!')
    else:
        cont = True
        cur_url = args.url
        urls = []
        while not ctrl_c:
            tqdm.write('Loading batch...')
            for _ in tqdm(range(BATCH_SIZE)):
                if not cont:
                    break
                new_urls = scraper.get_posts(cur_url)
                urls += new_urls
                cur_url = scraper.next_page(cur_url)
                if not cur_url:
                    cont = False

            tqdm.write('Downloading batch...')
            tasks = [(scraper, filt, processor, saver, url) for url in urls]
            p_map(scrape_one, tasks, **{"num_cpus": NUM_THREADS})
            if not cont:
                break
            urls = []
