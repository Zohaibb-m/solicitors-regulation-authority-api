import requests
import os
from dotenv import load_dotenv
import pgeocode
import json
from tqdm import tqdm
import math
from geopy.geocoders import Nominatim, Photon
import time
import pandas as pd

load_dotenv()

class OrganizationDataMaker:
    def __init__(self):
        self.Ocp_Apim_Subscription_Key = os.getenv("Ocp_Apim_Subscription_Key")
        self.url_endpoint = "https://sra-prod-apim.azure-api.net/datashare/api/V1/organisation/GetAll"
        self.headers = {
            'Ocp-Apim-Subscription-Key': self.Ocp_Apim_Subscription_Key
        }
        self.pgeocode_nominatim = pgeocode.Nominatim("gb")
        self.geolocator_nominatim = Nominatim(user_agent="SRA_API_Testing")
        self.geolocator_photon = Photon(user_agent="SRA_API_Testing")

    def get_data_from_api(self):
        print("Fetching data from API...")
        response = requests.get(self.url_endpoint, headers=self.headers)
        print(f"API response status code: {response.status_code}")
        if response.status_code == 200:
           return response.text
        else:
            return None
    
    def get_coordinates_from_postcode(self, postcode):
        response = self.pgeocode_nominatim.query_postal_code(postcode)
        if response["latitude"] is not None and response["longitude"] is not None and not response.empty:
            return (float(response["latitude"]), float(response["longitude"]))
        else:
            return None, None
    
    def get_coordinates_from_address(self, address):
        retries = 0
        while retries < 2:
            try:
                location = self.geolocator_nominatim.geocode(address)
                if location:
                    return (location.latitude, location.longitude)
                else:
                    location = self.geolocator_photon.geocode(address)
                    if location:
                        return (location.latitude, location.longitude)
                    else:
                        return (None, None)
            except Exception as e:
                print(f"Error geocoding address {address}: {e}")
                retries += 1
                time.sleep(5)
        return (None, None)
        
    def process_organization_data(self):
        data = json.loads(self.get_data_from_api())
        if data is None:
            print("Failed to retrieve data from API")
            return
        
        count = 0

        if os.path.exists("app/data/processed_organizations.csv"):
            organization_df = pd.read_csv('app/data/processed_organizations.csv', encoding='ISO-8859-1')
        with open("app/data/processed_organizations.csv", 'a') as f:
            if not os.path.exists("app/data/processed_organizations.csv"):
                f.write("name,office_address,postcode,website,phone_number,email,coordinates\n")
            for organisation in tqdm(data["Organisations"], desc="Processing organizations"):
                if "ORG" in organisation["OrganisationType"]:
                    if organisation['PracticeName'] in organization_df['name'].values:
                        continue
                    for office in organisation["Offices"]:
                        office_address = ""
                        if office['Address1']:
                            office_address += office['Address1'] + ', '
                        if office['Address2']:
                            office_address += office['Address2'] + ', '
                        if office['Address3']:
                            office_address += office['Address3'] + ', '
                        if office['Address4']:
                            office_address += office['Address4'] + ', '
                        if office['Town']:
                            office_address += office['Town'] + ', '
                        if office['County']:
                            office_address += office['County'] + ', '
                        if office['Country']:
                            office_address += office['Country']
                        lat, lon = self.get_coordinates_from_postcode(office['Postcode'])
                        if lat is None or lon is None or math.isnan(lat) or math.isnan(lon):
                            continue
                        f.write(f"\"{organisation['PracticeName']}\",")
                        f.write(f"\"{office_address.rstrip(', ')}\",")
                        f.write(f"{office['Postcode']},")
                        f.write(f"{office['Website']},")
                        f.write(f"{office['PhoneNumber']},")
                        f.write(f"{office['Email']},")
                        f.write(f"\"({lat},{lon})\"\n")
                        count += 1
        print(f"Total organizations processed: {count}")
            
if __name__ == "__main__":
    org_data_maker = OrganizationDataMaker()
    org_data_maker.process_organization_data()