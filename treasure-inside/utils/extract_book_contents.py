import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import os
import re
import logging

# Configure logging
logging.basicConfig(
    filename='extraction.log',
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

# Specify the path to Tesseract if not in PATH
# Uncomment and set the path if necessary (Example for Windows)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def create_output_directories(base_dir, chapter_name):
    """
    Create directories for each chapter's text and images.
    """
    chapter_dir = os.path.join(base_dir, chapter_name)
    text_dir = os.path.join(chapter_dir, "Text")
    images_dir = os.path.join(chapter_dir, "Images")
    
    os.makedirs(text_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)
    
    return text_dir, images_dir

def extract_text_from_page(page):
    """
    Extract text from a single PDF page using OCR.
    """
    try:
        # Render page to an image
        pix = page.get_pixmap()
        img_data = pix.pil_tobytes(format="PNG")
        image = Image.open(io.BytesIO(img_data))
        
        # Preprocess the image for better OCR accuracy
        image = image.convert("L")  # Convert to grayscale
        image = image.point(lambda x: 0 if x < 140 else 255, '1')  # Binarize the image
        
        # Perform OCR using pytesseract
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        logging.error(f"OCR failed for page {page.number + 1}: {e}")
        return ""

def extract_images_from_page(page, images_dir, chapter_name, page_number):
    """
    Extract all images from a single PDF page and save them.
    """
    try:
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = pdf.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            # Handle cases where image_ext might not be standard
            if image_ext.lower() not in ['png', 'jpeg', 'jpg', 'tiff', 'bmp', 'gif']:
                image_ext = 'png'  # Default to PNG if unknown
            
            image_name = f"{chapter_name}_page{page_number +1}_image{img_index +1}.{image_ext}"
            image_path = os.path.join(images_dir, image_name)
            with open(image_path, "wb") as img_file:
                img_file.write(image_bytes)
    except Exception as e:
        logging.error(f"Image extraction failed for {chapter_name} page {page_number +1}: {e}")

def sanitize_filename(name):
    """
    Sanitize the chapter name to create valid directory names.
    """
    return re.sub(r'[\\/*?:"<>|]', "_", name)

# Path to your "Book" directory
book_dir = "/Users/markconway/Projects/Treasure Inside/Book"

# Output directory inside "Book"
output_base_dir = os.path.join(book_dir, "Extracted_Content")
os.makedirs(output_base_dir, exist_ok=True)

# Regular expression to extract chapter name from filename
chapter_regex = re.compile(r'TTI Chapter ([\w\s]+) Pages (\d+)-(\d+)\.pdf', re.IGNORECASE)

# Iterate through each PDF in the "Book" directory
for filename in os.listdir(book_dir):
    if filename.lower().endswith('.pdf'):
        filepath = os.path.join(book_dir, filename)
        
        # Extract chapter details using regex
        match = chapter_regex.match(filename)
        if not match:
            logging.warning(f"Filename '{filename}' does not match the expected pattern. Skipping.")
            continue
        
        chapter_identifier = match.group(1).strip()
        start_page = int(match.group(2))
        end_page = int(match.group(3))
        
        chapter_name = f"TTI Chapter {chapter_identifier}"
        safe_chapter_name = sanitize_filename(chapter_name)
        
        print(f"Processing {chapter_name}: Pages {start_page} to {end_page}")
        
        # Create directories for the chapter
        text_dir, images_dir = create_output_directories(output_base_dir, safe_chapter_name)
        
        chapter_text = ""
        
        # Open the PDF
        try:
            pdf = fitz.open(filepath)
        except Exception as e:
            logging.error(f"Failed to open PDF '{filename}': {e}")
            continue
        
        # Iterate through the specified pages
        for page_num in range(start_page -1, end_page):  # fitz is 0-indexed
            try:
                page = pdf.load_page(page_num)
                
                # Extract text via OCR
                text = extract_text_from_page(page)
                chapter_text += f"--- Page {page_num +1} ---\n{text}\n"
                
                # Extract images
                extract_images_from_page(page, images_dir, safe_chapter_name, page_num)
                
            except Exception as e:
                logging.error(f"Failed to process {chapter_name} page {page_num +1}: {e}")
        
        # Save the extracted text to a file
        text_file_path = os.path.join(text_dir, f"{safe_chapter_name}.txt")
        try:
            with open(text_file_path, "w", encoding="utf-8") as text_file:
                text_file.write(chapter_text)
        except Exception as e:
            logging.error(f"Failed to write text file for {chapter_name}: {e}")
        
        print(f"Finished processing {chapter_name}")

print("Extraction complete!")
