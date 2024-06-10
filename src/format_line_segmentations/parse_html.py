'''from bs4 import BeautifulSoup
import json
import uuid

try:
        with open('/Users/ogyenthoga/Desktop/Work/Formatting_line_segmentation/data/line_segmentation_images/google_book_html/00000001.html',encoding="utf-8") as file:
            
            soup = BeautifulSoup(file, "html.parser")
            ocr_data = []
            for line in soup.find_all("span", {"class": "ocr_line"}):
                bbox = line["title"].split(";")[0].split()[1:]  # Extract bounding box
                bbox = [int(x) for x in bbox]
                text = line.text
                # Extract OCR confidence if available
        
                ocr_data.append({"bbox": bbox, "text": text})
        print(ocr_data)
except Exception as e:
        print(f"Error processing {'data/line_segmentation_images/google_book_html/00000001.html'}: {e}")
        print("NONE")

# Sample image metadata
image_metadata = {
    "id": "I2PD179890017.jpg_2000x700.jpg",
    "image": "https://s3.amazonaws.com/image-processing.openpecha/Works/fe/W1AC364/images-web/W1AC364-I2PD17989/I2PD179890017.jpg_2000x700.jpg?AWSAccessKeyId=AKIAWEXEWJ7GDFYE3KNU&Signature=h9WOkAQrS3gm%2FSU3rvO0HDsK4Nc%3D&Expires=1720527794",
    "width": 479,
    "height": 700
}

# Convert OCR data to spans
spans = []
#color_cycle = ["yellow", "cyan", "magenta", "springgreen", "tomato", "deepskyblue", "orange", "hotpink", "aquamarine", "gold", "peachpuff", "greenyellow", "tan", "gainsboro"]

for i, item in enumerate(ocr_data):
    bbox = item['bbox']
    text = item['text']
    span = {
        "id": str(uuid.uuid4()),
        "label": "Line",
        "color": "yellow",
        "x": bbox[0],
        "y": bbox[1],
        "height": bbox[3] - bbox[1],
        "width": bbox[2] - bbox[0],
        "center": [(bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2],
        "type": "rect",
        "points": [[bbox[0], bbox[1]], [bbox[0], bbox[3]], [bbox[2], bbox[3]], [bbox[2], bbox[1]]]
    }
    spans.append(span)

# Combine image metadata and spans
combined_output = {
    "id": image_metadata["id"],
    "image": image_metadata["image"],
    "spans": spans,
    "_input_hash": -548459323,
    "_task_hash": -1621366528,
    "_view_id": "image_manual",
    "width": image_metadata["width"],
    "height": image_metadata["height"],
    "answer": "accept"
}

# Output the result in JSONL format
jsonl_output = json.dumps(combined_output, ensure_ascii=False)
print(jsonl_output)

# Write the JSONL to a file
with open('output.jsonl', 'w', encoding='utf-8') as file:
    file.write(jsonl_output + '\n')
'''

import os
import json
import uuid
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime


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
#save ocr_data
def extract_metadata_from_html(parsed_data, image_file):
    metadata = {}
    # Extract ID from the image filename
    metadata['id'] = os.path.splitext(os.path.basename(image_file))[0] + ".jpg_2000x700.jpg"
    metadata['image'] = image_file
    for item in parsed_data:
        if isinstance(item, dict):
            text = item.get('text', '')
            if 'width' in text.lower():
                metadata['width'] = text.split(':')[-1].strip()
            elif 'height' in text.lower():
                metadata['height'] = text.split(':')[-1].strip()

    return metadata


