import os
import json
import requests
import service.HandlingJson as JsonService


def create_first_request():
    prompt = f"""
    Dưới đây gửi cho bạn nhiều chuỗi JSON chứa các đoạn hội thoại trao đổi công việc giữa các đồng nghiệp trong một ngày.
    Tôi cần bạn đọc và hiểu nội dung để thực hiện các yêu cầu của tôi sau này.
    Sau đây tôi sẽ gửi bạn nội dung bạn chỉ cần nhận thông tin và phân tích ngầm thôi không cần gửi lại phần phân tích ngay.
    """

    return prompt

def create_mid_command(path_file):
    data_from_file_json = JsonService.read_json(path_file)

    file_name = os.path.basename(path_file)
    file_stem = os.path.splitext(file_name)[0]

    prompt = f"""Đây là dữ liệu của file {file_stem} như sau: 
    {json.dumps(data_from_file_json, indent=2)}"""

    return prompt

def create_final_command():
    prompt = f"""Dựa vào những gì tôi vừa cung cấp bạn hãy phân tích và viết lại **báo cáo công việc** của ngày hôm đó, 
    dưới dạng **các gạch đầu dòng**, ngắn gọn, rõ ràng và đúng trọng tâm. 
    Đồng thời có bạn có thể đưa ra dự đoán về tiến độ công việc có thể hoàn thành trong tuần hay không 
    **Không bắt buộc, nếu đủ dữ liệu để dự đoán**"""

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
    JsonService.write_file_json("output/output_gpt.json", response_json)

    response = response_json["choices"][0]["message"]["content"]
    return response