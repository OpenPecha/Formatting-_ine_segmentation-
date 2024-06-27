import os
import shutil
from PIL import Image

ROOT_DIR = '/Users/ogyenthoga/Desktop/Work/Formatting_line_segmentation/data/htr_team_data'
XML_DEST_DIR = '/Users/ogyenthoga/Desktop/Work/Formatting_line_segmentation/data/htr_teams/htr_team_xml_folder'
IMAGES_DEST_DIR = '/Users/ogyenthoga/Desktop/Work/Formatting_line_segmentation/data/htr_teams/htr_team_images_folder'

def convert_to_jpg(src_path, dest_path):
    with Image.open(src_path) as img:
        img.convert('RGB').save(dest_path, 'JPEG')

def copy_files(src_dir, dest_xml_dir, dest_images_dir, prefix=''):
    xml_files = []
    image_files = []
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.lower().endswith('.xml'):
                dest_path = os.path.join(dest_xml_dir, f"{prefix}_{file}")
                shutil.copy2(os.path.join(root, file), dest_path)
                xml_files.append(dest_path)
            elif file.lower().endswith(('.tif', '.tiff', '.jpg', '.jpeg', '.png', '.gif')):
                dest_path = os.path.join(dest_images_dir, f"{prefix}_{os.path.splitext(file)[0]}.jpg")
                convert_to_jpg(os.path.join(root, file), dest_path)
                image_files.append(dest_path)
    return xml_files, image_files

def process_folder_B(folder_b_path, dest_xml_dir, dest_images_dir):
    folder_b_name = os.path.basename(folder_b_path)
    xml_files, image_files = copy_files(folder_b_path, dest_xml_dir, dest_images_dir, prefix=folder_b_name)
    xml_count = len(xml_files)
    image_count = len(image_files)
    print(f"Folder {folder_b_path} - XML files: {xml_count}, Image files: {image_count}")
    if xml_count != image_count:
        print(f"WARNING: Folder {folder_b_path} has {xml_count} XML files and {image_count} image files.")

def main():
    if not os.path.exists(XML_DEST_DIR):
        os.makedirs(XML_DEST_DIR)
    if not os.path.exists(IMAGES_DEST_DIR):
        os.makedirs(IMAGES_DEST_DIR)

    folder_b_count = 0
    for folder_b in os.listdir(ROOT_DIR):
        folder_b_path = os.path.join(ROOT_DIR, folder_b)
        if os.path.isdir(folder_b_path):
            process_folder_B(folder_b_path, XML_DEST_DIR, IMAGES_DEST_DIR)
            folder_b_count += 1
            print(f"Processed {folder_b_count} Folder B directories.")
    print(f"Total processed 'Folder B' directories: {folder_b_count}")

if __name__ == "__main__":
    main()
