import os
import shutil
from PIL import Image

ROOT_DIR = '../../data/extracted_data'
HTML_DEST_DIR = '../../data/google_books_html_folder'
IMAGES_DEST_DIR = '../../data/google_books_images_folder'

def convert_tiff_to_jpg(src_path, dest_path):
    with Image.open(src_path) as img:
        img.convert('RGB').save(dest_path, 'JPEG')

def copy_files(src_dir, dest_html_dir, dest_images_dir, prefix=''):
    html_files = []
    image_files = []
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.lower().endswith('.html'):
                dest_path = os.path.join(dest_html_dir, f"{prefix}_{file}")
                shutil.copy2(os.path.join(root, file), dest_path)
                html_files.append(dest_path)
            elif file.lower().endswith('.tif') or file.lower().endswith('.tiff'):
                dest_path = os.path.join(dest_images_dir, f"{prefix}_{os.path.splitext(file)[0]}.jpg")
                convert_tiff_to_jpg(os.path.join(root, file), dest_path)
                image_files.append(dest_path)
            elif file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                dest_path = os.path.join(dest_images_dir, f"{prefix}_{file}")
                shutil.copy2(os.path.join(root, file), dest_path)
                image_files.append(dest_path)

    return html_files, image_files

def process_folder_B(folder_b_path, dest_html_dir, dest_images_dir):
    for folder_c in os.listdir(folder_b_path):
        folder_c_path = os.path.join(folder_b_path, folder_c)
        if os.path.isdir(folder_c_path):
            html_folder = os.path.join(folder_c_path, 'html')
            images_folder = os.path.join(folder_c_path, 'images')
            if os.path.exists(html_folder) and os.path.exists(images_folder):
                html_files, image_files = copy_files(folder_c_path, dest_html_dir, dest_images_dir, prefix=os.path.basename(folder_c_path))
                html_count = len(html_files)
                image_count = len(image_files)
                print(f"Folder {folder_c_path} - HTML files: {html_count}, Image files: {image_count}")
                if html_count != image_count:
                    print(f"WARNING: Folder {folder_c_path} has {html_count} HTML files and {image_count} image files.")
            else:
                print(f"Skipping {folder_c_path} - Missing html or images folder.")
        else:
            print(f"Skipping non-directory item: {folder_c_path}")

def main():
    if not os.path.exists(HTML_DEST_DIR):
        os.makedirs(HTML_DEST_DIR)
    if not os.path.exists(IMAGES_DEST_DIR):
        os.makedirs(IMAGES_DEST_DIR)
    folder_b_count = 0
    for folder_b in os.listdir(ROOT_DIR):
        folder_b_path = os.path.join(ROOT_DIR, folder_b)
        if os.path.isdir(folder_b_path):
            process_folder_B(folder_b_path, HTML_DEST_DIR, IMAGES_DEST_DIR)
            folder_b_count += 1
            print(folder_b_count)
    print(f"Processed {folder_b_count} 'foldername B' directories.")

if __name__ == "__main__":
    main()
