from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher_suite = Fernet(key)

def encrypt_password(password: str) -> str:
    return cipher_suite.encrypt(password.encode()).decode()

original_password = "Abc@12345"
encrypted_pw = encrypt_password(original_password)

with open("secret.key", "wb") as key_file:
    key_file.write(key)
print(f"Password đã mã hóa: {encrypted_pw}")