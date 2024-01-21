import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime
import json
import logging

logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.INFO)


def get_brands():
    logging.info("Get brands_list from the network API")
    # Create a session to handle cookies
    session = requests.Session()

    # Add headers to the session
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/89.0.4389.82 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    session.headers.update(headers)
    # Send a GET request to the website
    link = "https://www.spoticar.fr/api/vehicleoffers/list/search?page=1"
    response = session.get(link)
    # Parse the response as JSON
    data = json.loads(response.text)
    brands_list = [item['key'].lower() for item in data['brands'][0]]
    return brands_list


def get_spoticar_fr_pages(nbr_pages):
    logging.info("Generating pages links")
    pages_links = []
    for i in range(1, nbr_pages + 1):
        url = "https://www.spoticar.fr/voitures-occasion?page=" + str(
            i) + "&gclid=Cj0KCQiA2-2eBhClARIsAGLQ2RmLWX9RHRY1zcon-MeOCzTG7NxKCf1l4CftXhiofjGgSQxUqib0Hc8aAjwAEALw_wcB&gclsrc=aw.ds"
        logging.info(f"generating : {url}")
        pages_links.append(url)
    return pages_links


def get_spoticar_fr_car_links(pages_links):
    car_links = []
    try:
        for link in pages_links:
            logging.info(f"Get the ads links from : {link}")
            # Create a session to handle cookies
            session = requests.Session()
            # Add headers to the session
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/89.0.4389.82 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            }
            session.headers.update(headers)
            # Send a GET request to the website
            response = session.get(link)
            soup = BeautifulSoup(response.content, 'lxml')
            ad_div = soup.find_all("div", class_="card clearfix gtm-vo-card")
            for ad in ad_div:
                link_div = ad.find("div", class_="card-wrapper col-lg-8 col-md-8 col-sm-12 col-xs-12")
                car_link = link_div.a.get("href")
                link = "https://www.spoticar.fr" + car_link
                logging.info(link)
                car_links.append(link)
    except:
        pass
    return car_links


