import os
import shutil
from utils import convert_jpeg_to_tiff, convert_tiff_to_jpeg, rename_image_files

def process_tipo_folder(tipo_folder):
    tif_folder = tipo_folder.replace('JPG', 'TIF')

    if not os.path.exists(tif_folder):
        os.makedirs(tif_folder)

    for dirpath, dirnames, filenames in os.walk(tipo_folder):
        for filename in filenames:
            if filename.lower().endswith('.tif'):
                tiff_path = os.path.join(dirpath, filename)

                # Copy TIF to TIF folder
                relative_path = os.path.relpath(dirpath, tipo_folder)
                new_tif_dir = os.path.join(tif_folder, relative_path)
                if not os.path.exists(new_tif_dir):
                    os.makedirs(new_tif_dir)
                new_tif_path = os.path.join(new_tif_dir, os.path.basename(tiff_path))
                shutil.copy(tiff_path, new_tif_path)

                # Convert TIF to JPEG and copy to JPG folder
                jpeg_path = convert_tiff_to_jpeg(tiff_path)
                new_jpg_dir = os.path.join(jpg_folder, relative_path)
                if not os.path.exists(new_jpg_dir):
                    os.makedirs(new_jpg_dir)
                new_jpg_path = os.path.join(new_jpg_dir, os.path.basename(jpeg_path))
                shutil.copy(jpeg_path, new_jpg_path)

            elif filename.lower().endswith('.jpg'):
                jpeg_path = os.path.join(dirpath, filename)

                # Copy JPEG to JPG folder
                relative_path = os.path.relpath(dirpath, tipo_folder)
                new_jpg_dir = os.path.join(jpg_folder, relative_path)
                if not os.path.exists(new_jpg_dir):
                    os.makedirs(new_jpg_dir)
                new_jpg_path = os.path.join(new_jpg_dir, os.path.basename(jpeg_path))
                shutil.copy(jpeg_path, new_jpg_path)

                # Convert JPEG to TIFF and copy to TIF folder
                tiff_path = convert_jpeg_to_tiff(jpeg_path)
                new_tif_dir = os.path.join(tif_folder, relative_path)
                if not os.path.exists(new_tif_dir):
                    os.makedirs(new_tif_dir)
                new_tif_path = os.path.join(new_tif_dir, os.path.basename(tiff_path))
                shutil.copy(tiff_path, new_tif_path)

def process_root_folder(root_folder):
    for dirpath, dirnames, filenames in os.walk(root_folder):
        for dirname in dirnames:
            if dirname in ['JPG', 'TIF', 'PDF']:
                tipo_folder = os.path.join(dirpath, dirname)
                if dirname == 'JPG':
                    process_tipo_folder(tipo_folder)
                # Add any additional processing for TIF and PDF folders if needed

def main():
    root_folder = input("Please, input the root folder: ")
    process_root_folder(root_folder)
    rename_image_files(root_folder)

if __name__ == "__main__":
    main()
