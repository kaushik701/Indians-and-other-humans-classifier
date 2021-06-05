# -*- coding: utf-8 -*-
"""
Created on Wed Apr  7 11:01:54 2021

@author: Arnav
"""

import selenium
from selenium import webdriver
import time
import requests
import os
from PIL import Image
import io
import hashlib
# This is the path I use
#DRIVER_PATH = '/Users/anand/Desktop/chromedriver'
# Put the path for your ChromeDriver here
DRIVER_PATH = 'D:\chromedriver_win32/chromedriver.exe'


def fetch_image_urls(query:str, max_links_to_fetch:int, wd:webdriver, sleep_between_interactions:int=1):
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)    
    
    # build the google query#type the url here
    search_url ="https://www.google.com/search?q=images+of+cheetah&tbm=isch&ved=2ahUKEwjYpoX-jsfwAhUDm-YKHd9HAZkQ2-cCegQIABAA&oq=images+of+chee&gs_lcp=CgNpbWcQARgAMgIIADICCAAyAggAMgIIADICCAAyAggAMgIIADICCAAyAggAMgIIADoECCMQJzoECAAQQzoFCAAQsQM6BAgAEAM6CAgAELEDEIMBUO-fCFjbmAxg1KQMaABwAHgAgAHVAYgBqAuSAQYwLjEwLjGYAQCgAQGqAQtnd3Mtd2l6LWltZ8ABAQ&sclient=img&ei=B1mdYJiHOYO2mgffj4XICQ&bih=803&biw=1688&rlz=1C1CHBD_enIN868IN870&hl=en"
    wd.get(search_url.format(q=query))

    image_urls = set()
    image_count = 0
    results_start = 0
    while image_count < max_links_to_fetch:
        scroll_to_end(wd)

        # get all image thumbnail results
        thumbnail_results = wd.find_elements_by_css_selector("img.Q4LuWd")
        number_results = len(thumbnail_results)
        
        print(f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")
        
        for img in thumbnail_results[results_start:number_results]:
            # try to click every thumbnail such that we can get the real image behind it
            try:
                img.click()
                time.sleep(sleep_between_interactions)
            except Exception:
                continue

            # extract image urls    
            actual_images = wd.find_elements_by_css_selector('img.n3VNCb')
            for actual_image in actual_images:
                if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                    image_urls.add(actual_image.get_attribute('src'))

            image_count = len(image_urls)

            if len(image_urls) >= max_links_to_fetch:
                print(f"Found: {len(image_urls)} image links, done!")
                break
        else:
            print("Found:", len(image_urls), "image links, looking for more ...")
            time.sleep(30)
            return
            load_more_button = wd.find_element_by_css_selector(".mye4qd")
            if load_more_button:
                wd.execute_script("document.querySelector('.mye4qd').click();")

        # move the result startpoint further down
        results_start = len(thumbnail_results)

    return image_urls

def persist_image(folder_path:str,file_name:str,url:str):
    try:
        image_content = requests.get(url).content

    except Exception as e:
        print(f"ERROR - Could not download {url} - {e}")

    try:
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file).convert('RGB')
        folder_path = os.path.join(folder_path,file_name)
        if os.path.exists(folder_path):
            file_path = os.path.join(folder_path,hashlib.sha1(image_content).hexdigest()[:10] + '.jpg')
        else:
            os.mkdir(folder_path)
            file_path = os.path.join(folder_path,hashlib.sha1(image_content).hexdigest()[:10] + '.jpg')
        with open(file_path, 'wb') as f:
            image.save(f, "JPEG", quality=85)
        print(f"SUCCESS - saved {url} - as {file_path}")
    except Exception as e:
        print(f"ERROR - Could not save {url} - {e}")

if __name__ == '__main__':
    wd = webdriver.Chrome(executable_path=DRIVER_PATH)
    queries = ["Cheetah"]  #change your set of querries here
    for query in queries:
        wd.get('https://google.com')
        search_box = wd.find_element_by_css_selector('input.gLFyf')
        search_box.send_keys(query)
        links = fetch_image_urls(query,50,wd)
        #images_path = '/Users/anand/Desktop/contri/images'  #enter your desired image path
        images_path = r"C:\Users\Kaushik\Desktop\MLProjects\Image Compression and Generation using Variational Autoencoders\Completed_Notebook_Data_Autoencoders\MiniProjectImages"
        for i in links:
            persist_image(images_path,query,i)
    wd.quit()
