LINK_HEAD = "E:/project/security/"

def read_file_key(path_file, checkout = True):
    if not path_file:
        return None

    try:
        if checkout:
            path_file = LINK_HEAD + path_file

        with open(path_file, "r") as key_file:
            return key_file.read()
    except FileNotFoundError:
        print(f"File not found: {path_file}")
        return None