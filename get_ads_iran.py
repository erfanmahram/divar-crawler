import time
import re
from bs4 import BeautifulSoup
import requests
from logzero import logger
import logzero
from datetime import datetime
from models import create_engine, connection_string, IranAdvertises
from sqlalchemy.orm import Session

logzero.logfile("./logs/iran_ads_logfile.log", maxBytes=1e7, backupCount=10)


def fix_city(text):
    pattern = r"(?<=در\s).*"
    res = re.search(pattern, text)
    return res.group()


def get_commercials():
    logger.info("crawling on divar over whole iran cities to get all urls for villas")
    engine = create_engine(connection_string)
    queries = ['اجاره%20سوییت%20مبله', 'اجاره%20مبله', 'اجاره%20اپارتمان%20مبله']
    for q in queries:
        logger.debug(f"Searching for Advertises in {q}".encode('utf-8'))
        for page in range(21,10000):
            time.sleep(10)
            with Session(engine) as session:
                logger.info(f"page number {page}")
                headers = {
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                  'Chrome/112.0.0.0 Safari/537.36'
                }
                try:
                    response = requests.get(
                        f'https://divar.ir/s/iran/rent-temporary-suite-apartment?q={q}&page={page}', headers=headers)
                    # time.sleep(20)
                    soup = BeautifulSoup(response.content, 'lxml')
                    article = soup.find_all('div', class_='post-card-item-af972')
                    if len(article) == 0:
                        break
                    logger.debug(f"{len(article)} Advertise found in page {page}".encode('utf-8'))
                    for i in article:
                        iran_advertise = IranAdvertises(AdvertiseUrl=f"https://divar.ir{i.find('a')['href']}",
                                                        City=fix_city(
                                                            i.find('span', class_='kt-post-card__bottom-description').text))
                        _iran_advertise = session.query(IranAdvertises).filter(
                            IranAdvertises.AdvertiseUrl == iran_advertise.AdvertiseUrl).first()
                        if _iran_advertise:
                            logger.debug(
                                f"this url has already added to DB {iran_advertise.AdvertiseUrl}".encode('utf-8'))
                            continue
                        session.add(iran_advertise)
                    session.commit()
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
