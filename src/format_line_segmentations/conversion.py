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
        "spans": spans,
        "_input_hash": -548459323,
        "_task_hash": -1621366528,
        "_view_id": "image_manual",
        "answer": "accept"
    }
    return json.dumps(combined_output, ensure_ascii=False)

#Convert OCR data and image metadata to an XML format.
def convert_to_xml(ocr_data, image_metadata, creator_name, created_time):
    root = ET.Element("PcGts", {
        "xmlns": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15",
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xsi:schemaLocation": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15 http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15/pagecontent.xsd"
    })
    metadata = ET.SubElement(root, "Metadata")
    creator = ET.SubElement(metadata, "Creator")
    creator.text = creator_name
    created = ET.SubElement(metadata, "Created")
    created.text = created_time
    now_last_changed = datetime.now()
    formatted_now_last_changed = now_last_changed.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
    formatted_now_last_changed = formatted_now_last_changed[:-3] + "+00:00"
    last_changed = ET.SubElement(metadata, "LastChanged")
    last_changed.text = formatted_now_last_changed
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
            "id": str(uuid.uuid4()),
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

# Main function to process HTML and XML files and convert them to JSONL and XML formats.
def main():
    input_directory_html = '/Users/ogyenthoga/Desktop/Work/Formatting_line_segmentation/data/line_segmentation_images/google_book_html/'
    input_directory_xml = '/Users/ogyenthoga/Desktop/Work/Formatting_line_segmentation/data/line_segmentation_images/Correction-2/'
    image_directory = '/Users/ogyenthoga/Desktop/Work/Formatting_line_segmentation/data/line_segmentation_images/google_book_images/'
    output_file_html = '/Users/ogyenthoga/Desktop/Work/Formatting_line_segmentation/data/line_segmentation_output_format/google_books_data.jsonl'
    output_file_xml = '/Users/ogyenthoga/Desktop/Work/Formatting_line_segmentation/data/line_segmentation_output_format/htr_team_data.jsonl'
    output_directory_html = '/Users/ogyenthoga/Desktop/Work/Formatting_line_segmentation/data/line_segmentation_output_format/google_books_data_xml/'
    output_directory_xml = '/Users/ogyenthoga/Desktop/Work/Formatting_line_segmentation/data/line_segmentation_output_format/htr_teams_data_xml/'
    if not os.path.exists(output_directory_html):
        os.makedirs(output_directory_html)
    if not os.path.exists(output_directory_xml):
        os.makedirs(output_directory_xml)
    image_files_html = {os.path.splitext(f)[0]: os.path.join(image_directory, f)
                        for f in os.listdir(image_directory) if f.lower().endswith(".jpg")}
    image_files_xml = {os.path.splitext(f)[0]: os.path.join(input_directory_xml, f)
                       for f in os.listdir(input_directory_xml) if f.lower().endswith(".jpg")}
    # Process HTML files
    with open(output_file_html, 'w', encoding='utf-8') as output_0:
        for filename in os.listdir(input_directory_html):
            if filename.endswith(".html"):
                file_id = os.path.splitext(filename)[0]
                if file_id in image_files_html:
                    file_path = os.path.join(input_directory_html, filename)
                    image_file_0 = image_files_html[file_id]
                    ocr_data = process_html_file(file_path)
                    image_metadata_0 = extract_metadata_from_html(ocr_data, image_file_0)
                    if ocr_data and image_metadata_0:
                        jsonl_output = convert_to_jsonl(ocr_data, image_metadata_0)
                        output_0 .write(jsonl_output + '\n')
                        xml_root = convert_to_xml(ocr_data, image_metadata_0, "Google Books",
                                                  "2024-06-10T11:08:30.326+00:00")
                        xml_output = prettify_xml(xml_root)
                        output_file_path = os.path.join(output_directory_html, f"{file_id}.xml")
                        with open(output_file_path, 'w', encoding='utf-8') as output_file_html:
                            output_file_html.write(xml_output)
    # Process XML files
    with open(output_file_xml, 'w', encoding='utf-8') as output_1:
        for filename in os.listdir(input_directory_xml):
            if filename.endswith(".xml"):
                file_id = os.path.splitext(filename)[0]
                image_file_1 = image_files_xml.get(file_id)
                if image_file_1:
                    file_path = os.path.join(input_directory_xml, filename)
                    ocr_data = process_xml_file(file_path)
                    image_metadata_1 = extract_metadata_from_xml(ocr_data, image_file_1)
                    if image_metadata_1:
                        jsonl_output = convert_to_jsonl(ocr_data, image_metadata_1)
                        output_1.write(jsonl_output + '\n')
                        xml_root = convert_to_xml(ocr_data, image_metadata_1, "AWS Data",
                                                  "2024-06-10T11:08:30.326+00:00")
                        xml_output = prettify_xml(xml_root)
                        output_file_path = os.path.join(output_directory_xml, f"{file_id}.xml")
                        with open(output_file_path, 'w', encoding='utf-8') as output_file_xml:
                            output_file_xml.write(xml_output)


if __name__ == "__main__":
    main()
