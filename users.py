from dontpad import dontpad
import os
import json

dontpad_link = '233450349853045APPLEBOT' # os.environ['DONTPAD_LINK']

# data = json.loads(dontpad.read(dontpad_link))
questions = json.load(open("questions.json"))

def read_from_dontpad():
    player_data = json.loads(dontpad.read(dontpad_link))
    return player_data

player_data = read_from_dontpad()

def remove_dupes_and_sort(input_list):
    t = list(set(input_list))
    t.sort()
    return t

def get_tags():
    core = questions['questions'][0]
    tags = dict()
    for topic in core:
        topic_tags = list()
        for questions_list in core[topic]:
            for tag in questions_list['tags']:
                topic_tags.append(tag)
        tags[topic] = remove_dupes_and_sort(topic_tags)
    return tags


tags = get_tags()


def add_player(id):
    players = player_data["players"]
    new_player_data = dict()
    new_player_data["id"] = id
    new_player_data["number_right"] = 0
    new_player_data["number_wrong"] = 0
    stats = dict()
    for topic in tags:
        stats[topic] = list()
        for tag in tags[topic]:
            tag_dict = dict()
            tag_dict["tag"] = tag
            tag_dict["wrong"] = 0
            tag_dict["right"] = 0
            stats[topic].append(tag_dict)
    new_player_data["stats"] = stats
    players.append(new_player_data)


def write_to_dontpad():
    json_string = json.dumps(player_data, indent=4, sort_keys=True)
    dontpad.write(dontpad_link, json_string)


def add_player_score_helper(player, subject, tag, right):
    tags = player["stats"][subject]
    for item in tags:
        if item["tag"] == tag:
            if right: 
                item["right"] += 1
                player["number_right"] += 1
            else: 
                item["wrong"] += 1
                player["number_wrong"] += 1 
            break
    else:    # if tag not added
        tag_dict = dict()
        tag_dict["tag"] = tag
        tag_dict["wrong"] = 0
        tag_dict["right"] = 0
        tags.append(tag_dict)


def add_player_score(id, subject, tags, right):
    for player in player_data["players"]:
        if player["id"] == id:
            for tag in tags:
                add_player_score_helper(player, subject, tag, right)
            break
    
    else:
        add_player(id)
        for player in player_data["players"]:
            if player["id"] == id:
                for tag in tags:
                    add_player_score_helper(player, subject, tag, right)
                break
    

def get_stats(player_id):
    for player in player_data["players"]:
        if player["id"] == player_id:
            stats_list = dict()
            for subject in player["stats"]:
                for topic in player["stats"][subject]: # iterate through all topics, get the nonzeroes
                    if topic['right'] != 0 or topic['wrong'] != 0:
                        try:
                            stats_list[subject].append(topic)
                        except:
                            stats_list[subject] = [topic]
            return stats_list
    else:
        return None

def get_player(id):
    for player in player_data["players"]:
        if player["id"] == id:
            return player
    return None