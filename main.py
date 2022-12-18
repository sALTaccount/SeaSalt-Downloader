def scrape_one(param):
    scraper, filt, processor, saver, url = param
    image, meta = scraper.Scraper.get_post(scraper, url)
    image, meta = filt.Filt.filt(filt, image, meta, args.filter[1:])
    if processor:
        image, meta = processor.Processor.process(processor, image, meta, args.preproc[1:])
    if image and meta:
        saver.Saver.save(saver, image, meta, args.saver[1:])


if __name__ == '__main__':
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
    # parser.add_argument('-n', '--parallelism')
    # parser.add_argument('-b', '--batch')

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
    processor = lazy_import('modules.preproc.' + args.preproc[0]) if args.preproc else None
    saver = lazy_import('modules.saver.' + args.saver[0])

    BATCH_SIZE = 3
    NUM_THREADS = 16

    if not args.parallel:
        cur_url = args.url
        to_scrape = scraper.Scraper.get_posts(scraper, cur_url)
        if to_scrape:
            while True:
                while to_scrape:
                    if ctrl_c:
                        sys.exit()
                    try:
                        scrape_one((scraper, filt, processor, saver, to_scrape.pop()))
                    except Exception as e:
                        print(e)
                cur_url = scraper.Scraper.next_page(scraper, cur_url)
                if not cur_url:
                    break
                print('Navigating to', cur_url)
                to_scrape = scraper.Scraper.get_posts(scraper, cur_url)
        else:
            print('No posts found!')
        print('Finished!')
    else:
        raise NotImplementedError('parallel downloading doesn\'t work yet!')
        cont = True
        cur_url = args.url
        urls = []
        while not ctrl_c:
            tqdm.write('Loading batch...')
            for _ in tqdm(range(BATCH_SIZE)):
                if not cont:
                    break
                new_urls = scraper.Scraper.get_posts(scraper, cur_url)
                urls += new_urls
                cur_url = scraper.Scraper.next_page(scraper, cur_url)
                if not cur_url:
                    cont = False

            tqdm.write('Downloading batch...')
            tasks = [(scraper, filt, processor, saver, url) for url in urls]
            p_map(scrape_one, tasks, **{"num_cpus": NUM_THREADS})
            if not cont:
                break
        print(urls)