def convert_to_jsonl(ocr_data, image_metadata):
    spans = []

    for i, item in enumerate(ocr_data):
        bbox = item['bbox']
        text = item['text']
        span = {
            "id": str(uuid.uuid4()),
          #  "x": bbox[0],
          #  "y": bbox[1],
            "height": bbox[3] - bbox[1],
            "width": bbox[2] - bbox[0],
            "center": [(bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2],
            "points": [[bbox[0], bbox[1]], [bbox[0], bbox[3]], [bbox[2], bbox[3]], [bbox[2], bbox[1]]]
        }
        spans.append(span)

    combined_output = {
        "id": image_metadata["id"],
        "image": image_metadata["image"],
        "spans": spans,
        "_input_hash": -548459323,
        "_task_hash": -1621366528,
        "_view_id": "image_manual",
       # "width": image_metadata["width"],
       # "height": image_metadata["height"],
        "answer": "accept"
    }
    print(combined_output)

    return json.dumps(combined_output, ensure_ascii=False)

def convert_to_xml(ocr_data, image_metadata):
    root = ET.Element("PcGts", {
        "xmlns": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15",
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xsi:schemaLocation": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15 http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15/pagecontent.xsd"
    })

    metadata = ET.SubElement(root, "Metadata")
    creator = ET.SubElement(metadata, "Creator")
    creator.text = "Google Books"
    now = datetime.now()
    formatted_now = now.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
    formatted_now = formatted_now[:-3] + "+00:00"
    created = ET.SubElement(metadata, "Created")
    created.text = "2024-06-10T11:08:30.326+00:00"
    last_changed = ET.SubElement(metadata, "LastChanged")
    last_changed.text = formatted_now

    page = ET.SubElement(root, "Page", {
        "imageFilename": image_metadata["id"],
       
    })

    reading_order = ET.SubElement(page, "ReadingOrder")
    ordered_group = ET.SubElement(reading_order, "OrderedGroup", {"id": "1234_0", "caption": "Regions reading order"})
    region_ref_indexed = ET.SubElement(ordered_group, "RegionRefIndexed", {"index": "0", "regionRef": "region_main"})

    text_region = ET.SubElement(page, "TextRegion", {"id": "region_main", "custom": "readingOrder {index:0;} structure {type:paragraph;}"})
    coords = ET.SubElement(text_region, "Coords", {"points": "79,24 79,336 1893,336 1893,24"})

    for i, item in enumerate(ocr_data):
        bbox = item['bbox']
        text_line = ET.SubElement(text_region, "TextLine", {
            "id": str(uuid.uuid4()),
            "custom": f"readingOrder {{index: {i};}}"
        })
        line_coords = ET.SubElement(text_line, "Coords", {
            "points": f"{bbox[0]},{bbox[1]} {bbox[0]},{bbox[3]} {bbox[2]},{bbox[3]} {bbox[2]},{bbox[1]}"
        })
        text_equiv = ET.SubElement(text_line, "TextEquiv")
        unicode_text = ET.SubElement(text_equiv, "Unicode")
        unicode_text.text = item['text']

    return root

def prettify_xml(elem):
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def main():
    input_directory = '/Users/ogyenthoga/Desktop/Work/Formatting_line_segmentation/data/line_segmentation_images/google_book_html/'
    image_directory = '/Users/ogyenthoga/Desktop/Work/Formatting_line_segmentation/data/line_segmentation_images/google_book_images/'
    output_file = 'output.jsonl'
    output_directory = '/Users/ogyenthoga/Desktop/Work/Formatting_line_segmentation/data/line_segmentation_output_format/xml_output/'
    
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    image_files = {os.path.splitext(f)[0]: os.path.join(image_directory, f) for f in os.listdir(image_directory) if f.endswith(".jpg")}
    
    with open(output_file, 'w', encoding='utf-8') as output:
        count =0
        countxml = 0
        for filename in os.listdir(input_directory):
            if filename.endswith(".html"):
                file_id = os.path.splitext(filename)[0] 
                if file_id in image_files:
                    file_path = os.path.join(input_directory, filename)
                    image_file = image_files[file_id]

                    
                    ocr_data = process_html_file(file_path)
                    #print(ocr_data)
                    image_metadata = extract_metadata_from_html(ocr_data, image_file)
                   # print(image_metadata)
                    
                    if ocr_data and image_metadata:
                        jsonl_output = convert_to_jsonl(ocr_data, image_metadata)
                        output.write(jsonl_output + '\n')
                        xml_root = convert_to_xml(ocr_data, image_metadata)
                        xml_output = prettify_xml(xml_root)
                        output_file_path = os.path.join(output_directory, f"{file_id}.xml")
                        with open(output_file_path, 'w', encoding='utf-8') as output_file:
                           output_file.write(xml_output)
                        print(f"Processed and wrote XML for {filename}")
                        count = count+1
                       # print(f"Processed and wrote data for {filename}")
        print("Count XML", countxml)            
        print(count)

       

if __name__ == "__main__":
    main()
