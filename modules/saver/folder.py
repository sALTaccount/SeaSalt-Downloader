import os
import shutil


class Saver:
    def save(self, image, meta, args):
        os.makedirs(args[0], exist_ok=True)
        shutil.copyfileobj(image, open(args[0] + '/' + meta['image_name'] + meta['ext'], 'wb'))
