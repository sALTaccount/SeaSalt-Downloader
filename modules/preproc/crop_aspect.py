import io

from PIL import Image


class Processor:
    def process(self, image, meta, args):
        image = Image.open(image)
        format = Image.registered_extensions()[meta['ext']]
        aspect = float(int(args[0]) / int(args[1]))

        if image.width / image.height > aspect:
            new_width = int(image.height * aspect)
            new_height = image.height
        else:
            new_width = image.width
            new_height = int(image.width / aspect)
        image = image.crop((0.5 * (image.width - new_width),
                            0.5 * (image.height - new_height),
                            0.5 * (image.width - new_width) + new_width,
                            0.5 * (image.height - new_height) + new_height))

        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format)
        img_byte_arr = img_byte_arr.getvalue()
        stream = io.BytesIO(img_byte_arr)
        return stream, meta
