import csv
import requests
from token_generator import TokenGenerator

INPUT_STATE = "MA"
INPUT_FILE_PATH = "./shelters/shelters_MA_ids_1.txt"

ANIMAL_ID = "animal_id"
ANIMAL_NAME = "animal_name"
GENDER = "gender"
AGE = "age"
SHELTER_ID = "shelter_id"
BIO = "bio"
BREED_ID = "breed_id"
COLOR = "color"
SIZE = "size"
MEDICAL_ID = "medical_id"
orgs_id_map = dict()


def get_orgs_id(file_path):
    ids = open(file_path, "r")
    for line in ids:
        parsed_line = line.split(" ")
        old_id = parsed_line[0]
        new_id = int(parsed_line[1][:-1])
        orgs_id_map[old_id] = new_id
    ids.close()


def get_animals_of_org_id(token, org_id):
    url = "https://api.petfinder.com/v2/animals?organization=" + org_id
    print("GET request:", url)
    bearer_token = "Bearer " + token
    header = {"Authorization": bearer_token}
    raw_data = requests.get(url, headers=header)
    if raw_data.status_code == 401:
        raise raw_data.raise_for_status()
    else:
        data = raw_data.json()
        return data


def parse_animals_map(animals_map, shelter_id):
    parsed_animals = []
    animals = animals_map['animals']

    for animal in animals:
        parsed_animal = dict()
        parsed_animal[ANIMAL_ID] = animal['id']
        parsed_animal[ANIMAL_NAME] = animal['name']
        parsed_animal[GENDER] = animal['gender']
        parsed_animal[AGE] = animal['age']
        parsed_animal[SHELTER_ID] = shelter_id
        parsed_animal[BIO] = animal['description']
        parsed_animal[BREED_ID] = animal['breeds']['primary']
        parsed_animal[COLOR] = animal['colors']['primary']
        parsed_animal[SIZE] = animal['size']
        parsed_animal[MEDICAL_ID] = "none"
        parsed_animals.append(parsed_animal)
    return parsed_animals


def dump_as_csv(animals):
    animals_data = open('./animals/animals_' + INPUT_STATE + '.csv', 'w')
    csvwriter = csv.writer(animals_data)

    count = 0
    for animal in animals:
        if count == 0:
            col_names = [ANIMAL_ID, ANIMAL_NAME, GENDER, AGE, SHELTER_ID, BIO, BREED_ID, COLOR, SIZE, MEDICAL_ID]
            csvwriter.writerow(col_names)
            count += 1
        csvwriter.writerow([animal[ANIMAL_ID],
                            animal[ANIMAL_NAME],
                            animal[GENDER],
                            animal[AGE],
                            animal[SHELTER_ID],
                            animal[BIO],
                            animal[BREED_ID],
                            animal[COLOR],
                            animal[SIZE],
                            animal[MEDICAL_ID]])
    animals_data.close()


def run():
    # get a valid token
    token_generator = TokenGenerator()
    token = token_generator.get_token()
    get_orgs_id(INPUT_FILE_PATH)

    animals_in_orgs = []
    for old_id in orgs_id_map.keys():
        new_id = orgs_id_map[old_id]
        animals = get_animals_of_org_id(token, old_id)
        animals_in_orgs += parse_animals_map(animals, new_id)

    dump_as_csv(animals_in_orgs)


if __name__ == '__main__':
    run()
