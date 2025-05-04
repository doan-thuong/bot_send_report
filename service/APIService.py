import requests
import service.HandlingJson as HandlingJson
from . import KeyHandling
from datetime import datetime, timedelta
import pytz
from dateutil import parser


def get_json_data(json_data):
    try:
        author = json_data["author"]

        attachments = json_data["attachments"]

        get_attachments = []

        if attachments:
            for attachment in attachments:
                get_attachments.append(attachment["content_type"])

        getData = {
            "sender": {
                "id": author["id"],
                "username": author["username"]
            },
            "timestamp": json_data["timestamp"],
            "attachments": get_attachments,
            "content": json_data["content"]
        }
        return getData
    except KeyError as e:
        print(f"Thiếu key trong JSON: {e}")
    except Exception as e:
        print(f"Lỗi khác: {e}")
    
    return None

def get_name_channel(id_channel, headers):
    url = f"https://discord.com/api/v10/channels/{id_channel}"
    response_channel = requests.get(url, headers=headers)

    channel_name = None
    if response_channel.status_code == 200:
        channel_info = response_channel.json()
        channel_name = channel_info["name"]
    else:
        print(f"Lỗi khi lấy thông tin kênh: {response_channel.status_code}, {response_channel.text}")

    return channel_name

def check_data_channel(channel_id, headers):
    url = f"https://discord.com/api/v9/channels/{channel_id}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        channel_data = response.json()
        
        channel_type = channel_data["type"]
        return {
            "type" : channel_type,
            "name" : channel_data["name"]
        }
    else:
        print(f"Lỗi: {response.status_code}, {response.text}")
    
    return {
        "type" : -1,
        "name" : None
    }

def get_data_to_forum_channel(channel_id, headers):
    list_id = []

    endpoints = [
        f"https://discord.com/api/v10/channels/{channel_id}/threads/search?archived=false",
        f"https://discord.com/api/v10/channels/{channel_id}/threads/archived/public",
        f"https://discord.com/api/v10/channels/{channel_id}/users/@me/threads/archived/private"
    ]

    for url in endpoints:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            res_json = response.json()
            threads = res_json.get("threads", [])

            for thread in threads:
                thread_id = thread.get("id")
                if thread_id:
                    list_id.append(thread_id)
        else:
            print(f"❌ Lỗi khi gọi {url}: {response.status_code}, {response.text}")

    return list_id

def get_messages_in_day(channel_id, headers):
    utc_now = datetime.now(pytz.utc)
    start_of_day = utc_now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)
    
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Lỗi khi lấy tin nhắn từ kênh {channel_id}: {response.status_code}, {response.text}")
        return None
    
    messages = response.json()
    filtered_messages = []
    
    for msg in messages:
        msg_time = parser.isoparse(msg['timestamp'])
        if start_of_day <= msg_time < end_of_day:
            get_data_json = get_json_data(msg)
            if get_data_json:
                filtered_messages.append(get_data_json)
        elif msg_time < start_of_day:
            break
    
    return filtered_messages

def process_channel_data(channel_id, headers):
    name_channel = get_name_channel(channel_id, headers)
    if not name_channel:
        print(f"Không thể lấy tên kênh cho ID {channel_id}")
        return None
    
    messages = get_messages_in_day(channel_id, headers)
    if messages is None or not messages:
        return None
    
    return {
        "name_channel": name_channel,
        "data_channel": messages
    }

def handle_data_channel(list_channel_id, headers):
    data = []
    for channel_id in list_channel_id:
        channel_data = process_channel_data(channel_id, headers)
        if channel_data:
            data.append(channel_data)
    return data

def handle_channel_id(check_type, channel_id, headers):
    list_channel_id = []
    
    match check_type:
        case 0:
            list_channel_id.append(channel_id)
        case 15:
            list_channel_id = get_data_to_forum_channel(channel_id, headers)
            if not list_channel_id:
                print("List channel id in forum null")
                return
        case _:
            print("Type channel nằm ngoài vùng cần get data")
    
    return list_channel_id

def retrieve_messages(channel_id):
    bot_token = KeyHandling.read_file_key("security/bot.key")
    
    headers = {
        "Authorization": bot_token
    }

    data_check = check_data_channel(channel_id, headers)

    check_type = data_check["type"]

    if check_type == -1:
        print("Channel type error!")
        return

    list_channel_id = handle_channel_id(check_type, channel_id, headers)

    if not list_channel_id:
        print("List channel id null")
        return

    if check_type != 15:
        data = handle_data_channel(list_channel_id, headers)
    else:
        data = {
            "name_channel" : data_check["name"],
            "content_channel": handle_data_channel(list_channel_id, headers)
        }
    
    if data:
        file_path = "output/output.json"
        HandlingJson.write_file_json(file_path, data, False)

# def convert_json_to_response(response):
