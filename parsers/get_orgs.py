import csv
import requests
from token_generator import TokenGenerator

INPUT_STATE = "MA"

SHELTER_ID = "shelter_id"
SHELTER_NAME = "shelter_name"
ADDRESS = "address"
CITY = "city"
STATE = "state"
POSTCODE = "postcode"
EMAIL_ADDRESS = "email_address"
PHONE_NUMBER = "phone_number"


def get_orgs_data(token, state):
    url = "https://api.petfinder.com/v2/organizations?location=" + state
    bearer_token = "Bearer " + token
    header = {"Authorization": bearer_token}
    raw_data = requests.get(url, headers=header)
    if raw_data.status_code == 401:
        raise raw_data.raise_for_status()
    else:
        data = raw_data.json()
        return data


def get_metadata():
    file = open("./shelter/shelters_metadata.txt", "r")
    line = file.readline()
    metadata = line.split(" ")
    last_file_id = int(metadata[1].split("=")[1])
    last_org_id = int(metadata[2].split("=")[1])
    file.close()
    return last_file_id, last_org_id


def write_to_file(file_id, org_id, text):
    metadata_file = open("./shelter/shelters_metadata.txt", "w")
    metadata_file.write("METADATA last_file=" + str(file_id) + " last_id=" + str(org_id))
    metadata_file.close()

    orgs_data_file = open("./shelter/shelters_" + INPUT_STATE + "_ids_" + str(file_id) + ".txt", "w")
    orgs_data_file.write(text)
    orgs_data_file.close()


def dump_as_csv(orgs_map):
    # a list of parsed organizations
    parsed_orgs = []
    # a list of raw organizations from the json object
    orgs = orgs_map['organizations']

    # store all org data in a list of dicts
    metadata = get_metadata()
    file_id = metadata[0]
    file_id += 1
    org_id = metadata[1]

    content = ""
    for org in orgs:
        org_id += 1
        content += org['id'] + " " + str(org_id) + "\n"
        parsed_org = dict()
        parsed_org[SHELTER_ID] = org_id
        parsed_org[SHELTER_NAME] = org['name']
        address_map = org['address']
        parsed_org[ADDRESS] = address_map['address1']
        parsed_org[CITY] = address_map['city']
        parsed_org[STATE] = address_map['state']
        parsed_org[POSTCODE] = address_map['postcode']
        parsed_org[EMAIL_ADDRESS] = org['email']
        parsed_org[PHONE_NUMBER] = org['phone']
        parsed_orgs.append(parsed_org)

    shelter_data = open('./shelter/shelters_' + INPUT_STATE + '.csv', 'w')
    csvwriter = csv.writer(shelter_data)

    count = 0
    for org in parsed_orgs:
        if count == 0:
            col_names = [SHELTER_ID, SHELTER_NAME, ADDRESS, CITY, STATE, POSTCODE, EMAIL_ADDRESS, PHONE_NUMBER]
            csvwriter.writerow(col_names)
            count += 1
        csvwriter.writerow([org[SHELTER_ID],
                            org[SHELTER_NAME],
                            org[ADDRESS],
                            org[CITY],
                            org[STATE],
                            org[POSTCODE],
                            org[EMAIL_ADDRESS],
                            org[PHONE_NUMBER]])
    shelter_data.close()
    write_to_file(file_id, org_id, content)


def run():
    # get a valid token
    token_generator = TokenGenerator()
    token = token_generator.get_token()
    # get organizations raw data (dict)
    orgs = get_orgs_data(token, INPUT_STATE)
    # dump shelters info to a csv file
    dump_as_csv(orgs)


if __name__ == '__main__':
    run()
