import sys
import datetime
from random import randint
import os
from bs4 import BeautifulSoup as bs
import time
import re
from sqlalchemy.sql.expression import func
import requests
from logzero import logger
import logzero
from models import create_engine, connection_string, VillaAdvertises, PageStatus, StatusException
from sqlalchemy.orm import Session
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait as wait

logzero.logfile("./logs/villa_ads_logfile.log", maxBytes=1e7, backupCount=10, encoding='utf-8')


def separate_info(information):
    info_dict = dict()
    if len(information) % 2 == 0:
        for i in range(len(information) - 1):
            if i % 2 == 0:
                info_dict[information[i]] = information[i + 1]
        return info_dict
    else:
        return dict(information=information)


def get_neighbourhood(text):
    pattern = "(،)[^a-zA-Z](.*)"
    match = re.search(pattern, text)
    if match is None:
        pattern = "(در)[^a-zA-Z](.*)"
        match = re.search(pattern, text)
    return match.groups()[-1]


def crawl_with_selen(url, counter):
    time.sleep(randint(5, 20))
    driver.get(url)
    # if counter > 0:
    driver.add_cookie({'name': 'token',
                       'value': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiMDkxMjEwMDE3NTUiLCJpc3MiOiJhdXRoIiwidmVyaWZpZWRfdGltZSI6MTY4NjgyNDEyOSwiaWF0IjoxNjg2ODI0MTI5LCJleHAiOjE2ODgxMjAxMjksInVzZXItdHlwZSI6InBlcnNvbmFsIiwidXNlci10eXBlLWZhIjoiXHUwNjdlXHUwNjQ2XHUwNjQ0IFx1MDYzNFx1MDYyZVx1MDYzNVx1MDZjYyIsInNpZCI6IjEwM2JmOGExLTk5M2ItNGNjOS1iZmQyLTY4YmY0NWYzODZmNSJ9.4-JOHzui6SQQFIVqhHv6aiA5_zrgdYKL_aPMK1uWGDQ'})
    # else:
    #     driver.add_cookie({'name': 'token',
    #                        'value': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiMDkzOTQ3ODMwOTciLCJpc3MiOiJhdXRoIiwidmVyaWZpZWRfdGltZSI6MTY4MzU2MDc4NSwiaWF0IjoxNjgzNTYwNzg1LCJleHAiOjE2ODQ4NTY3ODUsInVzZXItdHlwZSI6InBlcnNvbmFsIiwidXNlci10eXBlLWZhIjoiXHUwNjdlXHUwNjQ2XHUwNjQ0IFx1MDYzNFx1MDYyZVx1MDYzNVx1MDZjYyIsInNpZCI6ImE2OTM5NjU1LTVmMmYtNGQ4MC04ZWYzLWNiNGU5YzVmNzY0NSJ9.nA8KqBRdpqVdJuUeYkfcoM-H8vq0QMsfQF3H9SkCaAc'})
    if driver.title == 'دیوار | این راه به جایی نمی‌رسد!':
        return dict(status_code=PageStatus.NotFound)
    button = driver.find_elements(By.CLASS_NAME, 'kt-button--primary')[-1]
    button.click()
    try:
        if driver.find_element(By.CSS_SELECTOR, "div[class='kt-dimmer kt-dimmer--darker kt-dimmer--open']"):
            status_code = PageStatus.AccessDenied
            return dict(status_code=status_code)
    except NoSuchElementException as ne:
        logger.info('not banned yet :D')
        pass
    wait(driver, timeout=60).until(lambda drv: driver.find_element(By.CLASS_NAME, 'kt-unexpandable-row__action').text)
    tell = driver.find_element(By.CLASS_NAME, 'kt-unexpandable-row__action').text
    title = driver.find_element(By.CLASS_NAME, 'kt-page-title__title').text
    info_box = driver.find_element(By.CLASS_NAME, 'post-page__section--padded').text.strip('\n')
    try:
        response = requests.get(driver.current_url)
        soup = bs(response.content, 'lxml')
        slides = soup.find('ul', class_='kt-carousel__slides')
        images_url = [i['src'] for i in slides.find_all('img')]
    except:
        logger.exception('No Images Found')
        images_url = []
        pass
    description = driver.find_element(By.CLASS_NAME, 'kt-description-row').text
    neighbourhood = driver.find_element(By.CLASS_NAME, 'kt-page-title__subtitle').text
    print(tell)
    info_box = info_box.split('\n')
    more_info = separate_info(info_box)
    return dict(title=title, phone_number=tell, information=more_info, image_url_list=images_url,
                description=description, neighbourhood=neighbourhood)


def get_images(id, urls):
    addresses = list()
    for i, url in enumerate(urls):
        with requests.get(url, stream=True) as req:
            req.raise_for_status()
            os.makedirs(os.path.dirname(f"villa_images/{id}/image{i}.jpg"), exist_ok=True)
            with open(f"villa_images/{id}/image{i}.jpg", "wb+") as img:
                for chunk in req.iter_content(chunk_size=8192):
                    img.write(chunk)
        addresses.append(f"villa_images/{id}/image{i}.jpg")
    return addresses


def crawl_commercials():
    counter = -1
    engine = create_engine(connection_string)
    with Session(engine) as session:
        urls = session.query(VillaAdvertises).filter(VillaAdvertises.Status != PageStatus.Finished).filter(
            VillaAdvertises.Status != PageStatus.NotFound).order_by(func.random()).order_by(
            VillaAdvertises.RetryCount.asc()).limit(5).all()
    logger.info(f"These urls {urls} are going to crawl")
    for url in urls:
        with Session(engine) as session:
            session.query(VillaAdvertises).filter(url.Id == VillaAdvertises.Id).update(
                {VillaAdvertises.RetryCount: url.RetryCount + 1})
            logger.info(f'crawling on {url}')
            _ads = session.query(VillaAdvertises).filter(VillaAdvertises.Id == url.Id).first()
            try:
                counter *= -1
                sel = crawl_with_selen(url.AdvertiseUrl, counter)
                if sel.get('status_code') == PageStatus.AccessDenied:
                    # _ads.Status = PageStatus.AccessDenied
                    raise StatusException(PageStatus.AccessDenied)
                elif sel.get('status_code') == PageStatus.NotFound:
                    # _ads.Status == PageStatus.NotFound
                    raise StatusException(PageStatus.NotFound)
                _ads.Phone = sel.get('phone_number')
                _ads.Title = sel.get('title')
                media = get_images(_ads.Id, sel.get('image_url_list'))
                _ads.Media = str(media)
                _ads.Descriptions = f"{sel.get('description')} \n+++\n {sel.get('information')}"
                rooms = sel.get('information').get('اتاق')
                if rooms == 'بدون اتاق':
                    rooms = 0
                _ads.Rooms = int(rooms) if rooms else None
                _ads.NeighbourHood = get_neighbourhood(sel.get('neighbourhood'))
                _ads.Status = PageStatus.Finished
                _ads.LastUpdate = datetime.datetime.utcnow()
                session.commit()
            except StatusException as se:
                if se.status_code == 403:
                    logger.error(f"Error 403 acces denied for adsId: {_ads.Id} - adsurl: {_ads.AdvertiseUrl}")
                    _ads.Status = PageStatus.AccessDenied
                    session.commit()
                    os.system("shutdown /s /t 60")
                    exit()
                    continue
                elif se.status_code == 404:
                    logger.error(f"Error 404 for adsId: {_ads.Id} - adsurl: {_ads.AdvertiseUrl}")
                    _ads.Status = PageStatus.NotFound
                    session.commit()
                    continue
                elif se.status_code == 500:
                    logger.error(f"Error 500 for adsId: {_ads.Id} - adsurl: {_ads.AdvertiseUrl}")
                    _ads.Status = PageStatus.ServerError
                    session.commit()
                    continue
                else:
                    logger.exception(se)
                    session.commit()
                    time.sleep(60)
                    continue
            except TimeoutException as te:
                logger.exception(te)
                _ads.Status = PageStatus.NotFound
                session.commit()
                continue
            except Exception as e:
                logger.exception(e)
                _ads.Status = PageStatus.Problem
                session.commit()
                continue


if __name__ == '__main__':
    import os

    while True:
        driver = webdriver.Firefox()
        crawl_commercials()
        time.sleep(10)
        driver.close()
        driver.quit()
        if datetime.datetime.now().hour == 0:
            os.system("shutdown /s /t 60")
            exit()
