from my_fake_useragent import UserAgent
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import re
from datetime import datetime
import logging

logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.INFO)


def get_renew_auto_fr_pages(nbr_pages):
    print("Generating pages links")
    pages_links = []
    for i in range(1, nbr_pages + 1):
        url = "https://fr.renew.auto/achat-vehicules-occasions.html?page=" + str(i)
        print(f"generating : {url}")
        pages_links.append(url)
    return pages_links


def get_renew_auto_fr_car_links(pages_links):
    car_links = []
    try:
        for link in pages_links:
            print(f"Get the ads links from : {link}")
            # Scraping Method
            ua = UserAgent(family='chrome')
            user_agent = ua.random()
            headers = {
                "User-agent": user_agent
            }
            page = requests.get(link, headers=headers, timeout=560)
            soup = BeautifulSoup(page.content, 'lxml')
            ad_div = soup.find_all("a", class_="UCIVehicleCard__link")
            for ad in ad_div:
                car_link = ad.get("href")
                link = "https://fr.renew.auto" + car_link
                car_links.append(link)
            page.close()
    except:
        pass
    return car_links


def scrape_revew_auto_fr(links):
    cars = []
    for link in links:
        try:
            print(f"Get car data from : {link}")
            # Scraping Method
            ua = UserAgent(family='chrome')
            user_agent = ua.random()
            headers = {
                "User-agent": user_agent
            }
            page = requests.get(link, headers=headers, timeout=560)
            if page.status_code == 200:
                soup = BeautifulSoup(page.content, "lxml")
                car = {"ad_url": link}
                model_brand_div = soup.find("span", class_="UCIVehicleDetailsCardOld__brand")
                version_div = soup.find("span", class_="UCIVehicleDetailsCardOld__model")
                model_brand = model_brand_div.get_text().strip()
                version = version_div.get_text().strip()
                title = model_brand + " " + version
                car_title = (" ".join(title.split())).strip()
                car['ad_title'] = car_title
                try:
                    brand = str(model_brand_div.contents[0])
                    brand = brand.strip().lower()
                    car["car_brand"] = brand
                except:
                    car["car_brand"] = None
                try:
                    model = str(model_brand_div.contents[4])
                    model = model.strip().lower()
                    car["car_model"] = model
                except:
                    car["car_model"] = None
                try:
                    version = version.strip().lower()
                    car['car_version'] = version
                except:
                    car["car_version"] = None
                try:
                    location = soup.find("a", class_="UCIVehicleDetailsCardOld__dealerInfos")
                    car["owner_company_name"] = location.get_text().strip()
                except:
                    car["owner_company_name"] = None
                try:
                    price = soup.find("p", class_="UCIVehicleDetailsCardOld__salesOptionPrice")
                    car["ad_price"] = int("".join(re.findall(r"\d+", price.get_text())))
                except:
                    car["ad_price"] = None
                # car_data
                try:
                    info_data = soup.find("ul", class_="UCIVehicleEssentials__ListContent")
                    li_data = info_data.find_all("li", class_="UCIVehicleEssentials__ListItem")
                except:
                    li_data = None
                try:
                    data_list = soup.find("ul", class_="HorizontalList UCIVehicleDetailsIconsOld")
                    list_of_items = data_list.find_all("li", class_="HorizontalList__item")
                    transmission_types = ["manuelle", "automatique", "hybride", "robotisée"]
                    transmission = list_of_items[3].get_text().strip().lower()
                    for car_transmission in transmission_types:
                        if car_transmission in transmission:
                            car['car_transmission'] = car_transmission
                except:
                    car["car_transmission"] = None
                    # car_energy
                try:
                    energy_types = ["hybride", "diesel", "essence", "electrique", "gpl", "hydrogene", "gnv",
                                    "bioethanol", "gnl", "ethanol"]
                    car["car_energy"] = None
                    energy = li_data[3].get_text().strip()
                    energy = energy.lower()
                    for car_energy in energy_types:
                        if car_energy in energy:
                            car['car_energy'] = car_energy
                except:
                    car["car_energy"] = None
                # car_reg_year
                try:
                    year = li_data[0].get_text().strip()
                    car['car_reg_year'] = int(year)
                    car_reg_year = int(year)
                    car["car_registration_year"] = datetime(car_reg_year, 1, 1)
                except:
                    car['car_reg_year'] = None
                    car["car_registration_year"] = None
                # car_km
                try:
                    km = list_of_items[0].get_text().strip()
                    km = int(''.join(re.findall(r'\d+', km)))
                    car['car_km'] = km
                except:
                    car["car_km"] = None
                # car_color
                try:
                    color = li_data[1].get_text().strip().lower()
                    car["car_color"] = color
                except:
                    car["car_color"] = None
                # car_real_power
                try:
                    power = li_data[8].get_text().split(":")
                    power = power[1].strip()
                    car["car_power"] = int(''.join(re.findall(r'\d+', power)))
                except:
                    car["car_power"] = None
                # car_body
                try:
                    body = li_data[2].get_text().strip().lower()
                    car["car_body"] = body
                except:
                    car["car_body"] = None
                # car_nb_seats
                try:
                    car_nb_seats = li_data[6].get_text().split(":")
                    car_nb_seats = car_nb_seats[1].strip()
                    car["car_nb_seats"] = int(''.join(re.findall(r'\d+', car_nb_seats)))
                except:
                    car["car_nb_seats"] = None
                # car_nb_doors
                try:
                    car_nb_doors = li_data[5].get_text().split(":")
                    car_nb_doors = car_nb_doors[1].strip()
                    car["car_nb_doors"] = int(''.join(re.findall(r'\d+', car_nb_doors)))
                except:
                    car["car_nb_doors"] = None
                    # car_power
                try:
                    car_power = li_data[8].get_text().split(":")
                    car_power = car_power[1].strip()
                    car["car_power"] = int(''.join(re.findall(r'\d+', car_power)))
                except:
                    car["car_power"] = None
                # car_consumption
                try:
                    car_emission = li_data[10].get_text().split(":")
                    car_emission = car_emission[1].strip()
                    car["car_emission"] = int(''.join(re.findall(r'\d+', car_emission)))
                except:
                    car["car_emission"] = None
                # car_options
                try:
                    car_options = []
                    options = soup.find_all("div", class_="UCIVehicleSpecsContainer__items")
                    for option in options:
                        equipements = option.find_all("div", class_="UCIVehicleSpecsContainer__item")
                        for equipement in equipements:
                            car_options.append(equipement.get_text().lower().strip())
                    if car_options:
                        car["car_options"] = car_options
                except:
                    car["car_options"] = None
                # owner_phone_number
                try:
                    owner_location = soup.find_all("div", class_="DealerPreview__cta")
                    owner_location = owner_location[0].get_text().strip()
                    car["owner_location"] = owner_location
                except:
                    car["owner_location"] = None
                    # owner_phone_number
                try:
                    tel_number = soup.find_all("div", class_="DealerPreview__cta")
                    tel_number = tel_number[1].get_text().strip()
                    car["owner_phone_number"] = tel_number
                except:
                    car["owner_phone_number"] = None
                    # Fixed Features
                car['currency'] = "EUR"
                car["data_type"] = "FULL"
                car["ad_inactive"] = False
                car["country_code"] = "FR"
                # car : resulted_from scraping
                car['resulted_from'] = BOT_NAME
                car['ad_source'] = BASE_SRC
                car["ad_creation_date"] = datetime.utcnow()
                car["ad_crawling_date"] = datetime.utcnow()
                cars.append(car)
            page.close()
        except:
            pass
    return cars


