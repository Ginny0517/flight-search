import requests
import datetime


TEQUILA_ENDPOINT = "https://api.tequila.kiwi.com/v2"
FLIGHT_SEARCH_ENDPOINT = "https://api.tequila.kiwi.com"
SEARCH_API = "04vLsODNkjgwvWBD_6c6xXG6v74zsSHw"
CITY_FROM = "TPE"


class FlightSearch:
    # This class is responsible for talking to the Flight Search API.
    def get_destination_code(self, city_name):
        location_endpoint = f"{FLIGHT_SEARCH_ENDPOINT}/locations/query"
        headers = {
            "apikey": SEARCH_API
        }
        query = {
            "term": city_name,
            "location_types": "city"
        }
        response = requests.get(url=location_endpoint, params=query, headers=headers)
        results = response.json()["locations"]
        code = results[0]["code"]
        return code

    def search_flight(self, code):
        today = datetime.datetime.now().strftime("%d/%m/%Y")
        date_to = (datetime.datetime.now() + datetime.timedelta(days=6 * 30)).strftime("%d/%m/%Y")
        search_endpoint = f"{TEQUILA_ENDPOINT}/search"
        header = {
            "apikey": SEARCH_API
        }

        query = {
            "fly_from": f"city:{CITY_FROM}",
            "fly_to": f"city:{code}",
            "date_from": today,
            "date_to": date_to,
            "nights_in_dst_from": 5,
            "nights_in_dst_to": 28,
            "flight_type": "round",
            "one_for_city": 1,
            "max_stopovers": 0,
            "curr": "USD"

        }

        response = requests.get(url=search_endpoint, headers=header, params=query)
        response.raise_for_status()
        try:
            data = response.json()["data"][0]
        except IndexError:
            query["max_stopovers"] = 2
            response = requests.get(url=search_endpoint, headers=header, params=query)
            data = response.json()["data"][0]
            return data
        else:
            return data
