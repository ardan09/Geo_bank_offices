# -*- coding: utf-8 -*-

import requests
import numpy as np   
import pandas as pd  
import re
import math
import time  
import random 
from bs4 import BeautifulSoup
# from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver import ActionChains
# UserAgent().chrome
from selenium.common.exceptions import WebDriverException

# chromedriver установил через терминал brew install chromedriver
driver = webdriver.Chrome(executable_path="/usr/local/bin/chromedriver")

def get_url(page, region):
    url = 'https://www.cian.ru/cat.php?deal_type=rent&engine_version=2&offer_type=offices&office_type%5B0%5D=2&p='+ str(page) + '&region=' +  str(region)
    return url

def get_content(response):
    html = driver.page_source
    soup = BeautifulSoup(html,'html.parser')
    return soup

def find_num(text):
    ans = ''.join(re.findall(r'[0-9.]*[0-9]+', text))
    if ans == '':
        return 0
    else:
        return float(ans)

def offer_count(soup):
    n_offers = find_num(soup.html.head.title.text)
    return n_offers

def get_url_list(soup):
    OfferCards = soup.find_all('div', {'data-name': 'CommercialOfferCard'})
    url_list = []
    for i in range(len(OfferCards)):
        url = soup.find_all('a', {'class': 'c6e8ba5398--header-link--xVxAx'}, href=True)[i]['href'] # 03/01/21 - заменил 3XZlV на xVxAx - из кода страницы
        url_list.append(url)
    return url_list

def get_adress(html_list):
    html_list = html_list.find_all('address', {'class': 'a10a3f92e9--address--F06X3'}) # 03/01/21 - заменил значение 'class' из кода страницы
    adress_clean = []
    adress = html_list[0].find_all('a')
    for i in adress:
        adress_clean.append(i.text)
    return ", ".join(adress_clean)


def get_price_area(soup, address, url):
    adress = address
    url = url
    prices = soup.find_all('div', {'data-name': 'AreaParts'})
    all_trade = pd.DataFrame({"address":[], "area":[], "metr_price":[],"price":[], "url":[]}) 
    dict_tz = {}
    
    if len(prices) > 0:  
        for i in range(1, len(prices)):           
            area = prices[i].find_all('div', {'class': 'a10a3f92e9--area--TPGV8'})[0].text
            print('in for; ', area) # TEST
            metr_price = prices[i].find_all('div', {'class': 'a10a3f92e9--price-of-meter--SE6dT'})[0].text
            print('in for; ', metr_price) # TEST
            price = prices[i].find_all('div', {'class': 'a10a3f92e9--price--rz9MI'})[0].text
            print('in for; ', price) # TEST
            dict_tz["address"] = adress
            dict_tz["area"] = area
            dict_tz["metr_price"] = metr_price
            dict_tz["price"] = price
            dict_tz["url"] = url
            all_trade = all_trade.append(pd.DataFrame([dict_tz]))
            
    else: 
        area = soup.find_all('div', {'class': 'a10a3f92e9--info-value--bm3DC'})[0].text
        print('in else; ', area) # TEST
        metr_price = soup.find_all('div', {'a10a3f92e9--price_per_meter--yfcbi a10a3f92e9--price_per_meter--commercial--ALuAy'})[0].text
        print('in else; ', metr_price) # TEST

        try:
            price = soup.find_all('div', {'class': 'a10a3f92e9--value--wNns'})[0].text
        except:
            price = soup.find_all('div', {'class': 'a10a3f92e9--value--wNnsl'})[0].text

        print('in else; ', price) # TEST

        dict_tz["address"] = adress
        dict_tz["area"] = area
        dict_tz["metr_price"] = metr_price
        dict_tz["price"] = price
        dict_tz["url"] = url
        all_trade = all_trade.append(pd.DataFrame([dict_tz]))
        
    return all_trade

regions_code_zian = {'26ulyanovsk': 5027}
# {'35ufa': 176245, '71tumen': 5024}
#{'01msc':1} # {'25ulan_ude':5026}

cities = list(regions_code_zian.keys())
cities.sort()
cities = cities

for city in cities:

    all_trade_points = pd.DataFrame({"address":[], "area":[], "metr_price":[],"price":[], "url":[]})
    region = regions_code_zian[city]
    try:
        response = driver.get(get_url(1, region))
    except WebDriverException:
        driver.quit()
        # chromedriver установил через терминал brew install chromedriver
        driver = webdriver.Chrome(executable_path="/usr/local/bin/chromedriver")
        response = driver.get(get_url(1, region))
        
    soup = get_content(response)
    num_pages = int(offer_count(soup) / 25 + 1)

    if num_pages == 1:
        print("только 1 страница")
        # inp = input()

    print (city, " ", str(num_pages)," страниц")

    for page in range(1, num_pages + 1):

        print(str(page)," страница")

        try:
            response = driver.get(get_url(page, region))
        except WebDriverException:
            driver.quit()
            # chromedriver установил через терминал brew install chromedriver
            driver = webdriver.Chrome(executable_path="/usr/local/bin/chromedriver")
            response = driver.get(get_url(page, region))

        soup = get_content(response)
        url_list = get_url_list(soup)

        if len(url_list) == 0:
            continue

        for url in url_list:

            print(url) # TEST

            try:
                response = driver.get(url)
            except WebDriverException:
                driver.quit()
                # chromedriver установил через терминал brew install chromedriver
                driver = webdriver.Chrome(executable_path="/usr/local/bin/chromedriver")
                response = driver.get(url)

            soup = get_content(response)

            try:
                address = get_adress(soup)
                all_trade = get_price_area(soup, address, url)
                print(all_trade.head()) # TEST
                all_trade_points = all_trade_points.append(all_trade, ignore_index = True)
                print(all_trade_points.head()) # TEST
            except (ValueError, IndexError) as e:
#                 inp = input()
                print('has not parsed data from', url)
                # break # TEST
                # continue
            time.sleep(random.randrange(10,12))

        all_trade_points.to_csv("trade_1_" + city + ".csv", sep = ";", encoding='utf-8-sig')

        print (all_trade_points.head())

        time.sleep(random.randrange(10,15))

    time.sleep(random.randrange(10,20))

all_trade_points.to_csv("trade_" + city + ".csv", sep = ";", encoding='utf-8-sig')

driver.close()
driver.quit()