def test_required_columns(df):
    required_names = {'ad_url',
                      'ad_price',
                      'ad_title',
                      'car_energy',
                      'car_km',
                      'car_brand',
                      'car_model',
                      'car_transmission',
                      'car_reg_year'}
    if set(required_names).issubset(df.columns):
        print(f"Your required features test is Valid ✅ 🎉")
    else:
        print(f"Your required features test is Valid ❌")


def change_features_type(df):
    columns_to_int = ['ad_price', 'car_km', 'car_reg_year', 'car_nb_doors', 'car_nb_seats', 'car_power',
                      'car_real_power', 'car_weight', 'car_displacement', 'car_gearbox']
    columns_to_double = ['car_consumption', 'car_emission', 'car_cylinder']
    columns_to_bool = ['ad_inactive']
    columns_to_datetime = ['car_registration_year', 'ad_creation_date', 'ad_crawling_date', 'ad_publish_date']
    for i in columns_to_int:
        if i in df.columns:
            df[i] = df[i].astype(float).astype("Int32")
    for i in columns_to_double:
        if i in df.columns:
            df[i] = df[i].astype(float)
    for i in columns_to_bool:
        if i in df.columns:
            df[i] = df[i].astype(bool)
    for i in columns_to_datetime:
        if i in df.columns:
            df[i] = pd.to_datetime(df[i])
    print("Changing features types")
    return df


