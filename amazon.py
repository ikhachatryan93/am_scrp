import os
import re
import time
import sys
from random import randint

pwd = os.path.dirname(os.path.realpath(__file__))
sys.path.append(pwd)

import pythonLib

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from get_proxies import get_new_proxies

try:
    from urllib.parse import urljoin
except:
    from urlparse import urljoin

# import csv
main_url = "https://www.amazon.co.uk/"

proxies = []


# proxies = {"198.55.109.157:3128"
#    ,"192.126.164.4:3128", "198.55.109.235:3128"
#    ,"173.234.226.148:3128", "173.234.226.147:3128"}


def setup_chrome_driver(proxy):
    PROXY = proxy
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--proxy-server=%s' % PROXY)
    chrome = webdriver.Chrome("engines/chromedriver", chrome_options=chrome_options)
    chrome.set_window_position(0, 0)
    chrome.set_window_size(0, 0)
    return chrome


def setup_phantomjs_driver(proxy, type):
    # dcap = dict(DesiredCapabilities.PHANTOMJS)
    user_agent = ("Mozilla / 5.0(X11; Linux i686) AppleWebKit / "
                  "{}.36(KHTML, like Gecko) Ubuntu Chromium / "
                  "53.0 .2785 .{} Chrome / 53.0 .2785 .{} Safari / 537.{}".format(randint(1200, 3100),
                                                                                  randint(1200, 3100),
                                                                                  randint(1200, 3100),
                                                                                  randint(30, 99)))
    # dcap["phantomjs.page.settings.userAgent"] = user_agent

    # driver = webdriver.PhantomJS(desired_capabilities=dcap)
    print("Opening Browser")
    service_args = ['--proxy={}'.format(proxy),
                    '--ignore-ssl-errors=true',
                    '--ssl-protocol=any',
                    '--web-security=false',
                    '--proxy-type={}'.format(type)]
    # service_args = [u'--proxy={{}}'.format(proxy),'--proxy-type={{}}'.format(type)]

    driver = webdriver.PhantomJS(executable_path="engines/phantomjs")
    # driver = webdriver.PhantomJS(desired_capabilities=dcap, executable_path="engines/phantomjs", service_args=service_args)
    driver = webdriver.PhantomJS(executable_path="engines/phantomjs", service_args=service_args)
    return driver


# function to start browsing and getting page soup
def request(url, browser, hover=False):
    try:
        browser.maximize_window()
        time.sleep(0.2)
    except Exception as e:
        print(str(e))

    browser.get(url)
    time.sleep(0.2)
    try:
        browser.save_screenshot('/workspace/sergey/asd.png')
    except Exception as e:
        print(str(e))

    if hover:
        try:
            elements = browser.find_element_by_id("altImages").find_elements_by_css_selector(".a-button-input")
            for e in elements[1:]:
                pythonLib.hover(browser, e)
                if e == elements[4]:
                    break
                time.sleep(0.2)
        except Exception as e:
            print(str(e))

    return browser


# function to make soup
def make_soup(driver):
    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    return soup


def get_feature_bullets(feature_table):
    desk = []
    for b in feature_table:
        desk.append(b.get_text().replace(';', ' ').replace(',', ' ').strip())

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
    print("size of windows is".format(len(driver.window_handles)))
    try:
        keyword = soup.head.find("meta", {"name": "keywords"}).get("content").strip()
    except:
        print("#####################")
        print("can not find keyword" + page_url)
        time.sleep(20)
        return

    try:
        title = soup.find('h1', {'id': 'title'}).get_text().strip()
    except:
        title = ""

    try:
        brand = soup.find('a', {'id': 'brand'}).get_text().strip()
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

    print('Saving Data...')
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


def get_items_urls(subcategory_url, subcategory_name, all_items, page, driver):
    print("page %d" % page)

    try:
        driver = request(subcategory_url, driver)
        soup = make_soup(driver)
    except Exception as e:
        print(str(e) + subcategory_name)
        return

    try:
        next_page = urljoin(main_url, soup.find("a", {"id": "pagnNextLink"}).get("href"))
    except:
        next_page = ""

    if next_page:
        page += 1
        get_items_urls(next_page, subcategory_name, all_items, page, driver)

    try:
        items = soup.findAll('a', {"class": item_class})
    except:
        items = []

    for item in items:
        all_items[item.get("href")] = subcategory_name


def unit_test(url):
    subcategory = "test_category"
    print(proxies[0])
    # driver = setup_phantomjs_driver(proxies[0], "html")
    driver = setup_chrome_driver(proxies[0])
    result_file = "products_data_test.csv"
    print("Extracting Product Data...")
    driver = request(url, driver, hover=False)
    soup = make_soup(driver)

    save_products_data(soup, url, subcategory, result_file, driver)


def get_items(all_items, driver):
    global proxies
    number_of_proxies = len(proxies)

    result_file = "products_data.csv"
    try:
        done_urls = pythonLib.read_col_csv("done_urls.csv", 0)
    except:
        done_urls = []

    change_id = 4
    assert (change_id == 4)
    for url, subcategory in all_items.iteritems():

        print("Visiting URL: " + url)

        if url not in done_urls:
            if change_id % 4 == 0:
                driver = setup_chrome_driver(proxies[(change_id % number_of_proxies)])
                # driver = setup_phantomjs_driver(proxies[(change_id % number_of_proxies)], "html")

            change_id += 1
            print("Extracting Product Data...")
            driver = request(url, driver, hover=True)
            soup = make_soup(driver)

            save_products_data(soup, url, subcategory, result_file, driver)
            pythonLib.save_to_csv("done_urls.csv", [url])


# calling main function...
def main():
    # unit_test("http://whatismyip.org/")

    global proxies

    subcategory_links = pythonLib.read_col_csv("categories.csv", 4)
    subcategory_names = pythonLib.read_col_csv("categories.csv", 0)

    for subcategory_link, subcategory_name in zip(subcategory_links[1:], subcategory_names[1:]):
        try:
            proxies = get_new_proxies("html")
        except Exception as e:
            print(str(e))
        driver = setup_phantomjs_driver(proxies[0], "html")
        #driver = setup_chrome_driver(proxies[0])
        print("extracting item urls from " + subcategory_name)
        all_items = {}
        page = 1
        try:
            get_items_urls(subcategory_link, subcategory_name, all_items, page, driver)
        except:
            print("skipping " + subcategory_name + " " + subcategory_link)

        get_items(all_items, driver)


if __name__ == '__main__':
    sys.exit(main())
