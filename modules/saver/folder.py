import os
import shutil
import json


class Saver:
    def save(self, image, meta, args):
        os.makedirs(args[0], exist_ok=True)
        shutil.copyfileobj(image, open(args[0] + '/' + meta['image_name'] + meta['ext'], 'wb'))
        if len(args) > 1 and args[1] == 'json':
            with open(args[0] + '/' + meta['image_name'] + '.json', 'w') as f:
                json.dump(meta, f)
