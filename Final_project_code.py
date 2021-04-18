import wikipediaapi
import json
import requests
from requests_oauthlib import OAuth1
from newsapi import NewsApiClient
import sqlite3

wiki_wiki = wikipediaapi.Wikipedia('en')
page_aa = wiki_wiki.page('Ann Arbor')
aa_summary = page_aa.summary[0:195]
# print(aa_summary)

yelp_api_key = '4A0HCpyZ1rG4ktcbb5tOkRh4HsR4LREJRG2u-RMTCgik4otTdY5Kpkptl9gMak6yZD3wQbAf1N3LTTvPToc39-rIfMHP60OowZRVwp_INkFV52PfnyHW_UIArTh7YHYx'

ENDPOINTS_YELP = 'https://api.yelp.com/v3'

news_api = NewsApiClient(api_key='c657a4f410d641eab4771c6a5d95f60c')

conn = sqlite3.connect("City.sqlite")
cur = conn.cursor()

create_city_wiki = '''
    CREATE TABLE IF NOT EXISTS "city" (
        "Id" INTEGER UNIQUE,
        "Name"  TEXT NOT NULL,
        "County" TEXT NOT NULL,
        "State"  TEXT NOT NULL,
        "Population" INTEGER NOT NULL,
        PRIMARY KEY("Id" AUTOINCREMENT)
    );
'''

create_restaurant_yelp = '''
    CREATE TABLE IF NOT EXISTS "restaurant" (
        "Id" INTEGER UNIQUE,
        "Name"  TEXT NOT NULL,
        "County" TEXT NOT NULL,
        "State"  TEXT NOT NULL,
        "Population" INTEGER NOT NULL,
        PRIMARY KEY("Id" AUTOINCREMENT)
    );
'''

cur.execute(create_city_wiki)
conn.commit()

CACHE_FILE_NAME = "yelp_cache.json"
CACHE_DICT = {}

top_headlines = newsapi.get_top_headlines(q='bitcoin',
                                          sources='bbc-news,the-verge',
                                          category='business',
                                          language='en',
                                          country='us')

def load_cache():
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache

def save_cache(cache):
    dumped_json_cache = json.dumps(cache)
    fw = open(CACHE_FILE_NAME,"w")
    fw.write(dumped_json_cache)
    fw.close()

city = input("Please input the full name of the city that you would like to know")

restaurant = input("Interested in most popular restaurant in that city? Y/N")

news = input("Also interested in latest news about that city? Y/N")