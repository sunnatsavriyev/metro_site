import requests

def send_sms_via_eskiz(phone, message):
    
    login_url = "https://notify.eskiz.uz/api/auth/login"
    login_data = {
        'email': 'sunnatchiksavriyev@gmail.com',
        'password': 'g6z7fB3JR7WHmdjr8Xs0rH1898phBoeoerceBSci' 
    }
    
    login_response = requests.post(login_url, data=login_data)
    # Eskiz javobidan tokenni sug'urib olamiz
    token = login_response.json().get("data", {}).get("token")

    # 2. SMS YUBORISH (OLINGAN TOKEN BILAN)
    if token:
        send_url = "https://notify.eskiz.uz/api/message/sms/send"
        
        # TOKENNI HEADERS GA BERAMIZ
        headers = {
            "Authorization": f"Bearer {token}" 
        }
        
        payload = {
            "mobile_phone": phone,
            "message": message,
            "from": "4546"
        }
        
        # SMS yuborish so'rovi
        response = requests.post(send_url, data=payload, headers=headers)
        return response.json()
    
    return None