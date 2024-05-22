import streamlit as st
import numpy as np
import pandas as pd
import json
import pickle
import os
import folium
from folium.plugins import HeatMap
from scipy import stats
from collections import Counter
from streamlit_folium import st_folium
from dotenv import load_dotenv

load_dotenv()

collaborative_filename = os.getenv("RECO_COLLABORATIVE_FILE")
content_filename = os.getenv("RECO_CONTENT_FILE")
zip_code_file = os.getenv("RECO_ZIP_FILE")
cold_start_filename = os.getenv('RECO_COLD_START_FILE')
resto_filename = os.getenv('RECO_RESTO_LIST_FILE')

# Reading the files
user_ids = {}
with open(collaborative_filename, 'r') as fp:
    # Load data from the file
    data = json.load(fp)
    # Merge the loaded data into the user_ids dictionary
    user_ids.update(data)

with open(content_filename, 'r') as fp:
    store_restaurants_content = json.load(fp)

zips = pd.read_csv(zip_code_file, sep=',', quotechar='"', converters={'geopoint': eval})
zips['postal code'] = zips['postal code'].astype(str)

restaurants = pd.read_pickle(resto_filename)

cold_start_by_zip = pd.read_csv(cold_start_filename)

zip_codes = restaurants['postal_code'].unique().tolist()
locations = {item['postal code']: item['geopoint'] for index, item in zips.iterrows() if
             item['postal code'] in zip_codes}


def distance(coord1, coord2):
    R = 6373.0
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    lat1, lon1 = np.radians(lat1), np.radians(lon1)
    lat2, lon2 = np.radians(lat2), np.radians(lon2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    dist = R * c / 1.6
    return dist


def get_restaurants_by_usr_id(df, usr_id):
    store_restaurants = []
    df_colab = restaurants[restaurants['business_id'].isin([item[0] for item in user_ids[usr_id]])]
    df_content = restaurants[restaurants['business_id'].isin([item for item in store_restaurants_content[usr_id]])]
    df_rest = pd.concat([df_colab, df_content])
    df_rest.drop_duplicates(subset=['business_id'],inplace=True)

    for index, row in df_rest.iterrows():
        restaurant_details = {}
        restaurant_details['Name'] = row['name']
        restaurant_details['Address'] = row['address']
        restaurant_details['Zip Code'] = row['postal_code']
        restaurant_details['Latitude'] = row['latitude']
        restaurant_details['Longitude'] = row['longitude']

        restaurant_details['Category'] = row['sep_categories']
        restaurant_details['Topics'] = row['Topics']
        restaurant_details['Stars'] = row['stars']
        store_restaurants.append(restaurant_details)
    return sorted(store_restaurants, key=lambda x: x['Stars'], reverse=True)


def get_cold_start(df, zip_code):
    store_restaurants = []

    data = df.loc[df['postal_code'] == zip_code]

    for index, row in data.iterrows():
        restaurant_details = {}
        restaurant_details['Name'] = row['name']
        restaurant_details['Address'] = row['address']
        restaurant_details['Zip Code'] = str(row['postal_code'])
        restaurant_details['Latitude'] = row['latitude']
        restaurant_details['Longitude'] = row['longitude']

        restaurant_details['Category'] = row['sep_categories']
        restaurant_details['Topics'] = row['Topics']
        restaurant_details['Stars'] = row['stars']
        store_restaurants.append(restaurant_details)
    return sorted(store_restaurants, key=lambda x: x['Stars'], reverse=True)

user_ids_final=list(user_ids.keys())
user_ids_final.append('000_new_user')

def main():
    st.title("Nashville Restaurant Recommendation App")
    st.subheader("Personalized Recommendation & Cold Start Handling")
    user_id = st.selectbox("User ID", sorted(user_ids_final))
    zip_code = st.selectbox("Zip Code", sorted(locations.keys()))
    distance_input = st.text_input("Distance (in miles)")

    if st.button("Submit"):
        if distance_input:
            proximity = float(distance_input)
            if user_id == '000_new_user':
                store_rest = get_cold_start(cold_start_by_zip, int(zip_code))
            else:
                store_rest = get_restaurants_by_usr_id(restaurants, user_id)
                store_rest = [item for item in store_rest if
                            distance(locations[zip_code], locations[item['Zip Code']]) < proximity]
            if len(store_rest)<1:
                store_rest = get_cold_start(cold_start_by_zip, zip_code)
            store_rest = [item for item in store_rest if
                            distance(locations[zip_code], locations[item['Zip Code']]) < proximity]
            if len(store_rest)>0:
                nash_coordinates = [36.174465, -86.767960]
                folium_map = folium.Map(location=nash_coordinates, tiles="cartodbpositron", width=1200, height=600,
                                            zoom_start=12)

                for restaurant in store_rest:
                    coordinates = restaurant['Latitude'], restaurant['Longitude']
                    html = f'''<strong>Name:</strong> {restaurant['Name']}<br>
                            <strong>Categories:</strong> {restaurant['Category']}<br>
                            <strong>Amenities:</strong> {restaurant['Topics']}<br>
                            <strong>Rating:</strong> {restaurant['Stars']}
                            '''

                    iframe = folium.IFrame(html,
                                            width=200,
                                            height=200)
                    popup = folium.Popup(iframe,
                                            max_width=200)
                    folium.Marker(coordinates, popup=popup).add_to(folium_map)
                data = [(restaurant['Latitude'], restaurant['Longitude']) for restaurant in store_rest]
                HeatMap(data).add_to(
                    folium.FeatureGroup(name='Heat Map').add_to(folium_map))
                st_data = st_folium(folium_map, width=725,returned_objects=[])
            else:
                st.write('no found')


if __name__ == '__main__':
    main()