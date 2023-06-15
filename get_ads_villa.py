import time
import re
from bs4 import BeautifulSoup
import requests
from logzero import logger
import logzero
from datetime import datetime
from models import create_engine, connection_string, VillaAdvertises
from sqlalchemy.orm import Session

logzero.logfile("./logs/villa_ads_logfile.log", maxBytes=1e7, backupCount=10)


def fix_city(text):
    pattern = r"(?<=در\s).*"
    res = re.search(pattern, text)
    return res.group()


def get_commercials():
    logger.info("crawling on divar over whole iran cities to get all urls for villas")
    engine = create_engine(connection_string)
    queries = ['?page=', '?q=اجاره%20ویلا&page=', '?q=اجاره%20ویلا%20باغ&page=']
    for q in queries:
        logger.debug(f"Searching for Advertises in {q}".encode('utf-8'))
        for page in range(10000):
            time.sleep(10)
            with Session(engine) as session:
                logger.info(f"page number {page}")
                headers = {
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                  'Chrome/112.0.0.0 Safari/537.36'
                }
                try:
                    response = requests.get(
                        f'https://divar.ir/s/iran/rent-temporary-villa{q}{page}', headers=headers)
                    # time.sleep(20)
                    soup = BeautifulSoup(response.content, 'lxml')
                    article = soup.find_all('div', class_='post-card-item-af972')
                    if len(article) == 0:
                        break
                    logger.debug(f"{len(article)} Advertise found in page {page}".encode('utf-8'))
                    new_counter = 0
                    for i in article:
                        villa_advertise = VillaAdvertises(AdvertiseUrl=f"https://divar.ir{i.find('a')['href']}",
                                                        City=fix_city(
                                                            i.find('span', class_='kt-post-card__bottom-description').text))
                        _villa_advertise = session.query(VillaAdvertises).filter(
                            VillaAdvertises.AdvertiseUrl == villa_advertise.AdvertiseUrl).first()
                        if _villa_advertise:
                            new_counter += 1
                            # logger.debug(
                            #     f"this url has already added to DB {villa_advertise.AdvertiseUrl}".encode('utf-8'))
                            continue
                        session.add(villa_advertise)
                    session.commit()
                    logger.warning(f'{len(article) - new_counter} new villas added to db')
                    logger.warning('session committed to db')
                except Exception as e:
                    logger.exception(e)
                    continue
            time.sleep(10)


if __name__ == '__main__':
    start = datetime.now()
    get_commercials()
    end = datetime.now()
    print('start: ', start, 'end: ', end, 'duration: ', end - start)
