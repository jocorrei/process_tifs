import os
from PIL import Image


def convert_tif_to_jpg(directory):
    for root, dirs, files in os.walk(directory):
        print(dirs)
        for dir_name in dirs:
            if dir_name.lower() == 'jpg':
                tipo_jpg_path = os.path.join(root, dir_name)
                convert_images_in_tipo_jpg(tipo_jpg_path)


def convert_images_in_tipo_jpg(tipo_jpg_path):
    for root, dirs, files in os.walk(tipo_jpg_path):
        for file in files:
            if file.lower().endswith('.tif') or file.lower().endswith('.tiff'):
                file_path = os.path.join(root, file)
                new_file_path = os.path.splitext(file_path)[0] + '.jpg'
                # Open the .tif file and convert to .jpg
                with Image.open(file_path) as img:
                    img.convert('RGB').save(new_file_path, 'JPEG')

                print(f"Converted {file_path} to {new_file_path}")
                # Remove the original .tif file
                os.remove(file_path)
                print(f"Removed {file_path}")


def main():
    root_folder = input("Please, input the root folder: ")
    convert_tif_to_jpg(root_folder)


if __name__ == "__main__":
    main()
