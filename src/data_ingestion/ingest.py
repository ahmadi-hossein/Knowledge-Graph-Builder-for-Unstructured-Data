import os
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader # PdfReader is the correct class name
import docx
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import io # Needed for handling file objects

# --- Functions modified to accept file-like objects ---

def read_pdf(file_object, filename="Unknown"):
    """Extract text from PDF file object"""
    try:
        print(f"Reading PDF from object: {filename}") # Debugging
        text = ""
        # PyPDF2 works directly with file-like objects
        pdf_reader = PdfReader(file_object)
        print(f"Number of pages found: {len(pdf_reader.pages)}") # Debug info
        for i, page in enumerate(pdf_reader.pages):
            try:
                page_text = page.extract_text()
                if page_text: # Check if text extraction was successful for the page
                    text += page_text + "\n" # Add newline between pages
                else:
                    print(f"Warning: No text extracted from page {i+1} of {filename}")
            except Exception as page_e:
                print(f"Error extracting text from page {i+1} of {filename}: {page_e}")
        # Trim leading/trailing whitespace that might accumulate
        text = text.strip()
        if not text:
            print(f"Warning: No text could be extracted from PDF {filename}.")
        else:
            print(f"Extracted PDF Text from {filename} (First 500 chars): {text[:500]}")
        return text
    except Exception as e:
        print(f"Error while reading PDF object {filename}: {e}")
        # Optionally re-raise or handle specific exceptions like PasswordRequiredError
        if "PasswordRequiredError" in str(e):
             print(f"PDF file {filename} is password protected.")
             # You might want to return a specific message or raise it
             return f"Error: PDF file {filename} is password protected."
        return None

def read_docx(file_object, filename="Unknown"):
    """Extract text from DOCX file object"""
    try:
        print(f"Reading DOCX from object: {filename}") # Debugging
        # python-docx works directly with file-like objects
        doc = docx.Document(file_object)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        text = text.strip()
        if not text:
            print(f"Warning: No text could be extracted from DOCX {filename}.")
        else:
            print(f"Extracted DOCX Text from {filename} (First 500 chars): {text[:500]}")
        return text
    except Exception as e:
        # Catch specific errors if needed, e.g., PackageNotFoundError
        print(f"Error while reading DOCX object {filename}: {e}")
        return None

def read_txt(file_object, filename="Unknown"):
    """Extract text from TXT file object"""
    try:
        print(f"Reading TXT from object: {filename}") # Debugging
        # Read the bytes and decode, trying multiple encodings if necessary
        content_bytes = file_object.read()
        try:
            text = content_bytes.decode('utf-8')
        except UnicodeDecodeError:
            print(f"Warning: UTF-8 decoding failed for {filename}. Trying 'latin-1'.")
            try:
                text = content_bytes.decode('latin-1') # Common fallback
            except UnicodeDecodeError:
                 print(f"Error: Could not decode {filename} with UTF-8 or latin-1.")
                 return None # Give up if common encodings fail
        text = text.strip()
        if not text:
             print(f"Warning: No text could be extracted from TXT {filename} (possibly empty).")
        else:
            print(f"Extracted TXT Text from {filename} (First 500 chars): {text[:500]}")
        return text
    except Exception as e:
        print(f"Error while reading TXT object {filename}: {e}")
        return None

# --- New function to handle Streamlit's UploadedFile ---

def process_uploaded_file(uploaded_file):
    """Process Streamlit UploadedFile object based on its name's extension"""
    file_name = uploaded_file.name
    _, extension = os.path.splitext(file_name)
    print(f"Processing uploaded file: {file_name} with extension {extension}") # Debugging
    try:
        # Use BytesIO to wrap the bytes buffer if needed by a library,
        # but many libraries (like PdfReader, docx.Document) handle the file-like object directly.
        # file_object = io.BytesIO(uploaded_file.getvalue()) # Use getvalue() for bytes
        # Pass the uploaded_file object directly, as it's already file-like
        file_object = uploaded_file

        if extension.lower() == '.pdf':
            return read_pdf(file_object, filename=file_name)
        elif extension.lower() == '.docx':
            return read_docx(file_object, filename=file_name)
        elif extension.lower() == '.txt':
            return read_txt(file_object, filename=file_name)
        else:
            print(f"Unsupported file type: {extension}")
            # Return an error message to be displayed in Streamlit
            return f"Error: Unsupported file type '{extension}' for file '{file_name}'."
    except Exception as e:
        print(f"Error while processing uploaded file {file_name}: {e}")
        return f"Error processing file {file_name}: {e}" # Return error message

