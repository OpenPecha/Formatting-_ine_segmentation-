from bs4 import BeautifulSoup
import os

#Process an HTML file to extract OCR data.
def process_html_file(file_path):
    try:
        with open(file_path, encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")
            ocr_data = []
            for line in soup.find_all("span", {"class": "ocr_line"}):
                bbox = line["title"].split(";")[0].split()[1:]  # Extract bounding box
                bbox = [int(x) for x in bbox]
                text = line.text
                ocr_data.append({"bbox": bbox, "text": text})
        return ocr_data
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return []

#Extract metadata from parsed OCR data and the image file.
def extract_metadata_from_html(parsed_data, image_file):
    metadata = {}
    # Extract ID from the image filename
    metadata['id'] = os.path.splitext(os.path.basename(image_file))[0] + ".jpg_2000x700.jpg"
    metadata['image'] = image_file
    return metadata
