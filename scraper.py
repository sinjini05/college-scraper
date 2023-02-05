import requests,re
from pickle import TRUE
import xml.etree.ElementTree as ElementTree
from bs4 import BeautifulSoup
from csv import writer
import socket
from socket import error as socket_error


response=''

def handleRequests(query, token='', cookie=''):
    '''Returns HTML document'''

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36",
    "Accept-Encoding": "*",
    "Connection": "keep-alive"
    }
    try:
        response=requests.get(query, headers=headers, cookies=cookie,verify=False,timeout=600000).text
        return response 
    except ConnectionError :
        print("This site can't be reached") 
        pass
    except socket.error :
        print("couldnt connect with the server")
        pass

   

def getSoup(data):
    '''Returns parsed Soup Object from html text'''
    return BeautifulSoup(data, "html.parser")


data = handleRequests('https://www.4icu.org/in/')
soup = getSoup(data)


  
with open('college.csv','a',newline='',encoding='utf-8') as f:
 thewriter=writer(f)
 header=['College Name','Link','Placement Link','Details']
 thewriter.writerow(header)

 colleges=soup.find('div',class_='table-responsive').find_all('tr')[870:]

   
 for college in colleges:
    name=college.find('a').text.strip()

    link='https://www.4icu.org'+college.find('a').get('href')
    data1=handleRequests(link)
    soup1=getSoup(data1)
 
    website=soup1.find('table',class_='table borderless').find('tr')
    websitelink=website.a['href']

    if websitelink:

     soup_obj = getSoup(handleRequests(websitelink))
     body = soup_obj.find_all('body')
     text=''
     details=''
     for div in body:
          text = div.get_text().strip()
          if re.search(r'[+91][0-9]+', text):
            details=text
    else:
        print('not available')    
            



    page = handleRequests(f'{websitelink}/sitemap.xml')
    placement_links = []


    try:
        root = ElementTree.XML(page)
        for i, child in enumerate(root):
            for subchild in child:
                if subchild.tag == "{http://www.sitemaps.org/schemas/sitemap/0.9}loc":
                    if 'Placement'  in subchild.text:
                        placement_links.append(subchild.text)
    except Exception as ex:
        pass
    

    College=[name,websitelink,placement_links,details]
    thewriter.writerow(College)


response.close()

    
url='https://www.4icu.org/in'


  
   