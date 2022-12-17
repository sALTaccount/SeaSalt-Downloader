import io

from PIL import Image


class Processor:
    def process(self, image, meta, args):
        image = Image.open(image)
        format = Image.registered_extensions()[meta['ext']]
        x = int(args[0])
        y = int(args[1])

        image = image.resize((x,y), Image.Resampling.LANCZOS)

        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format)
        img_byte_arr = img_byte_arr.getvalue()
        stream = io.BytesIO(img_byte_arr)
        return stream, meta
