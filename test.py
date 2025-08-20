import json
import random as rdm

filename = "test.json"



names_list = ["Scott", "Ryan", "Sam", "Zoe"]
rooms_list = ["kitchen", "bathroom", "bedroom", "hallway", "living room", "dining room"]


lucky_dict = {}

for _ in range(50):
    name_choice = rdm.choice(names_list)
    room_choice = rdm.choice(rooms_list)
    lucky_dict[name_choice] = room_choice
    with open(filename, "a") as f:
        f.write(json.dumps(lucky_dict, indent=2) + "\n")