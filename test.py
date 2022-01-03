# import pandas as pd
#
# df_test = pd.read_csv("data/test.csv")
# print(df_test.head())

from selenium import webdriver
import time

url = "https://www.instagram.com/"

# chromedriver установил через терминал brew install chromedriver
driver = webdriver.Chrome(executable_path="/usr/local/bin/chromedriver")

try:
    driver.get(url=url)
    time.sleep(5)
except Exception as ex:
    print(ex)
finally:
    driver.close()
    driver.quit()