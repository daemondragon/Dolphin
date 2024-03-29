import requests
import csv
import os


def correct_float(value):
    return value.replace(",", ".")

def main():
    # To prevent pushing the values by mistakes on a public repo
    base_url = os.environ["JUMP_BASE_URL"]
    auth = (os.environ["JUMP_USER"], os.environ["JUMP_PWD"])

    url = base_url + "/asset?" + "&".join(["columns={}".format(column) for column in ["ASSET_DATABASE_ID", "LABEL", "TYPE", "LAST_CLOSE_VALUE_IN_CURR"]]) + "&date=2013-06-14"
    content = requests.get(url, auth=auth).json()

    with open("dataset/assets.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(["id", "name", "type", "value", "currency"])

        for asset in sorted(content, key=lambda asset: asset["ASSET_DATABASE_ID"]["value"]):

            # Remove asset that can't be used in the portfolio
            if "LAST_CLOSE_VALUE_IN_CURR" in asset and asset["TYPE"]["value"] in ["STOCK", "FUND"]:
                # Sometimes the value is not here.
                str_value = asset["LAST_CLOSE_VALUE_IN_CURR"]["value"].split(" ")

                value = correct_float(str_value[0])
                currency = str_value[1]

                writer.writerow([
                    asset["ASSET_DATABASE_ID"]["value"],
                    asset["LABEL"]["value"],
                    asset["TYPE"]["value"],
                    correct_float(str_value[0]),
                    str_value[1]
                ])
if __name__ == '__main__':
    main()
    print("done")