def scrape_spoticar_fr(links, brands):
    global energy_types
    energy_types = ["hybride", "diesel", "essence", "electrique", "gpl", "hydrogene", "gnv",
                    "bioethanol", "gnl", "ethanol"]
    cars = []
    for link in links:
        try:
            logging.info(f"Get car data from : {link}")
            # Create a session to handle cookies
            session = requests.Session()

            # Add headers to the session
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/89.0.4389.82 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            }
            session.headers.update(headers)
            # Send a GET request to the website
            response = session.get(link)
            session.close()
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "lxml")
                car = {"ad_url": link}
                title = soup.find("h1", class_="psa-fiche-vo-title")
                car_title = (" ".join(title.get_text().split())).lower().strip()
                car['ad_title'] = car_title
                try:
                    brand_model = title.find("span", class_="title product-line").get_text().strip().lower()
                    for brand in brands:
                        if brand_model.startswith(brand):
                            car["car_brand"] = brand
                except:
                    car["car_brand"] = None
                try:
                    model = brand_model.replace(car.get("car_brand"), '').strip().lower()
                    car["car_model"] = model
                except:
                    car["car_model"] = None
                try:
                    version = title.find("span", class_="title product-finish").get_text()
                    version = (" ".join(version.split())).lower().strip()
                    version = version.replace(model, "")
                    car['car_version'] = version
                except:
                    car["car_version"] = None
                try:
                    location = soup.find("span", class_="pdv-adress-data")
                    car["owner_location"] = location.get_text()
                except:
                    car["owner_location"] = None
                try:
                    company_name = soup.find("a", class_="raison-sociale ")
                    car["owner_company_name"] = (" ".join(company_name.get_text().split())).lower().strip()
                except:
                    car["owner_company_name"] = None
                try:
                    price = soup.find("div", class_="price-taxe-div")
                    car["ad_price"] = int("".join(re.findall(r"\d+", price.span.get_text())))
                except:
                    car["ad_price"] = None
                try:
                    img_div = soup.find("div", class_="ratio-container unknown-ratio-container")
                    car["img_uri"] = img_div.img["data-src"]
                except:
                    car["img_uri"] = None
                # car_transmission
                try:
                    transmission = soup.find("div",
                                             class_="summary-entrie characteristic-item field_vo_gear_box").get_text().strip()
                    transmission = transmission.lower()
                    car['car_transmission'] = transmission
                except:
                    car["car_transmission"] = None
                    # car_energy
                try:
                    car["car_energy"] = None
                    energy = soup.find("div",
                                       class_="summary-entrie characteristic-item field_vo_fuel").get_text().strip()
                    energy = energy.lower()
                    for car_energy in energy_types:
                        if car_energy in energy:
                            car['car_energy'] = car_energy
                except:
                    car["car_energy"] = None
                # car_reg_year
                try:
                    year = soup.find("div",
                                     class_="summary-entrie characteristic-item field_vo_matriculation_year").get_text().strip()
                    car['car_reg_year'] = int(year)
                except (ValueError, Exception):
                    car['car_reg_year'] = None
                # car_km
                try:
                    km = soup.find("div",
                                   class_="summary-entrie characteristic-item field_vo_mileage").get_text().strip()
                    km = int(''.join(re.findall(r'\d+', km)))
                    car['car_km'] = km
                except:
                    car["car_km"] = None
                # car_color
                try:
                    color = soup.find("div", class_="characteristics-entries psa-fiche-vo-characteristics-list-color")
                    color = color.find("span", class_="title-data").get_text().strip().lower()
                    car["car_color"] = color
                except:
                    car["car_color"] = None
                # car_registration_year
                try:
                    registration_year = soup.find("div",
                                                  class_="characteristics-entries psa-fiche-vo-characteristics-list-entry-into-service")
                    registration_year = registration_year.find("span", class_="title-data").get_text().strip()
                    car["car_registration_year"] = pd.to_datetime(registration_year)
                except:
                    car["car_registration_year"] = None
                # car_real_power
                try:
                    power = soup.find("div",
                                      class_="characteristics-entries psa-fiche-vo-characteristics-list-din-power")
                    power = power.find("span", class_="title-data").get_text().strip()
                    car["car_real_power"] = int(''.join(re.findall(r'\d+', power)))
                except:
                    car["car_real_power"] = None
                # car_body
                try:
                    body = soup.find("div",
                                     class_="characteristics-entries psa-fiche-vo-characteristics-list-silhouette")
                    body = body.find("span", class_="title-data").get_text().strip()
                    car["car_body"] = body
                except:
                    car["car_body"] = None
                # car_nb_seats
                try:
                    car_nb_seats = soup.find("div",
                                             class_="characteristics-entries psa-fiche-vo-characteristics-list-nbPlaces")
                    car_nb_seats = car_nb_seats.find("span", class_="title-data").get_text().strip()
                    car["car_nb_seats"] = int(''.join(re.findall(r'\d+', car_nb_seats)))
                except:
                    car["car_nb_seats"] = None
                # car_power
                try:
                    car_power = soup.find("div",
                                          class_="characteristics-entries psa-fiche-vo-characteristics-list-fiscal-power")
                    car_power = car_power.find("span", class_="title-data").get_text().strip()
                    car["car_power"] = int(''.join(re.findall(r'\d+', car_power)))
                except:
                    car["car_power"] = None
                # saler_type
                try:
                    saler_type = soup.find("div",
                                           class_="characteristics-entries psa-fiche-vo-characteristics-list-origin")
                    if saler_type == "Ex-Particulier":
                        car["saler_type"] = "private"
                    elif saler_type == "Ex-Loueur":
                        car["saler_type"] = "pro"
                except:
                    car["saler_type"] = None
                    # car_nb_doors
                try:
                    car_nb_doors = soup.find("div",
                                             class_="characteristics-entries psa-fiche-vo-characteristics-list-nb-portes")
                    car_nb_doors = car_nb_doors.find("span", class_="title-data").get_text().strip()
                    car["car_nb_doors"] = int(''.join(re.findall(r'\d+', car_nb_doors)))
                except:
                    car["car_nb_doors"] = None
                # car_weight
                try:
                    car_weight = soup.find("div",
                                           class_="characteristics-entries psa-fiche-vo-characteristics-list-ptac psa-fiche-vo-characteristics-tooltip")
                    car_weight = car_weight.find("span", class_="title-data").get_text().strip()
                    car["car_weight"] = int(''.join(re.findall(r'\d+', car_weight)))
                except:
                    car["car_weight"] = None
                    # car_displacement
                try:
                    car_displacement = soup.find("div",
                                                 class_="characteristics-entries psa-fiche-vo-characteristics-list-cylindree")
                    car_displacement = car_displacement.find("span", class_="title-data").get_text().strip()
                    car["car_displacement"] = int(''.join(re.findall(r'\d+', car_displacement)))
                except:
                    car["car_displacement"] = None
                # car_consumption
                try:
                    car_consumption_div = soup.find_all("div",
                                                        class_="consumption-entrie psa-fiche-vo-summary-consumption-combined col-lg-12 col-md-12 col-sm-12 col-xs-12")
                    for car_consumption in car_consumption_div:
                        car_consumption = car_consumption.find("span", class_="title-data").get_text().strip()
                        if "l/100 km" in car_consumption:
                            car["car_consumption"] = float(car_consumption.replace(" l/100 km", ""))
                        else:
                            car["car_consumption"] = None

                except:
                    car["car_consumption"] = None
                # car_emission
                try:
                    car_emission_div = soup.find_all("div",
                                                     class_="consumption-entrie psa-fiche-vo-summary-consumption-road col-lg-12 col-md-12 col-sm-12 col-xs-12")
                    for car_emission in car_emission_div:
                        car_emission = car_emission.find("span", class_="title-data").get_text().strip()
                        if " g/km" in car_emission:
                            car["car_emission"] = float(car_emission.replace(" g/km", ""))
                        else:
                            car["car_emission"] = None
                except:
                    car["car_emission"] = None
                # car_options
                try:
                    car_options = []
                    options = soup.find_all("ul", class_="psa-fiche-vo-equipements-list")
                    for option in options:
                        equipements = option.find_all("li")
                        for equipement in equipements:
                            car_options.append(equipement.get_text().lower())
                    if car_options:
                        car["car_options"] = car_options
                except:
                    car["car_options"] = None
                # owner_phone_number
                try:
                    tel_number = soup.find("span", class_="pdv-phone telephone")
                    tel_number = tel_number.get_text().strip()
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
            response.close()
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
        logging.info(f"Your required features test is Valid ✅ 🎉")
    else:
        logging.info(f"Your required features test is Valid ❌")


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
    logging.info("Changing features types")
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
                logging.info(column, ' type is Not-Valid ❌')
                test = False
        if column in columns_to_double:
            if not (df[column].dtypes == float):
                logging.info(column, ' type is Not-Valid ❌')
                test = False
        if column in columns_to_bool:
            if not (df[column].dtypes == bool):
                logging.info(column, ' type is Not-Valid ❌')
                test = False
        if column in columns_to_datetime:
            if not (df[column].dtypes == 'datetime64[ns]'):
                logging.info(column, ' type is Not-Valid ❌')
                test = False
    if test:
        logging.info(f"Your features_type test is Valid ✅ 🎉")
    else:
        logging.info(f"Your features_type test is Valid ❌")


def remove_null_values_from_list_dict(list_dict):
    new_list = [remove_null_values_from_dict(dict_item=d) for d in list_dict]
    return new_list


def remove_null_values_from_dict(dict_item):
    new_dict = {k: v for k, v in dict_item.items() if v is not None}
    return new_dict



BASE_SRC = 'https://www.spoticar.fr'
BOT_NAME = 'spoticar_fr.bot'
spoticar_brands_list = get_brands()
spoticar_fr_pages_links = get_spoticar_fr_pages(500)
spoticar_fr_ads_links = get_spoticar_fr_car_links(spoticar_fr_pages_links)
cars_dataset = scrape_spoticar_fr(spoticar_fr_ads_links, spoticar_brands_list)
cars_dataset = remove_null_values_from_list_dict(cars_dataset)
dataset = pd.DataFrame(cars_dataset)
test_required_columns(dataset)
dataset = change_features_type(dataset)
test_column_types(dataset)
dataset.to_csv('Spoticar_fr_scraping.csv', encoding="utf-8")