import json

mcq = ["phys", "chem", "bio"]
maths = ["amath", "emath"]

mcq_valids = [".A", ".B", ".C", ".D"]


def answer_validator(subject, answer):
    if subject in mcq:
        return answer in mcq_valids
        
    if subject in maths:

        try: 
            float(answer[1:]) # see if it can be converted into a float
            return True
        except:
            return False

    else: 
        print("Topic not valid")


def reformat():
    with open("questions.json") as questions_json, open("reformat.json", "w") as reformat_file:
        data = json.load(questions_json)
        json.dump(data, reformat_file, indent=4)

reformat()