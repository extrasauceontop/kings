from sgrequests import SgRequests
import re
import json
import pandas as pd
import pgeocode
import requests

state_list = [
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
]

session = SgRequests()

locator_domains = []
page_urls = []
location_names = []
street_addresses = []
citys = []
states = []
zips = []
country_codes = []
store_numbers = []
phones = []
location_types = []
latitudes = []
longitudes = []
hours_of_operations = []

page = 1
page_size = 512
while True:
    print("going")
    url = "http://find.cashamerica.us/api/stores?p=" + str(page) + "&s=" + str(page_size) + "&lat=32.72&lng=-97.45&d=2021-03-26T16:00:44.978Z&key=D21BFED01A40402BADC9B931165432CD"
    print(url)
    response = requests.get(url).json()

    if "message" in response:
        print("failed")
        if page_size == 1:
            break
        tot_successful_records = page_size * page - 1

        page_size = int(page_size / 2)

        page = int(tot_successful_records / page_size)
        print("new page size: " + str(page_size))
        continue
    else:
        page = page + 1
    for location in response:
        locator_domain = "http://find.cashamerica.us/"
        page_url = url
        location_name = location["brand"]
        address = location["address"]["address1"]
        city = location["address"]["city"]
        state = location["address"]["state"]
        if state not in state_list:
            state = "<MISSING>"
        zipp = location["address"]["zipCode"]

        nomi = pgeocode.Nominatim("us")
        if nomi.query_postal_code(str(zipp))["country_code"] != "US":
            continue
        else:
            country_code = "US"
        store_number = location["storeNumber"]
        
        phone = ""
        x = 0
        for character in location["phone"]:
            if bool(re.search(r'\d', character)):
                phone = phone + character
        
        location_type = location_name
        latitude = location["latitude"]
        longitude = location["longitude"]
        
        hours = ""
        hours_data = requests.get("http://find.cashamerica.us/api/stores/"+ str(location["storeNumber"])+ "?key=D21BFED01A40402BADC9B931165432CD").json()

        for item in hours_data["weeklyHours"]:
            day = item["weekDay"]
            open_time = item["openTime"]
            close_time = item["closeTime"]

            hours = day + ": " + open_time + " - " + close_time + ", "
        
        hours = hours[:-2]

        locator_domains.append(locator_domain)
        page_urls.append(page_url)
        location_names.append(location_name)
        street_addresses.append(address)
        citys.append(city)
        states.append(state)
        zips.append(zipp)
        country_codes.append(country_code)
        store_numbers.append(store_number)
        phones.append(phone)
        location_types.append(location_type)
        latitudes.append(latitude)
        longitudes.append(longitude)
        hours_of_operations.append(hours)

df = pd.DataFrame(
    {
        "locator_domain": locator_domains,
        "page_url": page_urls,
        "location_name": location_names,
        "street_address": street_addresses,
        "city": citys,
        "state": states,
        "zip": zips,
        "store_number": store_numbers,
        "phone": phones,
        "latitude": latitudes,
        "longitude": longitudes,
        "hours_of_operation": hours_of_operations,
        "country_code": country_codes,
        "location_type": location_types,
    }
)

df["dupecheck"] = (
    df["location_name"]
    + df["street_address"]
    + df["city"]
    + df["state"]
    + df["location_type"]
)

df = df.drop_duplicates(subset=["dupecheck"])
df = df.drop(columns=["dupecheck"])
df = df.replace(r"^\s*$", "<MISSING>", regex=True)
df = df.fillna("<MISSING>")

df.to_csv("data.csv", index=False)