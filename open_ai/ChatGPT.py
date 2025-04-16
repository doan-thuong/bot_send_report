import openai
import json
import requests
import service.Service as service


def create_content_request(path_file):
    data_from_file_json = service.read_json(path_file)

    prompt = f"""
    Dưới đây là một chuỗi JSON chứa các đoạn hội thoại trao đổi công việc giữa các đồng nghiệp trong một ngày.
    Hãy phân tích và viết lại **báo cáo công việc** của ngày hôm đó, dưới dạng **các gạch đầu dòng**, ngắn gọn, rõ ràng và đúng trọng tâm.
    JSON tin nhắn:
    {json.dumps(data_from_file_json, indent=2)}
    """

    return prompt

def create_summary_command(path_file):
    data_from_file_json = service.read_json(path_file)

    prompt = f"Bạn hãy đọc dữ liệu tôi cung cấp và hãy tìm hiểu xem đó là gì. Dữ liệu như sau: {json.dumps(data_from_file_json, indent=2)}"

    return prompt

def request_gpt(prompt):
    with open("security/gpt.key", "r") as key_file:
        api_key = key_file.read()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://localhost",
        "X-Title": "Request GPT"
    }

    data = {
        "model": "openchat/openchat-3.5-0106",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    request_to_gpt = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data
    )

    response_json = request_to_gpt.json()
    service.write_file_json("output/output_gpt.json", response_json)

    response = response_json["choices"][0]["message"]["content"]
    return response