import service.Service as Service
import service.HandlingJson as JsonService
import glob
import os
import requests


config = JsonService.read_json("config/config.json")
getRecipients = config["recipients"]

def send_discord_message(recipient):
    getMessage = Service.convert_to_messange()

    if not getMessage:
        return

    data = {
        "content": getMessage
    }
    
    Service.get_image()
    folder_name = "screenshots"
    image_files = glob.glob(os.path.join(folder_name, "*.png"))

    files = {f"file{i+1}": open(file_path, "rb") for i, file_path in enumerate(image_files)}
    
    response = requests.post(recipient, data=data, files=files)
    
    if response.status_code in [200, 204]:
        print(f"Sent message to {recipient}")
    else:
        print(f"Failed to send message to {recipient}, status: {response.status_code}")

print("Running...")
send_discord_message(getRecipients)