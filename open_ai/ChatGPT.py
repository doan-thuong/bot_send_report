import os
import json
import requests
import service.HandlingJson as JsonService
import service.KeyHandling as KeyService


def create_first_request():
    return "Bạn là trợ lý ảo chuyên phân tích hội thoại công việc. Tôi sẽ lần lượt gửi cho bạn các đoạn JSON — mỗi đoạn là một tập hội thoại giữa các đồng nghiệp trong cùng một ngày làm việc. Bạn cần đọc và ghi nhớ nội dung các đoạn hội thoại đó để tôi có thể yêu cầu bạn tổng hợp sau. Không phản hồi gì cho đến khi tôi yêu cầu bằng một lệnh rõ ràng."

def create_request_no_prompt(path_file):
    data_from_file_json = JsonService.read_json(path_file, False)
    return json.dumps(data_from_file_json, indent=2)

def create_mid_command(path_file):
    data_from_file_json = JsonService.read_json(path_file, False)

    file_name = os.path.basename(path_file)
    file_stem = os.path.splitext(file_name)[0]

    prompt = f"""Dữ liệu từ file “{file_stem}” (số đoạn: {len(data_from_file_json)}) như sau: 
    {json.dumps(data_from_file_json, indent=2)}
    Hãy đọc và lưu nội dung, đừng phản hồi."""

    return prompt

def create_final_command():
    # prompt = f"""Bây giờ bạn hãy tổng hợp **báo cáo công việc** của ngày hôm đó:
    # - Dạng gạch đầu dòng, ngắn gọn, rõ trọng tâm
    # - Kèm dự đoán tiến độ tuần (nếu dữ liệu cho phép)
    # “Không có dữ liệu dự đoán, cứ bỏ qua”"""

    prompt = "Bây giờ hãy dừng lại và cho tôi biết bạn đã hiểu được những gì từ các tin nhắn trước của tôi. Không cần diễn giải lại yêu cầu, chỉ cần tóm tắt nội dung chính hoặc mô tả lại các ý tôi đã gửi theo cách bạn hiểu."

    return prompt

def request_gpt(prompt):
    api_key = KeyService.read_file_key("security/gpt.key")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "deepseek/deepseek-chat-v3-0324:free",
        "messages": [
            {"role": "system", "content": "Bạn là một nhà phân tích nội dung cuộc trò chuuyện, đồng thời là một người trợ lý cho nhân viên kiểm tra chất lượng sản phẩm và bạn cần trả lời ngắn gọn nhưng phải đủ ý."},
            {"role": "user", "content": prompt}
        ]
    }
    
    request_to_gpt = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data
    )

    if "application/json" in request_to_gpt.headers.get("Content-Type", "") and request_to_gpt.text.strip() and request_to_gpt.status_code == 200:
        response_json = request_to_gpt.json()
        response = response_json["choices"][0]["message"]["content"]
        
        # JsonService.write_file_json("output/output_gpt.json", response, False)

        return response
    else:
        print("Nội dung phản hồi:", request_to_gpt.text)
        return None