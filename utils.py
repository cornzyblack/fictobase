import os
import requests
from datetime import datetime
from dotenv import load_dotenv
import re
from bs4 import BeautifulSoup
import logging
from random import random, shuffle, randint, uniform

load_dotenv()
logging.basicConfig(
    filename="scraping.log",
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def get_org_info(org_name):
    response = None
    crunchbase_api_key = os.getenv("CRUNCHBASE_API_KEY")
    try:
        org_name = org_name
        url = "https://api.crunchbase.com/v3.1/odm-organizations"
        querystring = {
            "name": org_name,
            "sort_order": "created_at DESC",
            "page": "1",
            "user_key": crunchbase_api_key,
        }
        response = requests.request("GET", url, params=querystring)
    except Exception as e:
        print(e)
    return response


def extract_details_json(json_obj):
    data = None
    items = None
    item = {}
    item_extract = {
        "api_path": None,
        "facebook_url": None,
        "twitter_url": None,
        "created_at": None,
        "short_description": None,
        "homepage_url": None,
        "region_name": None,
        "country_code": None,
        "profile_image_url": None,
    }

    if type(json_obj) == dict:
        try:
            data = json_obj.get("data")
            items = data.get("items")
            if (data is not None) and (items is not None):
                item = items[0].get("properties", {})
                item_extract["name"] = item.get("name", None)
                item_extract["api_path"] = item.get("api_path", None)
                item_extract["facebook_url"] = item.get("facebook_url", None)
                item_extract["twitter_url"] = item.get("twitter_url", None)
                item_extract["created_at"] = extract_date_pair(
                    item.get("created_at", None)
                )
                item_extract["short_description"] = item.get("short_description", None)
                item_extract["homepage_url"] = item.get("homepage_url", None)
                item_extract["region_name"] = item.get("region_name", None)
                item_extract["total_funding"] = None

                item_extract["web_path"] = (
                    "https://www.crunchbase.com/" + item["web_path"]
                    if item.get("web_path")
                    else None
                )
                item_extract["country_code"] = item["country_code"]
                item_extract["profile_image_url"] = item["profile_image_url"]
                item_extract["total_funding_dict"] = None
                item_extract["total_employee_dict"] = None
                item_extract["total_funding"] = None
                item_extract["total_employees"] = None
        except Exception as e:
            print("Here")
            print(e)

    return item_extract


def extract_date_pair(timestamp):
    date_pair_string = None
    try:
        date_pair = datetime.fromtimestamp(timestamp)
        date_pair_string = date_pair.strftime("%d, %B %Y")
    except Exception as e:
        logging.exception(timestamp)

    return date_pair_string


def convert_text_number(amount):
    result = None
    large_num_acronymns = {"K": 3, "M": 6, "B": 9, "T": 12}

    try:
        amount = re.sub(",", "", amount)

        amount_findings = re.search("(\d+[,\.\d]*)([KMBT]*)", amount)
        if amount_findings:
            amount = float(amount_findings.group(1))
            number_scale = amount_findings.group(2).upper()
            power = large_num_acronymns.get(number_scale, 0)
            result = amount * 10 ** power

    except Exception as e:
        print(e)
        logging.exception(amount)
        logging.shutdown()

    return result


def get_total_funding(site_url):

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "DNT": "1",
        "Connection": "close",
        "Upgrade-Insecure-Requests": "1",
    }

    total_funding = None
    response = requests.get(site_url, headers=headers)
    print(site_url)
    try:
        print("Response code", response.status_code)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            funding_tags = soup.find_all(
                "a",
                "link-primary component--field-formatter field-type-money ng-star-inserted",
            )
            print("---------------------")
            print(funding_tags)

            if funding_tags:
                total_funding = funding_tags[0].text

    except Exception as e:
        print("Error ", e)
        logging.exception(site_url)
        logging.shutdown()

    return total_funding


def random_fund_generator(company_name):
    no_years = round(len(company_name) * uniform(0.3, 1.45))
    start_date = 2020
    year_dict = {}
    total_funding = 0
    for year in range(1, no_years + 1):
        funding_amt_list = list(range(1, 17))
        shuffle(funding_amt_list)
        year_funding_amt = str(funding_amt_list[year]) + "K"
        fund_amt = convert_text_number(year_funding_amt)
        year_dict[start_date - year] = fund_amt
        total_funding += fund_amt

    total_funding = f"{total_funding:,.2f}"
    return total_funding, year_dict


def employee_generator(company_name):
    no_years = round(len(company_name) * random())
    start_date = 2020
    year_dict = {}
    total_employees = 0
    for year in range(1, no_years + 1):
        employee_amt_list = list(range(-4, 10))
        shuffle(employee_amt_list)
        year_dict[start_date - year] = employee_amt_list[year]
        total_employees += employee_amt_list[year]

    total_employees += randint(6, 15)
    total_employees = str(total_employees)

    return total_employees, year_dict
