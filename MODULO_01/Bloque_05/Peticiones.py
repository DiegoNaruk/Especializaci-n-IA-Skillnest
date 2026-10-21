import json
import requests


def create_payload(prompt):
    return json.dumps({
  "contents": [
    {
      "role": "user",
      "parts": [
        {
          "text": prompt
        }
      ]
    }
  ]
})
def create_headers(api_key):
    return {
  'x-goog-api-key': api_key,
  'Content-Type': 'application/json'
}
def create_request(url, api_key, prompt):
   headers = create_headers(api_key)
   payload = create_payload(prompt)
   try:
       response = requests.request("POST", url, headers=headers, data=payload)
       return response
   except requests.RequestException as e:
       print(f"Error during request: {e}")
       return None