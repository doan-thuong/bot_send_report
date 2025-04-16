import os
import glob
import gspread
import yagmail
from datetime import datetime, timedelta

from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from cryptography.fernet import Fernet

import JsonHandling

LINK_HEAD = "E:/project/security/"

def decrypt_password(encrypted_password: str) -> str:
    path = LINK_HEAD + "security/secret.key"
    with open(path, "rb") as key_file:
        saved_key = key_file.read()
    
    cipher_suite = Fernet(saved_key)

    decrypted_password = cipher_suite.decrypt(encrypted_password.encode())

    return decrypted_password.decode()

def convert_time(time, time_offset):
  set_time = datetime.strptime(time, "%H:%M")
  int_time_offset = int(time_offset)

  time_result = set_time - timedelta(hours=int_time_offset)
  final_time = time_result.strftime("%H:%M")
  
  return final_time

def send_noti(content_mail):
  config_mail = JsonHandling.read_json("config/config-mail.json")

  mail_from = config_mail["mail_from"]
  mail_to = config_mail["mail_to"]
  app_password = config_mail["app_password"]
  
  yag = yagmail.SMTP(mail_from, app_password)
  yag.send(
    to=mail_to,
    subject="Thông báo!!!",
    contents=content_mail
  )

def get_data_from_gg_sheet(id_sheet, name_tab_sheet):
  config = JsonHandling.read_json("config/config-mail.json")
  scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
  creds = ServiceAccountCredentials.from_json_keyfile_name(LINK_HEAD + "config/key-gg-config.json", scope)
  client = gspread.authorize(creds)

  spreadsheet = client.open_by_key(id_sheet)
  sheets = [ws.title for ws in spreadsheet.worksheets()]
  
  if name_tab_sheet not in sheets:
    
    not_found = config["not_found_sheet"]
    
    send_noti(f"{not_found} {name_tab_sheet}")
    return None

  sheet = spreadsheet.worksheet(name_tab_sheet)
  data = sheet.col_values(1)

  if len(data) == 0:
    null_data = config["not_data_sheet"]
    
    send_noti(f"{null_data} từ {name_tab_sheet}")
    return None
  
  return data

def convert_to_messange():
  name_tab_sheet = str(datetime.today().strftime('%Y-%m-%d'))
  title_mess = f"Test report {name_tab_sheet}:\n"
  file_config = JsonHandling.read_json("config/config.json")
  id_pm = file_config["id_pm"]

  links_to_sheet = file_config["sheet_url"]
  link_to_sheet = ""
  for link in links_to_sheet:
    link_to_sheet += "Link: " + link +"\n"
  
  id_sheet = file_config["id_sheet"]
  tag_pm = f"anh <@{id_pm}>"
  
  data = get_data_from_gg_sheet(id_sheet, name_tab_sheet)
  if data is None:
    return None

  i = 0
  while i < len(data):
    if str(data[i]).strip() == "":
      del data[i]
    else:
      data[i] = "- " + str(data[i])
      i += 1
  
  message = title_mess + "\n".join(map(str, data)) + "\n" + link_to_sheet + tag_pm

  return message

def login_google(driver, email, password):
  driver.get("https://accounts.google.com/signin")

  wait = WebDriverWait(driver, 10)

  email_input = driver.find_element(By.ID, "identifierId")
  email_input.send_keys(email)
  email_input.send_keys(Keys.RETURN)

  wait.until(EC.presence_of_element_located((By.NAME, "Passwd")))

  password_input = driver.find_element(By.NAME, "Passwd")
  password_input.send_keys(password)
  password_input.send_keys(Keys.RETURN)
  print(driver.current_url)

  try:
      wait.until(EC.presence_of_element_located((By.ID, "idvPreregisteredPhone")))
      print("Google yêu cầu xác thực 2 bước. Hãy xác nhận!!!")

      wait.until_not(EC.presence_of_element_located((By.ID, "idvPreregisteredPhone")))
      input("Hãy xác nhận đăng nhập trên điện thoại của bạn và nhấn Enter để tiếp tục...")

  except:
      print("Đăng nhập thành công.")

def get_image():
  config = JsonHandling.read_json("config/config.json")

  email = config["email"]
  password_encode = config["password"]
  password = decrypt_password(password_encode)
  sheet_url = config["sheet_url"]

  
  chrome_options = Options()
  chrome_options.add_argument("--headless")
  chrome_options.add_argument("--window-size=1920,1080")
  chrome_options.add_argument("--no-sandbox")
  chrome_options.add_argument("--disable-dev-shm-usage")
  chrome_options.add_argument("--disable-blink-features=AutomationControlled")
  chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

  drive_service = Service(ChromeDriverManager().install())
  driver = webdriver.Chrome(service=drive_service, options=chrome_options)

  login_google(driver, email, password)

  folder_name = "screenshots"
  os.makedirs(folder_name, exist_ok=True)

  for file_path in glob.glob(os.path.join(folder_name, "*.png")):
    os.remove(file_path)

  i = 0
  for url in sheet_url:
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.XPATH, "//body[contains(@class, 'docs')]")))

    # driver.find_element(By.TAG_NAME, "body").send_keys(Keys.TAB)
    
    # time.sleep(1)
    
    # zoom_button = wait.until(EC.element_to_be_clickable((By.ID, "t-zoom")))
    # zoom_button.click()
    
    # time.sleep(2)

    # zoom_80 = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[text()='75%']")))
    # zoom_80.click()

    # time.sleep(5)

    screenshot = os.path.join(folder_name, f"{i}.png")
    driver.save_screenshot(screenshot)
    i+=1
  
  driver.quit()
  print("Photo has been taken")

  return screenshot