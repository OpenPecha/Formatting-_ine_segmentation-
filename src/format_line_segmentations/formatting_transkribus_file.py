import os
import shutil
from PIL import Image

ROOT_DIR = '../../data/transkribus_extracted_data'
XML_DEST_DIR = '../../data/transkribus_xml_folder'
IMAGES_DEST_DIR = '../../data/transkribus_images_folder'

def convert_tiff_to_jpg(src_path, dest_path):
    with Image.open(src_path) as img:
        img.convert('RGB').save(dest_path, 'JPEG')

def copy_files(xml_folder, folder_c_path, dest_xml_dir, dest_images_dir, prefix=''):
    xml_files = []
    image_files = []
    xml_file_names = {os.path.splitext(file)[0] for file in os.listdir(xml_folder) if file.lower().endswith('.xml')}
    image_file_names = {os.path.splitext(file)[0] for file in os.listdir(folder_c_path) if file.lower().endswith(('.tif', '.tiff', '.jpg', '.jpeg', '.png', '.gif'))}

    common_files = xml_file_names & image_file_names

    for file_name in common_files:
        xml_src = os.path.join(xml_folder, f"{file_name}.xml")
        xml_dest = os.path.join(dest_xml_dir, f"{prefix}_{file_name}.xml")
        shutil.copy2(xml_src, xml_dest)
        xml_files.append(xml_dest)

        image_file = next(file for file in os.listdir(folder_c_path) if os.path.splitext(file)[0] == file_name)
        image_src = os.path.join(folder_c_path, image_file)
        image_dest = os.path.join(dest_images_dir, f"{prefix}_{file_name}.jpg")
        
        if image_file.lower().endswith(('.tif', '.tiff')):
            convert_tiff_to_jpg(image_src, image_dest)
        else:
            shutil.copy2(image_src, image_dest)
        
        image_files.append(image_dest)

    return xml_files, image_files

def process_folder_C(folder_b_name, folder_c_path, dest_xml_dir, dest_images_dir, folder_c_name):
    xml_folder = os.path.join(folder_c_path, 'xml')
    
    if not os.path.exists(xml_folder):
        print(f"Skipping {folder_c_path} - Missing xml folder.")
    
    if os.path.exists(xml_folder):
        prefix = f"{folder_b_name}_{folder_c_name}"
        xml_files, image_files = copy_files(xml_folder, folder_c_path, dest_xml_dir, dest_images_dir, prefix=prefix)
        xml_count = len(xml_files)
        image_count = len(image_files)
        print(f"Folder {folder_c_path} - XML files: {xml_count}, Image files: {image_count}")
        if xml_count != image_count:
            print(f"WARNING: Folder {folder_c_path} has {xml_count} XML files and {image_count} image files.")
    else:
        print(f"Skipping {folder_c_path} - No xml folder found.")

def process_folder_B(folder_b_path, dest_xml_dir, dest_images_dir, folder_b_name):
    for folder_c in os.listdir(folder_b_path):
        folder_c_path = os.path.join(folder_b_path, folder_c)
        if os.path.isdir(folder_c_path):
            print(f"Processing {folder_c_path}...")
            process_folder_C(folder_b_name, folder_c_path, dest_xml_dir, dest_images_dir, folder_c)
        else:
            print(f"Skipping non-directory item: {folder_c_path}")

def main():
    if not os.path.exists(XML_DEST_DIR):
        os.makedirs(XML_DEST_DIR)
    if not os.path.exists(IMAGES_DEST_DIR):
        os.makedirs(IMAGES_DEST_DIR)
    folder_b_count = 0
    for folder_b in os.listdir(ROOT_DIR):
        folder_b_path = os.path.join(ROOT_DIR, folder_b)
        if os.path.isdir(folder_b_path):
            print(f"Processing {folder_b_path}...")
            process_folder_B(folder_b_path, XML_DEST_DIR, IMAGES_DEST_DIR, folder_b)
            folder_b_count += 1
            print(f"Processed {folder_b_count} directories.")
    print(f"Processed {folder_b_count} 'Folder B' directories.")

if __name__ == "__main__":
    main()