def test_column_types(df):
    columns_to_int = ['ad_price', 'car_km', 'car_reg_year', 'car_nb_doors', 'car_nb_seats', 'car_power',
                      'car_real_power', 'car_weight', 'car_displacement', 'car_gearbox']
    columns_to_double = ['car_consumption', 'car_emission', 'car_cylinder']
    columns_to_bool = ['ad_inactive']
    columns_to_datetime = ['car_registration_year', 'ad_creation_date', 'ad_crawling_date', 'ad_publish_date']
    test = True
    for column in df.columns:
        if column in columns_to_int:
            if not (df[column].dtypes == "Int32"):
                print(column, ' type is Not-Valid ❌')
                test = False
        if column in columns_to_double:
            if not (df[column].dtypes == float):
                print(column, ' type is Not-Valid ❌')
                test = False
        if column in columns_to_bool:
            if not (df[column].dtypes == bool):
                print(column, ' type is Not-Valid ❌')
                test = False
        if column in columns_to_datetime:
            if not (df[column].dtypes == 'datetime64[ns]'):
                print(column, ' type is Not-Valid ❌')
                test = False
    if test:
        print(f"Your features_type test is Valid ✅ 🎉")
    else:
        print(f"Your features_type test is Valid ❌")


def remove_null_values_from_list_dict(list_dict):
    new_list = [remove_null_values_from_dict(dict_item=d) for d in list_dict]
    return new_list


def remove_null_values_from_dict(dict_item):
    new_dict = {k: v for k, v in dict_item.items() if v is not None}
    return new_dict


# Define a custom JSON encoder that handles datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super(DateTimeEncoder, self).default(o)


BASE_SRC = 'https://fr.renew.auto'
BOT_NAME = 'renew_auto_fr.bot'
renew_auto_fr_pages_links = get_renew_auto_fr_pages(400)  # 1391
renew_auto_fr_ads_links = get_renew_auto_fr_car_links(renew_auto_fr_pages_links)
cars_dataset = scrape_revew_auto_fr(renew_auto_fr_ads_links)
cars_dataset = remove_null_values_from_list_dict(cars_dataset)
dataset = pd.DataFrame(cars_dataset)
test_required_columns(dataset)
dataset = change_features_type(dataset)
test_column_types(dataset)
dataset.to_csv('renew_auto_fr_scraping.csv', encoding="UTF-8")
# Serialize the data to a JSON-formatted string
json_string = json.dumps(cars_dataset, cls=DateTimeEncoder)
# Write the JSON string to a file
with open("renew_auto_fr_scraping.json", "w") as json_file:
     json_file.write(json_string)