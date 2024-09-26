import os
from PIL import Image

def convert_jpeg_to_tiff(jpeg_path):
    tiff_path = jpeg_path.rsplit('.', 1)[0] + '.tif'
    with Image.open(jpeg_path) as img:
        img = img.convert('RGB')
        img.save(tiff_path, format='TIFF')
    return tiff_path

def convert_tiff_to_jpeg(tiff_path):
    jpeg_path = tiff_path.rsplit('.', 1)[0] + '.jpg'
    with Image.open(tiff_path) as img:
        img = img.convert('RGB')
        img.save(jpeg_path, format='JPEG')
    return jpeg_path

def rename_image_files(root_folder):
    for dirpath, dirnames, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.lower().endswith(('.jpg', '.jpeg', '.tif', '.tiff')):
                new_filename = correct_image_filename(filename)
                old_file_path = os.path.join(dirpath, filename)
                new_file_path = os.path.join(dirpath, new_filename)
                os.rename(old_file_path, new_file_path)
