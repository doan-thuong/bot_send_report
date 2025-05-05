import open_ai.ChatGPT as gpt
import service.APIService as api
from service import HandlingJson as JsonService

def request_auto_report():
    # meeting note, build android, build ios, qa chat
    channels_id = ["", "1125361289351409694", "1168900403350487171", "1273327902901141687", "1343963851661774989", ""]
    list_name_channel = []
    response = None

    for channel in channels_id:
        if not channel: continue
        
        name = api.retrieve_messages(channel)
        list_name_channel.append(name)

    for i in range(len(channels_id)):
        path_file = f"output_channel/{list_name_channel[i]}.json"
        
        if i == 0:
            text = gpt.create_first_request()

        elif i == 1:
            content = gpt.create_request_no_prompt(path_file, True)
            text = f"Sau đây là dữ liệu từ kênh meeting note - nơi sẽ đặt mục tiêu cho tuần. Dữ liệu như sau: {content}"
        
        elif i == len(channels_id) - 1:
            text = gpt.create_final_command()
            response = gpt.request_gpt(text)
            continue
        
        else:
            text = gpt.create_mid_command(path_file)
        
        gpt.request_gpt(text)

    return response


response = request_auto_report()
if response:
    path_file = "output/output_gpt.json"
    JsonService.write_file_json(path_file, response)