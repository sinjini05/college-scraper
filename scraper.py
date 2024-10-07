import os
import requests
import re
import xml.etree.ElementTree as ElementTree
from bs4 import BeautifulSoup
from csv import writer
import socket
from socket import error as socket_error
import time

def handle_requests(query, token='', cookie=''):
    '''Returns HTML document'''
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, khtml, like Gecko) Chrome/98.0.4758.82 Safari/537.36",
        "Accept-Encoding": "*",
        "Connection": "keep-alive"
    }
    
    try:
        response = requests.get(query, headers=headers, cookies=cookie, verify=False, timeout=10)
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

def scrape_colleges(output_file='college.csv'):
    with open(output_file, 'a', newline='', encoding='utf-8') as f:
        thewriter = writer(f)
        header = ['College Name', 'Link', 'Placement Link', 'Details']
        thewriter.writerow(header)

        data = handle_requests('https://www.4icu.org/in/')
        if not data:
            return

        soup = get_soup(data)
        colleges = soup.find('div', class_='table-responsive').find_all('tr')[870:]

        for college in colleges:
            name = college.find('a').text.strip()
            link = 'https://www.4icu.org' + college.find('a').get('href')
            data1 = handle_requests(link)
            if not data1:
                continue
            soup1 = get_soup(data1)

            website = soup1.find('table', class_='table borderless').find('tr')
            websitelink = website.a['href'] if website and website.a else None

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
                    root = ElementTree.XML(page)
                    for child in root:
                        for subchild in child:
                            if subchild.tag == "{http://www.sitemaps.org/schemas/sitemap/0.9}loc":
                                if 'Placement' in subchild.text:
                                    placement_links.append(subchild.text)
                except Exception as ex:
                    print("Error parsing sitemap:", ex)

            College = [name, websitelink, placement_links, details]
            thewriter.writerow(College)

if __name__ == "__main__":
    scrape_colleges()
