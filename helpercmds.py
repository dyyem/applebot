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
