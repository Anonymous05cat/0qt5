import requests
import socket
import platform

# Thay thế token và chat_id của bạn vào đây
TOKEN = '7312308423:AAGQ0CLkWsdJWYJux48gMWGo1CrMMNQ9aTU'
CHAT_ID = '-4212434726'

# Lấy địa chỉ IP của máy tính
def get_ip_address():
    try:
        # Sử dụng socket để lấy địa chỉ IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except socket.error:
        return None

def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    data = {
        'chat_id': CHAT_ID,
        'text': message
    }
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("Message sent successfully")
        else:
            print(f"Failed to send message. Status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Failed to send message: {e}")

# Lấy địa chỉ IP và gửi về Telegram
def main():
    device_name = platform.node()  # Lấy tên thiết bị từ hệ điều hành
    ip_address = get_ip_address()
    if ip_address:
        message = f"{device_name}'s IP address is {ip_address}"
        send_telegram_message(message)
    else:
        print("Failed to retrieve IP address")

if __name__ == "__main__":
    main()