import os
import json
import uuid
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from html_parsing import process_html_file, extract_metadata_from_html
from xml_parsing import process_xml_file, extract_metadata_from_xml

#Convert OCR data and image metadata to a JSONL format.
def convert_to_jsonl(ocr_data, image_metadata):
    spans = []
    for i, item in enumerate(ocr_data):
        bbox = item['bbox']
        text = item['text']
        span = {
            "id": str(uuid.uuid4()),
            "height": bbox[3] - bbox[1],
            "width": bbox[2] - bbox[0],
            "center": [(bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2],
            "points": [[bbox[0], bbox[1]], [bbox[0], bbox[3]], [bbox[2], bbox[3]], [bbox[2], bbox[1]]]
        }
        spans.append(span)
    combined_output = {
        "id": image_metadata["id"],
        "image": image_metadata["image"],
        "spans": spans
    }
    return json.dumps(combined_output, ensure_ascii=False)

#Convert OCR data and image metadata to an XML format.
def convert_to_xml(ocr_data, image_metadata, creator_name):
    root = ET.Element("PcGts", {
        "xmlns": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15",
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xsi:schemaLocation": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15 http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15/pagecontent.xsd"
    })
    metadata = ET.SubElement(root, "Metadata")
    creator = ET.SubElement(metadata, "Creator")
    creator.text = creator_name
    page = ET.SubElement(root, "Page", {
        "imageFilename": image_metadata["id"],
    })
    reading_order = ET.SubElement(page, "ReadingOrder")
    ordered_group = ET.SubElement(reading_order, "OrderedGroup", {"id": "1234_0", "caption": "Regions reading order"})
    region_ref_indexed = ET.SubElement(ordered_group, "RegionRefIndexed", {"index": "0", "regionRef": "region_main"})
    text_region = ET.SubElement(page, "TextRegion", {"id": "region_main",
                                                     "custom": "readingOrder {index:0;} structure {type:paragraph;}"})
    coords = ET.SubElement(text_region, "Coords", {"points": "79,24 79,336 1893,336 1893,24"})
    for i, item in enumerate(ocr_data):
        bbox = item['bbox']
        text_line = ET.SubElement(text_region, "TextLine", {
            "id": str(i),
            "custom": f"readingOrder {{index: {i};}}"
        })
        line_coords = ET.SubElement(text_line, "Coords", {
            "points": f"{bbox[0]},{bbox[1]} {bbox[0]},{bbox[3]} {bbox[2]},{bbox[3]} {bbox[2]},{bbox[1]}"
        })
    return root

#Convert an XML element tree to a pretty-printed string.
def prettify_xml(elem):
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

# Create directories if they do not exist.
def create_directories(paths):
    for output_type in paths.values():
        output_dirs = output_type.get("output_xml", [])
        if isinstance(output_dirs, str):
            output_dirs = [output_dirs]
        for output_dir in output_dirs:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

# Process Google Books Data (HTML) files
def process_google_books_html_files(paths):
    image_files_html = {os.path.splitext(f)[0]: os.path.join(paths["google_books"]["input_images"], f)
                        for f in os.listdir(paths["google_books"]["input_images"]) if f.lower().endswith(".jpg")}
    with open(paths["google_books"]["output_jsonl"], 'w', encoding='utf-8') as output_0:
        for filename in os.listdir(paths["google_books"]["input_html"]):
            if filename.endswith(".html"):
                file_id = os.path.splitext(filename)[0]
                if file_id in image_files_html:
                    file_path = os.path.join(paths["google_books"]["input_html"], filename)
                    image_file_0 = image_files_html[file_id]
                    ocr_data = process_html_file(file_path)
                    image_metadata_0 = extract_metadata_from_html(ocr_data, image_file_0)
                    if ocr_data and image_metadata_0:
                        jsonl_output = convert_to_jsonl(ocr_data, image_metadata_0)
                        output_0 .write(jsonl_output + '\n')
                        xml_root = convert_to_xml(ocr_data, image_metadata_0, "Google Books")
                        xml_output = prettify_xml(xml_root)
                        output_file_path = os.path.join(paths["google_books"]["output_xml"], f"{file_id}.xml")
                        with open(output_file_path, 'w', encoding='utf-8') as output_file_google_books:
                            output_file_google_books.write(xml_output)

# Process XML files for Transkribus and HTR team data
def process_xml_data(paths):
    for dataset, dataset_paths in paths.items():
        if dataset == "transkribus":
            image_files = {os.path.splitext(f)[0]: os.path.join(dataset_paths["input_images"], f)
                           for f in os.listdir(dataset_paths["input_images"]) if f.lower().endswith(".jpg")}
        elif dataset == "aws":
            image_files = {os.path.splitext(f)[0]: os.path.join(dataset_paths["input_images"], f)
                           for f in os.listdir(dataset_paths["input_images"]) if f.lower().endswith(".jpg")}
        else:
            continue
        with open(dataset_paths["output_jsonl"], 'w', encoding='utf-8') as output_jsonl:
            for filename in os.listdir(dataset_paths["input_xml"]):
                if filename.endswith(".xml"):
                    file_id = os.path.splitext(filename)[0]
                    image_file = image_files.get(file_id)
                    if image_file:
                        file_path = os.path.join(dataset_paths["input_xml"], filename)
                        ocr_data = process_xml_file(file_path)
                        image_metadata = extract_metadata_from_xml(ocr_data, image_file)
                        if ocr_data and image_metadata:
                            jsonl_output = convert_to_jsonl(ocr_data, image_metadata)
                            output_jsonl.write(jsonl_output + '\n')
                            xml_root = convert_to_xml(ocr_data, image_metadata, dataset.capitalize())
                            xml_output = prettify_xml(xml_root)
                            output_file_path = os.path.join(dataset_paths["output_xml"], f"{file_id}.xml")
                            with open(output_file_path, 'w', encoding='utf-8') as output_xml:
                                output_xml.write(xml_output)

# Main function to process HTML and XML files and convert them to JSONL and XML formats.
def main():
    base_path = '../../data/line_segmentation_inputs/'
    output_base_path = '../../data/line_segmentation_output_format/'
    '''    paths = {
        "aws": {
            "input_xml": f"{base_path}htr_teams/htr_team_xml_folder",
            "input_images": f"{base_path}htr_teams/htr_team_images_folder/",
            "output_jsonl": f"{output_base_path}htr_team_data.jsonl",
            "output_xml": f"{output_base_path}htr_teams_data_xml/"
        },
        "google_books": {
            "input_html": f"{base_path}google_books/google_books_html_folder/",
            "input_images": f"{base_path}google_books/google_books_images_folder/",
            "output_jsonl": f"{output_base_path}google_books_data.jsonl",
            "output_xml": f"{output_base_path}google_books_data_xml/"
        }, 
        "transkribus": {
            "input_xml_base": f"{base_path}transkribus/",
            "input_images": f"{base_path}transkribus_images_folder/",
            "output_jsonl": f"{output_base_path}transkribus_data.jsonl",
            "output_xml": f"{output_base_path}transkribus_data_xml/"
        }
    } '''  

    paths = {
        "aws": {
            "input_xml": f"{base_path}htr_teams/htr_team_xml_folder",
            "input_images": f"{base_path}htr_teams/htr_team_images_folder/",
            "output_jsonl": f"{output_base_path}htr_team_data.jsonl",
            "output_xml": f"{output_base_path}htr_teams_data_xml/"
        }
    }
    create_directories(paths)
    # Process Html files for Google Books data
   # process_google_books_html_files(paths)
    # Process XML files for Tanskribus and HTR team data
    process_xml_data(paths)
      
if __name__ == "__main__":
    main()
