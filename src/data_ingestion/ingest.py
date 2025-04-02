import os
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader  # PdfReader جایگزین PdfFileReader شده است
import docx
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

def read_pdf(file_path):
    """Extract text from PDF file"""
    try:
        print(f"Reading PDF file: {file_path}")  # Debugging statement
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PdfReader(file)  # استفاده از PdfReader
            for page in pdf_reader.pages:  # صفحات با استفاده از pages دسترسی پیدا می‌کنیم
                page_text = page.extract_text()  # استخراج متن از هر صفحه
                if page_text:  # بررسی اینکه آیا متن وجود دارد یا خیر
                    text += page_text
        print(f"Extracted PDF Text (First 500 chars): {text[:500]}")  # چاپ متن استخراج‌شده برای اشکال‌زدایی
        return text
    except Exception as e:
        print(f"Error while reading PDF: {e}")
        return None

def read_docx(file_path):
    """Extract text from DOCX file"""
    try:
        print(f"Reading DOCX file: {file_path}")  # Debugging statement
        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        print(f"Extracted DOCX Text (First 500 chars): {text[:500]}")  # چاپ متن استخراج‌شده برای اشکال‌زدایی
        return text
    except Exception as e:
        print(f"Error while reading DOCX: {e}")
        return None

def read_txt(file_path):
    """Extract text from TXT file"""
    try:
        print(f"Reading TXT file: {file_path}")  # Debugging statement
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        print(f"Extracted TXT Text (First 500 chars): {text[:500]}")  # چاپ متن استخراج‌شده برای اشکال‌زدایی
        return text
    except Exception as e:
        print(f"Error while reading TXT: {e}")
        return None

def scrape_url(url):
    """Scrape content from URL"""
    try:
        print(f"Fetching URL: {url}")  # Debugging statement
        response = requests.get(url, timeout=10)  # افزودن timeout برای جلوگیری از مسدود شدن
        print(f"Response Status Code: {response.status_code}")  # چاپ کد وضعیت
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            paragraphs = soup.find_all(['p', 'div', 'span'])  # جستجو در تگ‌های مختلف
            text = "\n".join([p.get_text() for p in paragraphs if p.get_text().strip()])
            
            if text.strip():  # بررسی اینکه آیا متن خالی نیست
                print(f"Scraped URL Text (First 500 chars): {text[:500]}")  # چاپ متن استخراج‌شده برای اشکال‌زدایی
                return text
            else:
                print("No text found on the page.")  # اگر متنی وجود نداشته باشد
                return None
        else:
            print(f"Failed to fetch URL. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error while scraping URL: {e}")
        return None

def scrape_url_with_selenium(url):
    """Scrape content from URL using Selenium (for JavaScript-heavy websites)"""
    try:
        print(f"Fetching URL with Selenium: {url}")  # Debugging statement
        
        # تنظیمات WebDriver
        service = Service("chromedriver.exe")  # مسیر فایل chromedriver
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # اجرای مرورگر در حالت پنهان
        driver = webdriver.Chrome(service=service, options=options)
        
        # باز کردن وب‌سایت
        driver.get(url)
        time.sleep(3)  # زمان برای بارگذاری کامل صفحه
        
        # استخراج متن
        elements = driver.find_elements(By.TAG_NAME, "p")
        text = "\n".join([element.text for element in elements if element.text.strip()])
        
        if text.strip():  # بررسی اینکه آیا متن خالی نیست
            print(f"Scraped URL Text (First 500 chars): {text[:500]}")  # چاپ متن استخراج‌شده برای اشکال‌زدایی
        else:
            print("No text found on the page.")  # اگر متنی وجود نداشته باشد
        
        driver.quit()
        return text
    except Exception as e:
        print(f"Error while scraping URL with Selenium: {e}")
        return None

def process_file(file_path):
    """Process file based on extension"""
    _, extension = os.path.splitext(file_path)
    try:
        if extension.lower() == '.pdf':
            return read_pdf(file_path)
        elif extension.lower() == '.docx':
            return read_docx(file_path)
        elif extension.lower() == '.txt':
            return read_txt(file_path)
        else:
            print(f"Unsupported file type: {extension}")
            return None
    except Exception as e:
        print(f"Error while processing file: {e}")
        return None