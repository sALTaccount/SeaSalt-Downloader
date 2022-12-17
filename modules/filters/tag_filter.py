class Filt:
    def filt(self, image, meta, args):
        if args:
            for arg in args:
                if arg in meta['tags']:
                    print('filtered out', meta['image_name'])
                    return None, None
        return image, meta
