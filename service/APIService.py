import requests
import service.HandlingJson as HandlingJson
from . import KeyHandling
from datetime import datetime, timedelta
import pytz
from dateutil import parser


def get_json_data(json_data):
    try:
        author = json_data["author"]
        getData = {
            "user": {
                "id": author["id"],
                "username": author["username"]
            },
            "content": json_data["content"]
        }
        return getData
    except KeyError as e:
        print(f"Thiếu key trong JSON: {e}")
    except Exception as e:
        print(f"Lỗi khác: {e}")
    
    return None

def check_type_channel(channel_id, headers):
    url = f"https://discord.com/api/v9/channels/{channel_id}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        channel_data = response.json()
        channel_type = channel_data.get("type")
        return channel_type
    else:
        print(f"Lỗi: {response.status_code}, {response.text}")
    
    return -1

def get_data_to_forum_channel(channel_id, headers):
    url = f"https://discord.com/api/v10/channels/{channel_id}/threads"
    response = requests.get(url, headers=headers)

    list_id = []

    if response.status_code == 200:
        get_thread_json = response.json()
        for json in get_thread_json:
            thread_id = json.get("id")
            if thread_id:
                list_id.append(thread_id)
    else:
        print(f"Lỗi: {response.status_code}, {response.text}")

    return list_id

def handle_data_channel(list_channel_id, headers):
    utc_now = datetime.now(pytz.utc)
    start_of_day = utc_now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    url_base = f"https://discord.com/api/v10/channels/"

    data = []

    for get_id in list_channel_id:
        url = url_base + get_id + "/messages"

        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            messages = response.json()

            for msg in messages:
                msg_time = parser.isoparse(msg['timestamp'])

                if start_of_day <= msg_time < end_of_day:
                    get_data = get_json_data(msg)

                    if not get_data:
                        break

                    data.append(get_data)
                elif msg_time < start_of_day:
                    break
        else:
            print(f"Lỗi: {response.status_code}, {response.text}")
            
            return
        
    return data

def handle_channel_id(check_type, channel_id, headers):
    list_channel_id = []
    
    match check_type:
        case -1:
            print("Channel type error!")
            return
        case 0:
            list_channel_id.append(channel_id)
        case 15:
            list_channel_id = get_data_to_forum_channel(channel_id, headers)
            if not list_channel_id:
                print("List channel id null")
                return
        case _:
            print("Type channel nằm ngoài vùng cần get data")
    
    return list_channel_id

def retrieve_messages(channel_id):
    bot_token = KeyHandling.read_file_key("security/bot.key")
    
    headers = {
        "Authorization": bot_token
    }

    check_type = check_type_channel(channel_id, headers)

    list_channel_id = handle_channel_id(check_type, channel_id, headers)

    if not list_channel_id:
        print("List channel id null")
        return

    data = handle_data_channel(list_channel_id, headers)
    
    if data:
        file_path = "output/output.json"
        HandlingJson.write_file_json(file_path, data, False)

# def convert_json_to_response(response):
