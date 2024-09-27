import os
from PIL import Image

def convert_jpeg_to_tiff(jpeg_path, output_dir):
    tiff_path = os.path.join(output_dir, os.path.basename(jpeg_path).rsplit('.', 1)[0] + '.tif')
    with Image.open(jpeg_path) as img:
        img = img.convert('RGB')
        img.save(tiff_path, format='TIFF')
    return tiff_path

def convert_tiff_to_jpeg(tiff_path, output_dir):
    jpeg_path = os.path.join(output_dir, os.path.basename(tiff_path).rsplit('.', 1)[0] + '.jpg')
    with Image.open(tiff_path) as img:
        img = img.convert('RGB')
        img.save(jpeg_path, format='JPEG')
    return jpeg_path