class Filt:
    def filt(self, image, meta, args):
        new_args = ['.' + a for a in args]
        if meta['ext'] in new_args:
            return image, meta
        return None, None