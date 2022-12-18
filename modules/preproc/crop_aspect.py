import io

from PIL import Image


class Processor:
    def process(self, image, meta, args):
        if meta['ext'] not in ['.jpg', '.jpeg', 'png']:
            return None, None
        image = Image.open(image)
        format = Image.registered_extensions()[meta['ext']]
        aspect = float(int(args[0]) / int(args[1]))

        if image.width / image.height > aspect:
            new_width = int(image.height * aspect)
            new_height = image.height
        else:
            new_width = image.width
            new_height = int(image.width / aspect)
        image = image.crop((int(0.5 * (image.width - new_width)),
                            int(0.5 * (image.height - new_height)),
                            int(0.5 * (image.width - new_width) + new_width),
                            int(0.5 * (image.height - new_height) + new_height)))

        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format)
        img_byte_arr = img_byte_arr.getvalue()
        stream = io.BytesIO(img_byte_arr)
        return stream, meta
