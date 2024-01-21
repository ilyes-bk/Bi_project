import requests
import json
import pandas as pd
import time
from datetime import datetime
import logging

logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=print)


def carvago_ads_extraction():
    cars = []
    # change the region to choose the number of pages scraped
    for page in range(1, 200):
        try:
            data = {
                "page": page,
                "limit": 75,
                "sort": "publish-date",
                "direction": "desc",
                "pbt": False}
            print(f"Get cars from page : {page}")
            url = 'https://api.carvago.com/api/listedcars'
            print(f"Get cars from : {url}")
            x = requests.post(url, json=data, timeout=30)
            data = json.loads(x.text)
            print(len(data))
            for ad in data:
                try:
                    car = {}
                    car_data = ad
                    car['ad_url'] = car_data.get('external_url')
                    car['ad_title'] = car_data.get('title').lower()
                    car['car_brand'] = car_data.get('model_edition').get('model_family').get('make').get('name').lower()
                    car['car_model'] = car_data.get('model_edition').get('model_family').get('name').lower()
                    car['car_version'] = car_data.get('model_edition').get('name').lower()
                    car['ad_price'] = int(car_data.get('uniform_price'))
                    car['car_real_power'] = int(car_data.get('power'))
                    car['car_nb_seats'] = int(car_data.get('number_of_seats'))
                    car['car_energy'] = car_data.get('fuel_type').get('name').lower()
                    if car.get('car_energy') == "petrol":
                        car['car_energy'] = "essence"
                    if car.get('car_energy') == "electric":
                        car['car_energy'] = "electrique"
                    if car.get('car_energy') == "hybrid":
                        car['car_energy'] = "hybride"
                    if car.get('car_energy') == "hydrogen":
                        car['car_energy'] = "hydrogene"
                    if car.get('car_energy') == "lpg":
                        car['car_energy'] = "gpl"
                    car['car_transmission'] = car_data.get('transmission').get('name')
                    if car.get("car_transmission") == "automatic":
                        car['car_transmission'] = "automatique"
                    if car.get("car_transmission") == "manual":
                        car['car_transmission'] = "manuelle"
                    if car.get("car_transmission") == "semi-automatic":
                        car['car_transmission'] = "hybride"

                    car['car_consumption'] = None
                    try:
                        car['car_consumption'] = float(car_data.get('fuel_consumption_combined'))
                    except (ValueError, TypeError):
                        pass

                    car['car_weight'] = None
                    try:
                        car['car_weight'] = int(car_data.get('weight'))
                    except (ValueError, TypeError):
                        pass

                    car['car_gearbox'] = None
                    try:
                        car['car_gearbox'] = int(car_data.get('number_of_gears'))
                    except (ValueError, TypeError):
                        pass

                    car['car_emission'] = None
                    try:
                        car['car_emission'] = float(car_data.get('carbon_dioxide_emission'))
                    except (ValueError, TypeError):
                        pass

                    car['car_body'] = car_data.get('car_style').get('name')

                    car_reg_year = car_data.get('registration_date')
                    car['car_registration_year'] = None
                    try:
                        car['car_registration_year'] = pd.to_datetime(car_reg_year, yearfirst=True)
                    except (ValueError, TypeError):
                        pass

                    car['car_reg_year'] = None
                    try:
                        car['car_reg_year'] = int(car_reg_year[0:4])
                    except (ValueError, TypeError):
                        pass

                    car['car_nb_doors'] = None
                    try:
                        car['car_nb_doors'] = int(car_data.get('door_count').get('name')[2])
                    except (ValueError, TypeError, IndexError):
                        pass
                    car['ad_creation_date'] = car_data.get('created_at').get('date')
                    car['car_km'] = int(car_data.get('mileage'))
                    try:
                        car['car_color'] = car_data.get('color').get('name')
                    except:
                        car['car_color'] = car_data.get('color')
                    car['ad_crawling_date'] = None
                    try:
                        car['ad_crawling_date'] = car_data.get('first_crawl').get('date')
                    except:
                        pass

                    car['owner_loaction'] = None
                    try:
                        car['owner_loaction'] = car_data.get('location_city')
                    except:
                        pass

                    car['owner_street'] = None
                    try:
                        car['owner_street'] = car_data.get('location_street')
                    except:
                        pass

                    car['owner_country'] = None
                    try:
                        car['owner_country'] = car_data.get('location_country').get('name')
                    except:
                        pass

                    car['country_code'] = None
                    try:
                        car['country_code'] = car_data.get('location_country').get('iso_code')
                    except:
                        pass

                    car['ad_inactive'] = False

                    car['saler_type'] = None
                    try:
                        car['saler_type'] = car_data.get('seller').get('type').get('name')
                    except:
                        pass
                    if car['saler_type'] == 'Dealership':
                        car['saler_type'] = 'pro'
                    else:
                        car['saler_type'] = 'private'
                    car['img_uri'] = car_data.get('image').get('path')
                    car['owner_street'] = car_data.get('location_street')
                    options = car_data.get('features')
                    option_list = []
                    for i in options:
                        option_list.append(i.get('name'))
                    car['currency'] = "EUR"
                    car['car_options'] = option_list
                    car['ad_source'] = BASE_SRC
                    car['resulted_from'] = BOT_NAME
                    car['ad_inactive'] = False
                    car['data_type'] = "FULL"
                    car["ad_creation_date"] = datetime.utcnow()
                    car["ad_crawling_date"] = datetime.utcnow()
                    cars.append(car)
                except:
                    pass
            x.close()
            time.sleep(5)
        except:
            pass
    return cars


def change_features_type(df):
    columns_to_int = ['ad_price', 'car_km', 'car_reg_year', 'car_nb_doors', 'car_nb_seats', 'car_power',
                      'car_real_power', 'car_weight', 'car_displacement', 'car_gearbox']
    columns_to_double = ['car_consumption', 'car_emission', 'car_cylinder']
    columns_to_bool = ['ad_inactive']
    columns_to_datetime = ['car_registration_year', 'ad_creation_date', 'ad_crawling_date', 'ad_publish_date']
    for i in columns_to_int:
        if i in df.columns:
            df[i] = df[i].astype(float).astype('Int32')
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
        print(f"Your required features test is NOT Valid ❌")


def test_column_types(df):
    columns_to_int = ['ad_price', 'car_km', 'car_reg_year', 'car_nb_doors', 'car_nb_seats', 'car_power',
                      'car_real_power', 'car_weight', 'car_displacement', 'car_gearbox']
    columns_to_double = ['car_consumption', 'car_emission', 'car_cylinder']
    columns_to_bool = ['ad_inactive']
    columns_to_datetime = ['car_registration_year', 'ad_creation_date', 'ad_crawling_date', 'ad_publish_date']
    test = True
    for column in df.columns:
        if column in columns_to_int:
            if not (df[column].dtypes == 'Int32'):
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
        print(f"Your features_type test is NOT Valid ❌")


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



BASE_SRC = 'https://carvago.com'
BOT_NAME = 'carvago.bot'
cars = carvago_ads_extraction()
(cars)
dataset = pd.DataFrame(cars)
dataset = change_features_type(dataset)
test_required_columns(dataset)
test_column_types(dataset)
dataset.to_csv('carvago_scraping.csv', encoding="UTF-8")
# Serialize the data to a JSON-formatted string
json_string = json.dumps(cars, cls=DateTimeEncoder)
# Write the JSON string to a file
with open("carvago_scraping.json", "w") as json_file:
     json_file.write(json_string)