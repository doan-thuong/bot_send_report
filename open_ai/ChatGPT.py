import os
import json
import requests
import service.HandlingJson as JsonService


def create_first_request():
    return "Bạn là trợ lý ảo chuyên phân tích hội thoại công việc. Tôi sẽ lần lượt gửi cho bạn các đoạn JSON — mỗi đoạn là một tập hội thoại giữa các đồng nghiệp trong cùng một ngày làm việc. Bạn cần đọc và ghi nhớ nội dung các đoạn hội thoại đó để tôi có thể yêu cầu bạn tổng hợp sau. Không phản hồi gì cho đến khi tôi yêu cầu bằng một lệnh rõ ràng."

def create_request_no_prompt(path_file):
    data_from_file_json = JsonService.read_json(path_file)
    return json.dumps(data_from_file_json, indent=2)

def create_mid_command(path_file):
    data_from_file_json = JsonService.read_json(path_file)

    file_name = os.path.basename(path_file)
    file_stem = os.path.splitext(file_name)[0]

    prompt = f"""Dữ liệu từ file “{file_stem}” (số đoạn: {len(data_from_file_json)}) như sau: 
    {json.dumps(data_from_file_json, indent=2)}
    Hãy đọc và lưu nội dung, đừng phản hồi."""

    return prompt

def create_final_command():
    prompt = f"""Bây giờ bạn hãy tổng hợp **báo cáo công việc** của ngày hôm đó:
    - Dạng gạch đầu dòng, ngắn gọn, rõ trọng tâm
    - Kèm dự đoán tiến độ tuần (nếu dữ liệu cho phép)
    “Không có dữ liệu dự đoán, cứ bỏ qua”"""

    return prompt

def request_gpt(prompt):
    with open("E:/project/security/security/gpt.key", "r") as key_file:
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