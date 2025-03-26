import cairosvg
import os
# from PIL import Image
import pandas as pd
import xml.etree.ElementTree as ET
import re
from pathlib import Path

def find_kanji_unicode( xml_file, target_kanji ):
    """Search for a kanji element in the XML file and return its Unicode value."""
    # Define the namespace
    ns = {'kvg': 'http://kanjivg.tagaini.net'}

    try:
        # Parse the XML file
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Search for all g elements
        for g_element in root.findall(".//g", ns):
            # Get the kvg:element attribute using the full namespace
            element_attr = g_element.get('{http://kanjivg.tagaini.net}element')
            if element_attr == target_kanji:
                # Find the parent kanji element
                parent = g_element
                while parent is not None and parent.tag != 'kanji':
                    parent = parent.getparent() if hasattr(parent, 'getparent') else root.find(
                        ".//*[@id='{}']..".format(parent.get('id')))

                if parent is not None and parent.tag == 'kanji':
                    kanji_id = parent.get('id')
                    # Extract the unicode value using regex
                    match = re.search(r'kvg:kanji_([0-9a-f]+)', kanji_id)
                    if match:
                        return match.group(1)
        return None

    except ET.ParseError as e:
        print(f"Error parsing XML file: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def process_kanjidic2( xml_path, xml_file ):
    """ Process the KANJIDIC2 XML file to extract kanji and their definitions."""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        kanji_data = []
        count = 0

        for character in root.findall('.//character'):
            count += 1
            if count % 1000==0:
                print(count, " processed.")

            kanji = character.find('literal').text
            # Get the meaning elements (not their text content)
            meaning_elements = character.findall('.//meaning')

            # Filter for meanings without m_lang attribute (English meanings)
            english_meanings = [m.text for m in meaning_elements if m.get('m_lang') is None]

            unicode_value = find_kanji_unicode(xml_file, kanji)
            # print("unicode_value", unicode_value)

            if english_meanings and unicode_value:
                kanji_data.append({
                    'file_name': f"{unicode_value}.png",
                    'text': '; '.join(english_meanings)
                })

        return pd.DataFrame(kanji_data)

    except ET.ParseError as e:
        print(f"Error parsing XML file: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame()

def remove_stroke_numbers(svg_content):
    """Remove text elements that contain stroke numbers."""
    svg_content = re.sub(r'<text.*?</text>', '', svg_content, flags=re.DOTALL)
    return svg_content


def convert_svg_to_png( svg_path, output_path, size=(512, 512) ):
    """Convert SVG to PNG while removing stroke numbers."""
    try:
        # Read the SVG file
        with open(svg_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()

        # Remove stroke numbers
        modified_svg = remove_stroke_numbers(svg_content)

        # Create a temporary file for the modified SVG
        temp_svg_path = str(Path(output_path).parent / f"temp_{Path(svg_path).name}")

        with open(temp_svg_path, 'w', encoding='utf-8') as f:
            f.write(modified_svg)

        try:
            # Convert the modified SVG to PNG
            cairosvg.svg2png(
                url=temp_svg_path,
                write_to=output_path,
                output_width=size[0],
                output_height=size[1]
            )
        finally:
            # Clean up temporary file
            if os.path.exists(temp_svg_path):
                os.remove(temp_svg_path)

    except Exception as e:
        print(f"Error converting {svg_path} to PNG: {e}")

def prepare_dataset( kanjidic2_path, svg_font_dir, output_dir, xml_file):
    # Create output directories
    os.makedirs(os.path.join(output_dir, 'images2'), exist_ok=True)

    # Process KANJIDIC2
    df = process_kanjidic2(kanjidic2_path, xml_file)
    print("dataframe created.")

    # Convert SVGs to PNGs
    for idx, row in df.iterrows():
        unicode_value = row['file_name']
        print("unicode_value", unicode_value)

        svg_path = os.path.join(svg_font_dir, f"{unicode_value[:-4]}.svg")
        png_path = os.path.join(output_dir, 'images2', f"{unicode_value}")

        if os.path.exists(svg_path):
            print("converting...")
            convert_svg_to_png(svg_path, png_path)

    # Save metadata
    df.to_csv(os.path.join(output_dir, 'metadata.csv'), index=False)

if __name__ == "__main__":
    kanjidic2_path = "data/kanjidic2.xml"
    svg_font_dir = "kanjivg/kanji"
    output_dir = "data/kanjidic_dataset"
    xml_file = "data/kanjivg.xml"

    prepare_dataset(
        kanjidic2_path,
        svg_font_dir,
        output_dir,
        xml_file
    )