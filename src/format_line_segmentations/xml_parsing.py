import xml.etree.ElementTree as ET
import os

#Process an XML file to extract OCR data.
def process_xml_file(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        ocr_data = []
        ns = {'ns': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}  # XML namespace
        for line in root.findall('.//ns:TextLine', ns):
            coords = line.find('ns:Coords', ns).get('points')
            bbox = [int(point) for point in coords.replace(',', ' ').split()]
            text = line.find('.//ns:Unicode', ns).text if line.find('.//ns:Unicode', ns) is not None else ''
            ocr_data.append({"bbox": bbox, "text": text})
        return ocr_data
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return []

#Extract metadata from parsed OCR data and the image file.  
def extract_metadata_from_xml(ocr_data, image_file):
    metadata = {}
    metadata['id'] =os.path.splitext(os.path.basename(image_file))[0] + ".jpg"
    metadata['image'] = image_file
    return metadata
