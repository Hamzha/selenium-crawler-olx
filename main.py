from sys import path
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from mangodb import *

PATH = "C:\Program Files (x86)/chromedriver.exe"

option = webdriver.ChromeOptions()

option.add_argument("--disable-infobars")
option.add_argument("start-maximized")
option.add_argument("--disable-extensions")
option.add_experimental_option(
    "prefs", {"profile.default_content_setting_values.notifications": 2}
)


def open_page(url, options):

    driver = webdriver.Chrome(options=options, executable_path=PATH)
    driver.get(url)

    return driver


def search_element(driver, query):
    driver.find_element(by=By.XPATH,
                        value='//input[@type="search"]').send_keys(query)
    driver.find_element(by=By.XPATH,
                        value='//button[@aria-label="Search"]').click()
    return driver


def load_till_last_page(driver):
    product_list = []
    try:
        sleep(5)

        product_list = driver.find_element(by=By.XPATH,
                                           value='//li[@aria-label="Listing"]/article[@class="_7e3920c1"]/div[@class="ee2b0479"]/a')
        for index, product in enumerate(product_list):
            print('----', index, product)
            product_list[index] = product.get_attribute('href')
    except Exception as e:
        print(e.__str__())
    return driver, product_list


def get_all_pages(driver, url):
    page_links = []
    i = 1
    while True:
        try:
            driver.get(url+'?page='+str(i))
            total_height = int(driver.execute_script(
                "return document.body.scrollHeight"))
            for l in range(1, total_height, 5):
                driver.execute_script("window.scrollTo(0, {});".format(l))

            links = driver.find_elements(
                by=By.XPATH, value='//div[@class="a52608cc"]/a')

            for l in links:
                page_links.append(l.get_attribute('href'))

            driver.find_element(
                by=By.XPATH, value='//a[@class="_95dae89d"]').click()
            i += 1
            sleep(5)
        except Exception as e:
            print(e.__str__())
            break
    return driver, page_links


def save_ads_links():
    cluster, db = connect_DB('mongodb://localhost:27017', 'olx')
    driver = open_page(url='https://www.olx.com.pk/', options=option)
    driver = search_element(driver, 'oneplus 7')
    url = driver.current_url

    driver, pages_link = get_all_pages(driver, url)
    print(pages_link)
    for link in pages_link:
        insert_single_record(db, 'olx', {'url': link})
    driver.quit()


def delete_all_records():
    cluster, db = connect_DB('mongodb://localhost:27017', 'olx')
    db.olx.delete_many({})


def iterate_ads_link():
    cluster, db = connect_DB('mongodb://localhost:27017', 'olx')

    data = get_all_records(db, 'olx')
    driver = open_page(url='https://www.olx.com.pk/', options=option)
    i = 0
    for d in data:
        i+=1
        print(i)
        print(d['url'])
        try:
            driver.get(url=d['url'])
            images = driver.find_elements(by=By.XPATH,
                                        value='//img[@class="_5b8e3f79"]')
            sleep(3)
            # for image in images:
            #     print(image.get_attribute("src"))
            price = driver.find_element(by=By.XPATH,
                                        value='//span[@class="_56dab877"]').text
            price = ''.join([str(s) for s in price if s.isdigit()])
            location = driver.find_element(by=By.XPATH,
                                        value='//div[@class="_1075545d e3cecb8b _5f872d11"]').text
            description = driver.find_element(by=By.XPATH,
                                            value='//div[@class="_0f86855a"]/span').text
            record = {
                'price': price,
                'location': location.split('\n')[0],
                'description': description,
                'images': [value.get_attribute("src") for value in images]
            }
            update_record(db, 'olx', d['_id'], record)
        except:
            print('error')
            continue
    driver.quit()


iterate_ads_link()
