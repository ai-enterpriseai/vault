import requests

API_KEY = "12345"

# url = "http://localhost:11434/api/generate"
url = "http://localhost:8000/generate"

def main():
    payload = {
        "model": "llama3.1",
        "prompt": "Write a haiku about programming.",
        "stream": False
    }
    headers = {
        "X-API-Key": API_KEY
    }

    response = requests.post(url, json=payload, headers=headers)

    try:
        response_data = response.json()
        print(response_data["response"])
    except ValueError:
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.content}")

# Wrap the existing code in a main function
if __name__ == "__main__":
    main()