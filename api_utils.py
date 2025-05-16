import requests

def fetch_text_from_api(api_url):
    fallback_text = "The quick brown fox jumps over the lazy dog."

    try:
        response = requests.get(api_url)
        
        if response.status_code == 200:
            data = response.json()
            if "quote" in data and "body" in data["quote"]:
                return data["quote"]["body"]
            else:
                return fallback_text  
        else:
            return fallback_text  

    except requests.RequestException as e:
        return fallback_text