import io

from PIL import Image


class Processor:
    def process(self, image, meta, args):
        if meta['ext'] not in ['.jpg', '.jpeg', 'png']:
            return None, None
        image = Image.open(image)
        format = Image.registered_extensions()['.png']  # meta['ext']]
        aspect = float(int(args[0]) / int(args[1]))
        x = int(args[2])
        y = int(x * int(args[1]) / int(args[0]))

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

        image = image.resize((x, y), Image.Resampling.LANCZOS)

        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format)
        img_byte_arr.seek(0)
        img_byte_arr = img_byte_arr.read()
        stream = io.BytesIO(img_byte_arr)
        return stream, meta
