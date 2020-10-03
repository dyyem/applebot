import json, random

valid_subjects = ["chem", "phys"]
questions = json.load(open("questions.json"))

def generate(subject):
    qns_list = questions["questions"][0][subject]
    weights = [100 for x in range(qns_list)]
    return random.choice(qns_list)


for x in range(1,25):
    print(generate("chem")['id'])