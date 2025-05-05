import json
import os


LINK_HEAD = "E:/project/security/"

def read_json(name_file, checkout = True):
    if checkout:
        name_file_final = LINK_HEAD + name_file
    with open(name_file_final, "r", encoding="utf-8") as file:
        return json.load(file)

def write_file_json(file_path, data, checkout = True):
    if not data:
        print(f"Data write null: {file_path}")
        return
    if not file_path:
        print("Path file null")
        return
    
    if checkout:
        file_path = LINK_HEAD + file_path
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def append_file_json(file_path, data, checkout=True):
    if not data:
        print("Data append null")
        
        return
    if not file_path:
        print("Path file null")
        
        return
    
    if checkout:
        file_path = LINK_HEAD + file_path
    
    existing_data = []
    
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    print("Lỗi: File JSON không chứa danh sách (list).")
                    
                    return
        except json.JSONDecodeError:
            print("Lỗi: File JSON không hợp lệ.")
            
            return
        except Exception as e:
            print(f"Lỗi khi đọc file: {e}")
            
            return
    
    if isinstance(data, list):
        existing_data.extend(data)
    else:
        existing_data.append(data)
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Lỗi khi ghi file: {e}")