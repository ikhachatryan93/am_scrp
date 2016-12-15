import os
import re
import time
import sys

pwd = os.path.dirname(os.path.realpath(__file__))
sys.path.append(pwd)

import pythonLib

from bs4 import BeautifulSoup
from selenium import webdriver

try:
    from urllib.parse import urljoin
except:
    from urlparse import urljoin

# import csv
main_url = "https://www.amazon.co.uk/"


def setup_chrome_browser():
    PROXY = "198.55.109.157:3128"
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--proxy-server=%s' % PROXY)
    chrome = webdriver.Chrome("engines/chromedriver", chrome_options=chrome_options)
    return chrome


def setup_proxy_and_browser():
    service_args = [
        '--proxy=198.55.109.157:3128'
        '--proxy-type=socks5']

    driver = webdriver.PhantomJS(executable_path="engines/phantomjs", service_args=service_args)
    return driver


# function to start browsing and getting page soup
def request(url, driver, hover=False):
    try:
        driver.maximize_window()
    except Exception as e:
        print (str(e))

    driver.get(url)

    if hover:
        try:
            elements = driver.find_element_by_id("altImages").find_elements_by_css_selector(".a-button-input")
            for e in elements:
                pythonLib.hover(driver, e)
        except Exception as e:
            print str(e)

    return driver


# function to make soup
def make_soup(driver):
    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    return soup


def get_feature_bullets(feature_table):
    desk = []
    for b in feature_table:
        desk.append(b.get_text().replace(';', ' ').replace(',', ' ').replace('&nbsp', ' ').strip())

    try:
        bul_1 = desk[0]
    except:
        bul_1 = ""

    try:
        bul_2 = desk[1]
    except:
        bul_2 = ""

    try:
        bul_3 = desk[2]
    except:
        bul_3 = ""

    try:
        bul_4 = desk[3]
    except:
        bul_4 = ""

    try:
        bul_5 = desk[4]
    except:
        bul_5 = ""

    return desk, bul_1, bul_2, bul_3, bul_4, bul_5


def get_images(soup, driver):
    all_images = []

    try:
        class_id = re.compile(".*itemNo.*")
        image_li = soup.find('div', {'id': 'main-image-container'}).find_all('li', {'class': class_id})
    except:
        image_li = []

    for li in image_li:
        try:
            div = li.find("div", {"class": "imgTagWrapper"})
            all_images.append(div.find("img").get("data-old-hires"))
        except:
            continue

    try:
        img_1 = all_images[0]
    except:
        img_1 = ""

    try:
        img_2 = all_images[1]
    except:
        img_2 = ""

    try:
        img_3 = all_images[2]
    except:
        img_3 = ""

    try:
        img_4 = all_images[3]
    except:
        img_4 = ""

    try:
        img_5 = all_images[4]
    except:
        img_5 = ""

    return img_1, img_2, img_3, img_4, img_5


def get_price(soup):
    try:
        price = soup.find('span', {'id': 'priceblock_ourprice'}).get_text().strip()
    except:
        try:
            price = soup.find('span', {"class": "a-color-price"}).get_text()
        except:
            price = ""

    return price


def get_item_weight(info_table):
    item_weight = ""
    for each_tr in info_table:

        if "Item Weight" in each_tr.find('td').get_text().strip():
            td_2 = each_tr.findAll('td')
            item_weight = td_2[1].get_text().strip()
            break

    return item_weight


