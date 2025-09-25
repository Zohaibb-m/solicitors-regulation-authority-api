import pandas as pd
from geopy import distance, Nominatim, Photon
import pgeocode
import time

class DistanceCalculator:
    def __init__(self):
        self.pgeocode_nominatim = pgeocode.Nominatim("gb")
        self.geolocator_nominatim = Nominatim(user_agent="SRA_API_Testing")
        self.geolocator_photon = Photon(user_agent="SRA_API_Testing")
        self.read_organization_data()
    
    def read_organization_data(self):
        self.organisation_df = pd.read_csv('app/data/processed_organizations.csv', encoding='ISO-8859-1')

    def calculate_distance(self, coord1, coord2):
        return distance.distance(coord1, coord2).km

    def get_5_closest_organizations(self, user_postcode):
        user_coordinates, location = self.get_coordinates_from_postcode(user_postcode)
        location = location.split(",")[0] if "," in location else location
        if user_coordinates == (None, None):
            user_coordinates = self.get_coordinates_from_address(user_postcode)
            if user_coordinates == (None, None):
                print("Could not determine coordinates for the provided postcode or address.")
                return None
        self.organisation_df["distance_km"] = self.organisation_df.apply(lambda row: self.calculate_distance(user_coordinates, eval(row['coordinates'])), axis=1)
        organisations_sorted = self.organisation_df.sort_values(by="distance_km")
        all_organisations = []
        for row in organisations_sorted.head(5).itertuples():
            org_info = {
                "organization_name": row.name,
                "office_address": row.office_address,
                "postcode": row.postcode,
                "website": "" if pd.isna(row.website) else row.website,
                "phone_number": "" if pd.isna(row.phone_number) else row.phone_number,
                "email": "" if pd.isna(row.email) else row.email,
                "distance_km": round(row.distance_km, 2)
            }
            all_organisations.append(org_info)
        return {"location": location, "organizations_count": 5, "organizations": all_organisations}

    def get_coordinates_from_postcode(self, postcode):
        response = self.pgeocode_nominatim.query_postal_code(postcode)
        if response["latitude"] is not None and response["longitude"] is not None and not response.empty:
            return ((float(response["latitude"]), float(response["longitude"])), response["place_name"])
        else:
            return(None, None), None
        
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