# --- Original file processing function (optional, commented out if unused) ---
# def process_file(file_path):
#     """Process file based on extension (Original version using path)"""
#     _, extension = os.path.splitext(file_path)
#     try:
#         # This version requires opening the file from path
#         if extension.lower() == '.pdf':
#             with open(file_path, 'rb') as f:
#                 return read_pdf(f, filename=os.path.basename(file_path))
#         elif extension.lower() == '.docx':
#              with open(file_path, 'rb') as f:
#                 return read_docx(f, filename=os.path.basename(file_path))
#         elif extension.lower() == '.txt':
#              with open(file_path, 'rb') as f: # Read as bytes for consistent handling
#                 return read_txt(f, filename=os.path.basename(file_path))
#         else:
#             print(f"Unsupported file type: {extension}")
#             return None
#     except FileNotFoundError:
#         print(f"Error: File not found at {file_path}")
#         return None
#     except Exception as e:
#         print(f"Error while processing file path {file_path}: {e}")
#         return None

# --- URL Scraping Functions (Unchanged from original logic, added error prints) ---

def scrape_url(url):
    """Scrape content from URL using requests/BeautifulSoup"""
    try:
        print(f"Fetching URL: {url}") # Debugging statement
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, timeout=20, headers=headers) # Increased timeout, added user-agent
        print(f"Response Status Code: {response.status_code}") # چاپ کد وضعیت

        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        soup = BeautifulSoup(response.content, 'html.parser')

        # Try to find main content areas first, fallback to paragraphs
        main_content = soup.find('main') or soup.find('article') or soup.find('div', role='main')
        if main_content:
             paragraphs = main_content.find_all(['p']) # Focus on <p> within main content
        else:
             paragraphs = soup.find_all(['p']) # Fallback to all <p> tags

        text = "\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])

        if text.strip(): # Check if any text was actually extracted
            print(f"Scraped URL Text (First 500 chars): {text[:500]}")
            return text.strip()
        else:
            # If no <p> tags worked, try getting all text from body
            print("Warning: No text found in <p> tags. Trying body text.")
            body_text = soup.body.get_text(separator='\n', strip=True) if soup.body else None
            if body_text:
                 print(f"Scraped Body Text (First 500 chars): {body_text[:500]}")
                 return body_text.strip()
            else:
                print("Error: No meaningful text could be scraped from the URL.")
                return None # Explicitly return None if scraping fails

    except requests.exceptions.RequestException as e:
        print(f"Error during requests to {url}: {e}")
        return None
    except Exception as e:
        print(f"Error while scraping URL {url}: {e}")
        return None

def scrape_url_with_selenium(url):
    """Scrape content from URL using Selenium (for JavaScript-heavy websites)"""
    # Important: Requires chromedriver to be installed and accessible.
    # Provide the full path to chromedriver if it's not in PATH.
    # Example: service = Service("C:/path/to/chromedriver.exe")
    try:
        print(f"Fetching URL with Selenium: {url}") # Debugging statement
        service = Service() # Assumes chromedriver is in PATH or Service finds it
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox") # Often needed in containerized environments
        options.add_argument("--disable-dev-shm-usage") # Overcome limited resource problems
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36") # Set user agent

        # Use a context manager for the driver
        with webdriver.Chrome(service=service, options=options) as driver:
            driver.get(url)
            time.sleep(5) # Increase wait time for JS loading

            # Extract text - consider trying body text as a fallback
            elements = driver.find_elements(By.TAG_NAME, "p")
            text = "\n".join([element.text for element in elements if element.text and element.text.strip()])

            if not text.strip():
                print("Warning: No text found in <p> tags via Selenium. Trying body text.")
                try:
                     body_element = driver.find_element(By.TAG_NAME, "body")
                     text = body_element.text
                except Exception as body_e:
                     print(f"Could not get body text via Selenium: {body_e}")
                     text = "" # Ensure text is empty string if body fails

            text = text.strip()
            if text:
                print(f"Scraped Selenium URL Text (First 500 chars): {text[:500]}")
            else:
                print("Error: No meaningful text found on the page via Selenium.")

            return text if text else None

    except Exception as e:
        print(f"Error while scraping URL with Selenium: {e}")
        # Check for common Selenium errors like WebDriverException
        if "WebDriverException" in str(e):
            print("Ensure chromedriver is installed and accessible in your PATH.")
        return None
