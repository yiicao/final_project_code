import wikipediaapi
import json
import requests
from requests_oauthlib import OAuth1
from newsapi import NewsApiClient


import sqlite3
import urllib
from urllib.parse import quote




yelp_api_host = 'https://api.yelp.com'
yelp_search_path = '/v3/businesses/search'
yelp_api_key = '4A0HCpyZ1rG4ktcbb5tOkRh4HsR4LREJRG2u-RMTCgik4otTdY5Kpkptl9gMak6yZD3wQbAf1N3LTTvPToc39-rIfMHP60OowZRVwp_INkFV52PfnyHW_UIArTh7YHYx'


headers = {
        'Authorization': 'Bearer %s' % yelp_api_key,
        }

news_api = NewsApiClient(api_key='c657a4f410d641eab4771c6a5d95f60c')

CACHE_FILE_NAME = "wiki_cache.json"
CACHE_DICT = {}




def creat_yelp_db():
    conn = sqlite3.connect("restaurant.sqlite")
    cur = conn.cursor()

    create_restaurant_yelp = '''
        CREATE TABLE IF NOT EXISTS "restaurant" (
            "Id" INTEGER UNIQUE,
            "RestaurantId" TEXT NOT NULL,
            "Name"  TEXT NOT NULL,
            "Rating" NUMERIC NOT NULL,
            "Latitude"  NUMERIC NOT NULL,
            "Longitude" INTEGER NOT NULL,
            "City" TEXT NOT NULL,
            PRIMARY KEY("Id" AUTOINCREMENT)
        );
    '''
    create_city = '''
        CREATE TABLE IF NOT EXISTS "City" (
            "Id" INTEGER UNIQUE,
            "Name" TEXT NOT NULL,
            PRIMARY KEY("Id" AUTOINCREMENT)
        );
    '''
    cur.execute(create_restaurant_yelp)
    cur.execute(create_city)
    conn.commit()
    conn.close()

def insert_db_infor(restaurant_list):
    conn = sqlite3.connect("restaurant.sqlite")
    cur = conn.cursor()

    insert_restaurant_infor = '''
        INSERT INTO restaurant("RestaurantId", "Name", "Rating", "Latitude", "Longitude", "City")
        VALUES(?,?,?,?,?,?);
    '''
    insert_city_infor = '''
        INSERT INTO City("Name")
        VALUES(?);
    '''
    for each in restaurant_list:
        insertion = [each['RestaurantId'], each['Name'], each['Rating'], each['Latitude'], each['Longitude'], each['City']]
        cur.execute(insert_restaurant_infor, insertion)
    
    cur.execute(insert_city_infor, [restaurant_list[-1]['City']])
    conn.commit()
    conn.close()



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

def make_wiki_request_using_cache(city, cache):
    if (city in cache.keys()):
        print('Using cache')
        return cache[city]
    else:
        print('Fetching')
        response = get_wikipedia_full_text(city)
        cache[city] = response
        save_cache(cache)
        return cache[city]


def get_wikipedia_full_text(response):
    wiki_wiki = wikipediaapi.Wikipedia(
        language='en',
        extract_format=wikipediaapi.ExtractFormat.WIKI
    )
    wiki = wiki_wiki.page(response)

    return wiki.text

def make_request_yelp(city):
    url_params = {
        'term': 'restaurant',
        'location': city.replace(' ', '+'),
        'limit': 50
    }
    
    url = '{0}{1}'.format(yelp_api_host, quote(yelp_search_path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % yelp_api_key,
        }
    response = requests.request('GET', url, headers=headers, params=url_params)
    return response.json()

def get_restaurant_information(results):
    restaurant_list = []
    for each in results['businesses']:
        restaurant = {}
        restaurant['RestaurantId'] = each['id']
        restaurant['Name'] = each['name']
        restaurant['Rating'] = each['rating']
        restaurant['Latitude'] = each['coordinates']['latitude']
        restaurant['Longitude'] = each['coordinates']['longitude']
        restaurant['City'] = each['location']['city']
        restaurant_list.append(restaurant)
    return restaurant_list

def get_newsapi_info(city):
    all_articles = news_api.get_everything(q=city,
                                          language='en',
                                          from_param='2021-04-28'
                                          )
    return all_articles


def interactive_prompt():
    response = ''
    while response != 'exit':
        response = input("Please input the full name of the city that you would like to know: ")
        try:
            CACHE_DICT = load_cache()
            wiki_results = make_wiki_request_using_cache(response, CACHE_DICT)
            print(wiki_results)
            yelp_search = input('Interested in most popular restaurants in that city? Y/N ')
            if yelp_search == 'Y':
                yelp_results = make_request_yelp(response)
                print(yelp_results)
            res_list = get_restaurant_information(yelp_results)
            insert_db_infor(res_list)
            news_search = input('Also interested in latest news about that city? Y/N ')
            if news_search == 'Y':
                news_results = get_newsapi_info(response)
                print(news_results)
        except:
            print("Thanks for using!")



if __name__=="__main__":
    # get_newsapi_info()
    # creat_yelp_db()
    interactive_prompt()
    # city = input("Please input the full name of the city that you would like to know")

    # restaurant = input("Interested in most popular restaurant in that city? Y/N")

    # news = input("Also interested in latest news about that city? Y/N")

    # make_request_yelp('ann arbor')
    # creat_yelp_db()
