import os
import re
import cv2
import time
import logging
import numpy as np
from PIL import Image
from concurrent.futures import ProcessPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO)

def load_image(file_path):
    pil_image = Image.open(file_path).convert('RGB')  # Convert to RGB to ensure uniformity
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

    return left_margin, top_margin, right_margin, bottom_margin

def crop_image(image, max_margin):
    if max_margin <= 0:
        return image
    cropped_image = image[max_margin:image.shape[0]-max_margin, max_margin:image.shape[1]-max_margin]
    return cropped_image

def save_image_as_jpg(image, output_path):
    pil_image = Image.fromarray(image)
    pil_image.save(output_path, format='JPEG', quality=95)

def process_image(file_path):
    try:
        image = load_image(file_path)
        margins = detect_black_margin(image)
        max_margin = max(margins)
        cropped_image = crop_image(image, max_margin)

        # Convert the file path to a JPG output path
        jpg_path = file_path.rsplit('.', 1)[0] + '.jpg'
        save_image_as_jpg(cropped_image, jpg_path)

        os.remove(file_path)  # Remove the original TIFF file
        return jpg_path, "Success"
    except Exception as e:
        logging.error(f"Error processing {file_path}: {e}")
        return file_path, f"Error: {e}"

def extract_file_number(filename):
    match = re.search(r'_m(\d+)', filename)
    if match:
        return int(match.group(1))
    else:
        return float('inf')  # Return a high number to push incorrectly named files to the end

def rename_files(root_folder):
    for dirpath, dirnames, filenames in os.walk(root_folder):
        # Sort filenames based on the number after 'm'
        filenames.sort(key=extract_file_number)
        for index, filename in enumerate(filenames):
            if filename.lower().endswith('.jpg'):
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
                subprocesso_number = subprocesso.split()[1] if subprocesso else '00'
                file_index_str = f"{index + 1:04d}"
                new_filename = f"PT-MNE-CICL-IC-1-{caixa_number}-{processo_number}"
                if subprocesso:
                    new_filename += f"-{subprocesso_number}"
                new_filename += f"_m{file_index_str}.jpg"
                old_file_path = os.path.join(dirpath, filename)
                new_file_path = os.path.join(dirpath, new_filename)

                if os.path.exists(new_file_path):
                    continue

                os.rename(old_file_path, new_file_path)
                print(f"Renamed {old_file_path} to {new_file_path}")

def process_folder(root_folder):
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = []
        for dirpath, dirnames, filenames in os.walk(root_folder):
            filenames.sort(key=extract_file_number)  # Ensure the files are processed in order
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if filename.lower().endswith('.tif') or filename.lower().endswith('.tiff'):
                    futures.append(executor.submit(process_image, file_path))
        for future in as_completed(futures):
            file_path, status = future.result()

def main():
    print("\n\t\t------ JPG's SCRIPT! ------\t\t")
    print("\n🚨This script will process all files in a folder🚨\n")

    root_folder = input("Please, input the root folder (default is './HD_fixed'): ") or './HD_fixed'
    action = input("Do you want to process, rename, or both? ").lower()

    if action not in ["process", "rename", "both"]:
        print("Invalid action. Please enter 'process', 'rename', or 'both'.")
        return

    print("Processing...")

    ## stopwatch
    start = time.time()

    if action in ["process", "both"]:
        process_folder(root_folder)

    if action in ["rename", "both"]:
        rename_files(root_folder)

    end = time.time()
    print(f"Operation completed in: {end - start} seconds")

if __name__ == "__main__":
    main()
