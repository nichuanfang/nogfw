import requests
import my_selenium
import logging

logging.basicConfig(level=logging.INFO)

soup = my_selenium.get_soup('https://www.youtube.com/watch?v=qmRkvKo-KbQ')
logging.info(soup.prettify())