import os
import re
import cv2
import time
import logging
import numpy as np
from PIL import Image
from concurrent.futures import ProcessPoolExecutor, as_completed
import uuid

logging.basicConfig(level=logging.INFO)


def load_image(file_path):
    pil_image = Image.open(file_path).convert(
        'RGB')  # Convert to RGB to ensure uniformity
    image = np.array(pil_image)
    return image


def detect_black_margin(image, threshold=10):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, gray = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)

    top_margin = bottom_margin = left_margin = right_margin = 0

    for i in range(gray.shape[0]):
        if np.any(gray[i, :] != 0):
            top_margin = i
            break

    for i in range(gray.shape[0] - 1, -1, -1):
        if np.any(gray[i, :] != 0):
            bottom_margin = gray.shape[0] - 1 - i
            break

    for i in range(gray.shape[1]):
        if np.any(gray[:, i] != 0):
            left_margin = i
            break

    for i in range(gray.shape[1] - 1, -1, -1):
        if np.any(gray[:, i] != 0):
            right_margin = gray.shape[1] - 1 - i
            break

    # logging.info(f"Margins detected - Left: {left_margin}, Top: {top_margin}, Right: {right_margin}, Bottom: {bottom_margin}")
    return left_margin, top_margin, right_margin, bottom_margin


def crop_image(image, max_margin):
    if max_margin <= 0:
        return image
    cropped_image = image[max_margin:image.shape[0] -
                          max_margin, max_margin:image.shape[1] - max_margin]
    return cropped_image


def add_black_margin(image, margin_size_mm, pixel_to_mm_ratio):
    margin_size_px = int(margin_size_mm / pixel_to_mm_ratio)
    new_shape = (image.shape[0] + 2 * margin_size_px,
                 image.shape[1] + 2 * margin_size_px, image.shape[2])
    new_image = np.zeros(new_shape, dtype=image.dtype)
    new_image[margin_size_px:margin_size_px + image.shape[0],
              margin_size_px:margin_size_px + image.shape[1]] = image
    return new_image


def process_image(file_path, pixel_to_mm_ratio, new_margin_mm):
    try:
        image = load_image(file_path)
        margins = detect_black_margin(image)
        max_margin = max(margins)
        cropped_image = crop_image(image, max_margin)
        final_image = add_black_margin(
            cropped_image, new_margin_mm, pixel_to_mm_ratio)
        final_pil_image = Image.fromarray(final_image)
        final_pil_image.save(file_path)
        return file_path, "Success"
    except Exception as e:
        logging.error(f"Error processing {file_path}: {e}")
        return file_path, f"Error: {e}"


def convert_jpeg_to_tiff(jpeg_path):
    tiff_path = jpeg_path.rsplit('.', 1)[0] + '.tif'
    with Image.open(jpeg_path) as img:
        img = img.convert('RGB')  # Ensure the image is in RGB mode
        img.save(tiff_path, format='TIFF')
    os.remove(jpeg_path)
    # logging.info(f"Converted and removed {jpeg_path}. TIFF saved as {tiff_path}")
    return tiff_path


def rename_files_to_temp(root_folder):
    for dirpath, dirnames, filenames in os.walk(root_folder):
        # Filter out hidden files like .DS_Store
        filenames = [f for f in filenames if not f.startswith('.')]
        filenames.sort()  # Ensure files are sorted alphabetically

        # Start index at 1 for all cases
        for index, filename in enumerate(filenames, start=1):
            if filename.lower().endswith('.tif') or filename.lower().endswith('.tiff'):
                unique_id = str(uuid.uuid4())  # Generate a unique identifier
                temp_filename = f"{index:04d}_{unique_id}.tif"

                old_file_path = os.path.join(dirpath, filename)
                temp_file_path = os.path.join(dirpath, temp_filename)

                os.rename(old_file_path, temp_file_path)
                # print(f"Temporarily renamed {old_file_path} to {temp_file_path}")


def rename_files_to_final(root_folder):
    for dirpath, dirnames, filenames in os.walk(root_folder):
        # Filter out hidden files like .DS_Store
        filenames = [f for f in filenames if not f.startswith('.')]
        filenames.sort()  # Ensure files are sorted alphabetically

        # Only process directories that start with "Caixa"
        if not os.path.basename(dirpath).startswith("Caixa"):
            continue

        # Start index at 1 for all cases
        for index, filename in enumerate(filenames, start=1):
            if filename.lower().endswith('.tif') or filename.lower().endswith('.tiff'):
                relative_path = os.path.relpath(dirpath, root_folder)
                parts = relative_path.split(os.sep)
                if len(parts) == 2:
                    caixa, processo = parts
                    subprocesso = None
                elif len(parts) == 3:
                    caixa, processo, subprocesso = parts
                else:
                    continue

                caixa_number = caixa.split()[1]
                processo_number = processo.split()[1]
                subprocesso_number = subprocesso.split()[
                    1] if subprocesso else '00'

                # Consistent 4-digit formatting
                file_index_str = f"{index:04d}"

                new_filename = f"PT-MNE-CICL-IC-1-{caixa_number}-{processo_number}"
                if subprocesso:
                    new_filename += f"-{subprocesso_number}"
                new_filename += f"_m{file_index_str}.tif"

                temp_file_path = os.path.join(dirpath, filename)
                new_file_path = os.path.join(dirpath, new_filename)

                os.rename(temp_file_path, new_file_path)
                # print(f"Final renamed {temp_file_path} to {new_file_path}")


def process_folder(root_folder, pixel_to_mm_ratio, new_margin_mm):
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = []
        for dirpath, dirnames, filenames in os.walk(root_folder):
            filenames.sort()  # Ensure the files are processed in order
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if filename.lower().endswith('.jpeg') or filename.lower().endswith('.jpg'):
                    tiff_path = convert_jpeg_to_tiff(file_path)
                    futures.append(executor.submit(
                        process_image, tiff_path, pixel_to_mm_ratio, new_margin_mm))
                elif filename.lower().endswith('.tif') or filename.lower().endswith('.tiff'):
                    futures.append(executor.submit(
                        process_image, file_path, pixel_to_mm_ratio, new_margin_mm))
        for future in as_completed(futures):
            file_path, status = future.result()


def rename_files(root_folder):
    rename_files_to_temp(root_folder)
    rename_files_to_final(root_folder)


def main():
    root_folder = input(
        "Please, input the root folder (default is '../HD_fixed'): ") or '../HD_fixed'
    action = input("Do you want to process, rename, or both? ").lower()

    if action not in ["process", "rename", "both"]:
        print("Invalid action. Please enter 'process', 'rename', or 'both'.")
        return

    pixel_to_mm_ratio = 0.1  # Example ratio, adjust based on your image resolution
    new_margin_mm = 5  # New margin size in millimeters

    print("Processing...")

    # stopwatch
    start = time.time()

    if action in ["process", "both"]:
        process_folder(root_folder, pixel_to_mm_ratio, new_margin_mm)

    if action in ["rename", "both"]:
        rename_files(root_folder)

    end = time.time()
    print(f"Operation completed in: {end - start} seconds")


if __name__ == "__main__":
    main()
