import requests
import csv
import os

# To prevent pushing the values by mistakes on a public repo
base_url = os.environ["JUMP_BASE_URL"]
auth = (os.environ["JUMP_USER"], os.environ["JUMP_PWD"])

destination_currency = "EUR"
currencies = ["EUR", "GBP", "JPY", "NOK", "SEK", "USD"]

def get_url(source, destination):
    global base_url
    return base_url + "/currency/rate/{}/to/{}".format(source, destination)

def correct_float(value):
    return value.replace(",", ".")

with open("dataset/euros_rate.csv", "w") as file:
    writer = csv.writer(file)
    writer.writerow(["source", "destination", "rate"])
    for source in currencies:

        response = requests.get(get_url(source, destination_currency), auth=auth)
        try:
            writer.writerow([source, destination_currency, correct_float(response.json()["rate"]["value"])])
        except Exception as e:
            # Try the other way to get it
            response = requests.get(get_url(destination_currency, source), auth=auth)

            try:
                writer.writerow([source, destination_currency, str(1 / float(correct_float(response.json()["rate"]["value"])))])
            except Exception as e:
                print("Could not get conversion from {} to {}".format(source, destination_currency))

