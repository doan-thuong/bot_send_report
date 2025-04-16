import open_ai.ChatGPT as gpt


text = gpt.create_summary_command("output/output_gpt.json")

resp = gpt.request_gpt(text)
print(resp)