def save_products_data(soup, page_url, subcategory, filename, driver):
    # name
    try:
        keyword = soup.head.find("meta", {"name": "keywords"}).get("content").strip()
    except:
            print "#####################"
            print "can not find keyword" + page_url
            return

    try:
        title = soup.find('h1', {'id': 'title'}).get_text().replace('&nbsp', ' ').strip()
    except:
        title = ""

    try:
        brand = soup.find('a', {'id': 'brand'}).get_text().replace('&nbsp', ' ').strip()
    except:
        brand = ""

    price = get_price(soup)

    try:
        feature_table = soup.find('div', {'id': 'feature-bullets'}).find_all('span')
    except:
        feature_table = []

    description, bul_1, bul_2, bul_3, bul_4, bul_5 = get_feature_bullets(feature_table)

    try:
        info_table = soup.find('div', {'id': 'prodDetails'}).find_all('tr')
    except:
        info_table = []

    item_weight = get_item_weight(info_table)

    img_1, img_2, img_3, img_4, img_5 = get_images(soup, driver)

    print ("Saving Data...")
    if not os.path.exists(filename):
        headings = ["Keyword",
                    "Subcategory",
                    "Title",
                    "Brand",
                    "Price",
                    "Description",
                    "Image Url 1", "Image Url 2", "Image Url 3", "Image Url 4", "Image Url 5",
                    "Bullet Point 1", "Bullet Point 2", "Bullet Point 3", "Bullet Point 4", "Bullet Point 5",
                    "Weight",
                    "Product URL"]
        pythonLib.save_to_csv(filename, headings)

    pythonLib.save_to_csv(filename, [keyword, subcategory, title, brand, price, " ".join(description),
                                     img_1, img_2, img_3, img_4, img_5,
                                     bul_1, bul_2, bul_3, bul_4, bul_5,
                                     item_weight, page_url])


item_class = "a-link-normal s-access-detail-page a-text-normal"


def get_category_items(subcategory_url, subcategory_name, driver, all_items, page):
    try:
        print("page %d" % page)
    except:
        print ("asdasd")

    try:
        driver = request(subcategory_url, driver)
        soup = make_soup(driver)
    except:
        print ("error when reading " + subcategory_name)
        return ()

    try:
        next_page = urljoin(main_url, soup.find("a", {"id": "pagnNextLink"}).get("href"))
    except:
        next_page = ""

    if next_page:
        page += 1
        get_category_items(next_page, subcategory_name, driver, all_items, page)

    try:
        items = soup.findAll('a', {"class": item_class})
    except:
        items = []

    for item in items:
        all_items[item.get("href")] = subcategory_name

def unit_test(url):
    subcategory="test_category"
    driver = setup_proxy_and_browser()
    result_file = "products_data_test.csv"
    print ("Extracting Product Data...")
    driver = request(url, driver, hover=True)
    soup = make_soup(driver)

    save_products_data(soup, url, subcategory, result_file, driver)

# calling main function...
def main():
    #unit_test("https://www.amazon.co.uk/Coastline-la16mo-m-si-Guest-Towel-Cotton-x/dp/B01J9LRMIS/ref=sr_1_6166?m=A3P5ROKL5A1OLE&s=kitchen&ie=UTF8&qid=1481805662&sr=1-6166")
    result_file = "products_data.csv"

    print ("Opening Browser")
    driver = setup_proxy_and_browser()
    #driver = setup_chrome_browser()

    subcategory_links = pythonLib.read_col_csv("categories.csv", 4)
    subcategory_names = pythonLib.read_col_csv("categories.csv", 0)

    # extract_all_items from category
    all_items = {}
    for subcategory_link, subcategory_name in zip(subcategory_links, subcategory_names):
        page = 1
        print("extracting item urls from " + subcategory_name)
        try:
            get_category_items(subcategory_link, subcategory_name, driver, all_items, page)
        except:
            print ("skipping " + subcategory_name + " " + subcategory_link)

    try:
        done_urls = pythonLib.read_col_csv("done_urls.csv", 0)
    except:
        done_urls = []

    for url, subcategory in all_items.iteritems():

        print ("Visiting URL: " + url)

        if url not in done_urls:
            print ("Extracting Product Data...")
            driver = request(url, driver, hover=True)
            soup = make_soup(driver)

            save_products_data(soup, url, subcategory, result_file, driver)
            pythonLib.save_to_csv("done_urls.csv", [url])

# calling get_profiles() function to start the program
if __name__ == '__main__':
    sys.exit(main())
