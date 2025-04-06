import os
import requests
import re
import xml.etree.ElementTree as ElementTree
from defusedxml.ElementTree import fromstring as secure_fromstring
from bs4 import BeautifulSoup
from csv import writer
import socket
from socket import error as socket_error
import time
from urllib.parse import urlparse

def handle_requests(query, token='', cookie=''):
    '''Returns HTML document'''
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, khtml, like Gecko) Chrome/98.0.4758.82 Safari/537.36",
        "Accept-Encoding": "*",
        "Connection": "keep-alive"
    }
    
    try:
        response = requests.get(query, headers=headers, cookies=cookie, verify=True, timeout=10)
        response.raise_for_status()  # Raise an error for bad responses
        return response.text
    except (requests.ConnectionError, socket.error) as e:
        print("Could not connect to the server:", e)
        return None
    except requests.Timeout:
        print("Request timed out.")
        return None
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def get_soup(data):
    '''Returns parsed Soup Object from HTML text'''
    return BeautifulSoup(data, "html.parser")

def is_valid_url(url):
    '''Validates a URL'''
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def scrape_colleges(output_file='college.csv'):
    if not os.path.exists(output_file):
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            thewriter = writer(f)
            header = ['College Name', 'Link', 'Placement Link', 'Details']
            thewriter.writerow(header)

    with open(output_file, 'a', newline='', encoding='utf-8') as f:
        thewriter = writer(f)

        data = handle_requests('https://www.4icu.org/in/')
        if not data:
            return

        soup = get_soup(data)
        colleges = soup.find('div', class_='table-responsive').find_all('tr')[870:]

        for college in colleges:
            name = college.find('a').text.strip()
            link = 'https://www.4icu.org' + college.find('a').get('href')
            if not is_valid_url(link):
                print(f"Invalid URL: {link}")
                continue

            data1 = handle_requests(link)
            if not data1:
                continue
            soup1 = get_soup(data1)

            website = soup1.find('table', class_='table borderless').find('tr')
            websitelink = website.a['href'] if website and website.a else None
            if websitelink and not is_valid_url(websitelink):
                print(f"Invalid website link: {websitelink}")
                websitelink = None

            details = ''
            if websitelink:
                soup_obj = get_soup(handle_requests(websitelink))
                body = soup_obj.find_all('body')
                for div in body:
                    text = div.get_text().strip()
                    if re.search(r'[+91][0-9]+', text):
                        details = text
                        break  # Stop after finding the first match

            else:
                print('Website link not available')

            # Fetch placement links from sitemap
            placement_links = []
            page = handle_requests(f'{websitelink}/sitemap.xml') if websitelink else None
            if page:
                try:
                    root = secure_fromstring(page)
                    for child in root:
                        for subchild in child:
                            if subchild.tag == "{http://www.sitemaps.org/schemas/sitemap/0.9}loc":
                                if 'Placement' in subchild.text:
                                    placement_links.append(subchild.text)
                except Exception as ex:
                    print("Error parsing sitemap:", ex)

            College = [name, websitelink, placement_links, details]
            sanitized_college = [str(item).replace('\n', ' ').replace('\r', '') for item in College]
            thewriter.writerow(sanitized_college)

if __name__ == "__main__":
    scrape_colleges()