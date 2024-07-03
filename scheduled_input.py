import streamlit as st

import datetime
import joblib

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import requests

import psycopg2



def fetch_odine_stock_price():

    url = "https://bigpara.hurriyet.com.tr/borsa/hisse-fiyatlari/odine-odine-teknoloji-detay/"
    response = requests.get(url)
    soup1 = BeautifulSoup(response.text, 'html.parser')
    odine_val = (
        float(
        soup1
        .find('div', class_='hisseProcessBar mBot10')
        .find("span", class_="value")
        .text.strip()
        .replace(",", ".")
        ))
    return odine_val


def get_driver():
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")  
    chrome_options.add_argument("--no-sandbox")  
    chrome_options.add_argument("--disable-dev-shm-usage") 
    chrome_options.add_argument("--disable-gpu")  

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def fetch_usd_rate():
    
    url = "https://www.tcmb.gov.tr/wps/wcm/connect/tr/tcmb+tr/main+page+site+area/bugun"
    
    driver = get_driver()
    driver.get(url)
    html = driver.page_source
    driver.quit()
    
    soup2 = BeautifulSoup(html, 'html.parser')
    usd_val = (
        float(
            soup2
            .find("table", class_ = "kurlarTablo")
            .find_all("td", class_ = "deger efdeger")
            [1].text
            .strip()
            .replace(",", ".")
            ))
    return usd_val
    
def insert_data(odine_val, usd_val, entrydate):
    
    DATABASE_URL = joblib.load("postgresql_url.pkl")
    
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO tbl_odine (odine_fiyat, tlusd_doviz_kuru, entrydate) VALUES (%s, %s, %s);
        ''', (odine_val, usd_val, entrydate))
        conn.commit()
        cur.close()
        
    except Exception as e:
        print(f"Hata: {e}")
        
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    
    odine_val = fetch_odine_stock_price()
    usd_val = fetch_usd_rate()
    entrydate = datetime.datetime.now().strftime("%d-%m-%Y, %H:%M:%S")
    
    insert_data(odine_val, usd_val, entrydate)
    st.write("Today's ODINE value:", odine_val)

