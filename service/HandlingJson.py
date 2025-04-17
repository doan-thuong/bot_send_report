import json


LINK_HEAD = "E:/project/security/"

def read_json(name_file):
  name_file_final = LINK_HEAD + name_file
  with open(name_file_final, "r", encoding="utf-8") as file:
    return json.load(file)

def write_file_json(file_path, data, checkout = True):
    if not data:
        print("Data write null")
        return
    if not file_path:
        print("Path file null")
        return
    
    if checkout:
        file_path = LINK_HEAD + file_path
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)