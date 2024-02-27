import pandas as pd
import requests 
import re
import urllib.request
import os
import re
import shutil

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from html.parser import HTMLParser
from urllib.parse import urlparse
from collections import deque
from bs4 import BeautifulSoup

#directory = os.getenv("output_directory")
#output_directory = directory

output_directory = r'E:\QDS\azure-search-openai-demo'
output_directory2 = output_directory+r'\text'
output_directory_W = output_directory+r'\data'

# Regex pattern to match a URL
HTTP_URL_PATTERN = r'^http[s]*://.+'

# Create a class to parse the HTML and get the hyperlinks
class HyperlinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        # Create a list to store the hyperlinks
        self.hyperlinks = []

    # Override the HTMLParser's handle_starttag method to get the hyperlinks
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        # If the tag is an anchor tag and it has an href attribute, add the href attribute to the list of hyperlinks
        if tag == "a" and "href" in attrs:
            self.hyperlinks.append(attrs["href"])

# Function to get the hyperlinks from a URL
          
def get_hyperlinks(url):

    # Try to open the URL and read the HTML
    try:
        # Open the URL and read the HTML
        with urllib.request.urlopen(url) as response:

            # If the response is not HTML, return an empty list
            if not response.info().get('Content-Type').startswith("text/html"):
                return []

            # Decode the HTML
            html = response.read().decode('utf-8')
    except Exception as e:
        print(e)
        return []

    # Create the HTML Parser and then Parse the HTML to get hyperlinks
    parser = HyperlinkParser()
    parser.feed(html)

    return parser.hyperlinks

# Function to get the hyperlinks from a URL that are within the same domain
def get_domain_hyperlinks(local_domain, url):
    clean_links = []
    for link in set(get_hyperlinks(url)):
        clean_link = None

        # If the link is a URL, check if it is within the same domain
        if re.search(HTTP_URL_PATTERN, link):
            # Parse the URL and check if the domain is the same
            url_obj = urlparse(link)
            if url_obj.netloc == local_domain:
                clean_link = link

        # If the link is not a URL, check if it is a relative link
        else:
            if link.startswith("/"):
                link = link[1:]
            elif link.startswith("#") or link.startswith("mailto:"):
                continue
            clean_link = "https://" + local_domain + "/" + link

        if clean_link is not None:
            if clean_link.endswith("/"):
                clean_link = clean_link[:-1]
            clean_links.append(clean_link)

    # Return the list of hyperlinks that are within the same domain
    return list(set(clean_links))

def delete_files_in_folder(folder_path):
    try:
        # Check if the folder exists
        if os.path.exists(folder_path):
            # Iterate over each file in the folder and delete it
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
            print(f"All files deleted from {folder_path}")
        else:
            print(f"Folder {folder_path} does not exist.")
    except Exception as e:
        print(f"Error deleting files: {e}")




def crawl(url):
    # Parse the URL and get the domain
    local_domain = urlparse(url).netloc

    # Create a queue to store the URLs to crawl
    queue = deque([url])

    # Create a set to store the URLs that have already been seen (no duplicates)
    seen = set([url])

    # While the queue is not empty, continue crawling
    while queue:

        # Get the next URL from the queue
        url = queue.pop()
        print(url) # for debugging and to see the progress

        # Save text from the url to a <url>.txt file
        with open(output_directory2+"\\"+url.replace("https://","").replace(".", "_").replace("/", "_") + ".txt", "w", encoding="UTF-8") as f:

            # Get the text from the URL using BeautifulSoup
            soup = BeautifulSoup(requests.get(url).text, "html.parser")

            # Get the text but remove the tags
            text = soup.get_text()

            # If the crawler gets to a page that requires JavaScript, it will stop the crawl
            if ("You need to enable JavaScript to run this app." in text):
                print("Unable to parse page " + url + " due to JavaScript being required")

            # Otherwise, write the text to the file in the text directory
            f.write(text)

        # Get the hyperlinks from the URL and add them to the queue
        for link in get_domain_hyperlinks(local_domain, url):
            if link not in seen:
                queue.append(link)
                seen.add(link)

def remove_newlines(serie):
    serie = serie.str.replace('\n', ' ')
    serie = serie.str.replace('\\n', ' ')
    serie = serie.str.replace('  ', ' ')
    serie = serie.str.replace('  ', ' ')
    return serie


def create_pdf_from_dataframe(df, output_file):
    # Create a PDF document
    pdf_document = SimpleDocTemplate(output_file, pagesize=letter)

    # Create a style sheet
    styles = getSampleStyleSheet()
    style_normal = styles['Normal']

    # Create paragraphs with text from the 'text' column
    paragraphs = [Paragraph(text, style_normal) for text in df['text']]

    # Build the PDF document
    pdf_document.build(paragraphs)

def remove_newlines_pdf(text):
        return text.replace('\n', ' ')     

class WEB_to_PDF():    
    # Create a directory to store the text files
   
    if not os.path.exists(output_directory2):
        os.mkdir(output_directory2)
    else: 
        delete_files_in_folder(output_directory2)
    with open(output_directory+r'/qdsnet.txt', 'r') as file:
        urls = file.read().splitlines()

    # Define a regular expression pattern to extract the website name
    pattern = re.compile(r'https://www\.(\w+)\.com')

    website_groups = {}

    # Group URLs by website names
    for url in urls:
        match = re.search(pattern, url)
        if match:
            website_name = match.group(1)
            if website_name not in website_groups:
                website_groups[website_name] = []
            website_groups[website_name].append(url.strip())

    for index, url in enumerate(urls, start=1):
        crawl(url)
    output_directory_f = output_directory_W+"\\"+website_name
    if os.path.exists(output_directory_f):
        shutil.rmtree(output_directory_f)
    os.makedirs(output_directory_f)
     

    # Create a list to store the text files
    texts=[]

    # Get all the text files in the text directory
    for file in os.listdir(output_directory2):
        with open(os.path.join(output_directory2, file), "r", encoding="UTF-8") as f:
            text = f.read()
            texts.append((file[11:-4].replace('-', ' ').replace('_', ' ').replace('#update', ''), text))
            print (file.replace('.txt', ''))

            # Create a dataframe from the list of texts
            df = pd.DataFrame(texts, columns=['fname', 'text'])
            df.drop('fname', axis=1, inplace=True)
            df['text'] = df['text'].apply(remove_newlines_pdf)
            # Create separate PDFs for each URL in the dataframe
            out = output_directory_f+"\\"+file.replace('.txt', '.pdf')
            create_pdf_from_dataframe(df,out)
            texts.clear() 
          