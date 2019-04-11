import csv
import requests
from token_generator import TokenGenerator
import json

INPUT_STATE = "MA"
INPUT_FILE_PATH = "./shelter/shelters_MA_ids_1.txt"

ANIMAL_TYPE_JSON_FILE_PATH = "./animal_type/animal_type.json"
BREED_JSON_FILE_PATH = "./breed/breed.json"

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
TYPE_ID = "type_id"
TYPE_NAME = "type_name"
BREED_NAME = "breed_name"
ANIMAL_IMAGE = "animal_image"

orgs_id_map = dict()
animal_type_map = dict()
breed_map = dict()
image_map = dict()


def get_orgs_id(file_path):
    ids = open(file_path, "r")
    for line in ids:
        parsed_line = line.split(" ")
        old_id = parsed_line[0]
        new_id = int(parsed_line[1][:-1])
        orgs_id_map[old_id] = new_id
    ids.close()


def get_from_animal_type_file(file_path):
    global animal_type_map
    file = open(file_path, "r")
    animal_type_map = json.load(file)
    file.close()


def get_from_breed_file(file_path):
    global breed_map
    file = open(file_path, "r")
    breed_map = json.load(file)
    file.close()


def add_to_animal_type(type):
    """Returns animal type id associated with input the type"""
    last_id = 0
    for id, animal_type in animal_type_map.items():
        last_id = max(last_id, int(id))
        if type == animal_type:
            return int(id)
    new_id = last_id + 1
    animal_type_map[new_id] = type
    return new_id


def add_to_breed(type, breed):
    """Returns breed id associated with the input breed"""
    type_id = add_to_animal_type(type)
    last_id = 0
    for breed_id, value in breed_map.items():
        last_id = max(last_id, int(breed_id))
        if breed == value[BREED_NAME] and type_id == value[TYPE_ID]:
            return int(breed_id)
    new_breed_id = last_id + 1
    breed_map[new_breed_id] = {BREED_NAME: breed, TYPE_ID: type_id}
    return new_breed_id


def add_to_image(animal_id, img_url=""):
    if animal_id in image_map.keys():
        image_map[animal_id].append(img_url)
    else:
        image_map[animal_id] = [img_url]


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
        if len(animal['photos']) > 0:
            add_to_image(animal['id'], img_url=animal['photos'][0]['medium'])
        parsed_animal = dict()
        parsed_animal[ANIMAL_ID] = animal['id']
        parsed_animal[ANIMAL_NAME] = animal['name']
        parsed_animal[GENDER] = animal['gender']
        parsed_animal[AGE] = animal['age']
        parsed_animal[SHELTER_ID] = shelter_id
        parsed_animal[BIO] = animal['description']
        parsed_animal[BREED_ID] = add_to_breed(animal['type'], animal['breeds']['primary'])
        parsed_animal[COLOR] = animal['colors']['primary']
        parsed_animal[SIZE] = animal['size']
        parsed_animal[MEDICAL_ID] = "none"
        parsed_animals.append(parsed_animal)
    return parsed_animals


def dump_json_to_file(json_data, file_path):
    file = open(file_path, "w")
    json.dump(json_data, file, indent=4)
    file.close()


def dump_as_csv(animals):
    animals_data = open('./animal/animals_' + INPUT_STATE + '.csv', 'w')
    csv_writer = csv.writer(animals_data)

    count = 0
    for animal in animals:
        if count == 0:
            col_names = [ANIMAL_ID, ANIMAL_NAME, GENDER, AGE, SHELTER_ID, BIO, BREED_ID, COLOR, SIZE, MEDICAL_ID]
            csv_writer.writerow(col_names)
            count += 1
        csv_writer.writerow([animal[ANIMAL_ID],
                             animal[ANIMAL_NAME],
                             animal[GENDER],
                             animal[AGE],
                             animal[SHELTER_ID],
                             animal[BIO],
                             animal[BREED_ID],
                             animal[COLOR],
                             animal[SIZE]])  # medical id is omitted
    animals_data.close()


def dump_animal_type_as_csv(animal_types):
    file = open("./animal_type/animal_type.csv", "w")
    csv_writer = csv.writer(file)

    count = 0
    for id, animal_type in animal_types.items():
        if count == 0:
            col_names = [TYPE_ID, TYPE_NAME]
            csv_writer.writerow(col_names)
            count += 1
        csv_writer.writerow([int(id), animal_type])
    file.close()


def dump_breed_as_csv(breeds):
    file = open("./breed/breed.csv", "w")
    csv_writer = csv.writer(file)

    count = 0
    for id, value in breeds.items():
        if count == 0:
            col_names = [BREED_ID, BREED_NAME, TYPE_ID]
            csv_writer.writerow(col_names)
            count += 1
        csv_writer.writerow([int(id), value[BREED_NAME], value[TYPE_ID]])
    file.close()

def dump_image_as_csv(images):
    file = open("./image/image.csv", "w")
    csv_writer = csv.writer(file)

    count = 0
    for id, value in images.items():
        if count == 0:
            col_names = [ANIMAL_ID, ANIMAL_IMAGE]
            csv_writer.writerow(col_names)
            count += 1
        for img_url in value:
            csv_writer.writerow([int(id), img_url])
    file.close()

def run():
    # get a valid token
    token_generator = TokenGenerator()
    token = token_generator.get_token()
    get_orgs_id(INPUT_FILE_PATH)
    get_from_animal_type_file(ANIMAL_TYPE_JSON_FILE_PATH)
    get_from_breed_file(BREED_JSON_FILE_PATH)

    animals_in_orgs = []
    for old_id in orgs_id_map.keys():
        new_id = orgs_id_map[old_id]
        animals = get_animals_of_org_id(token, old_id)
        animals_in_orgs += parse_animals_map(animals, new_id)

    dump_as_csv(animals_in_orgs)
    dump_json_to_file(animal_type_map, ANIMAL_TYPE_JSON_FILE_PATH)
    dump_json_to_file(breed_map, BREED_JSON_FILE_PATH)
    dump_animal_type_as_csv(animal_type_map)
    dump_breed_as_csv(breed_map)
    dump_image_as_csv(image_map)


if __name__ == '__main__':
    run()
