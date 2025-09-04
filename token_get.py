import requests

# Step 1: Get a Bearer token
token_url = "https://data-api.globalforestwatch.org/auth/token"
username = "gapelbep@gmail.com"        # Replace with your GFW email
password = "Grishcom23@"     # Replace with your GFW password

token_response = requests.post(
    token_url,
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    data={"username": username, "password": password}
)

if token_response.status_code != 200:
    print("Failed to get token:", token_response.text)
    exit()

access_token = token_response.json()["data"]["access_token"]
print("Access token obtained!")

# Step 2: Create an API key using the token
apikey_url = "https://data-api.globalforestwatch.org/auth/apikey"
apikey_data = {
    "alias": "pulseapi",
    "email": username,
    "organization": "Bboxx",
    "domains": ["localhost"]  # Replace with specific domains if needed
}

apikey_response = requests.post(
    apikey_url,
    headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    },
    json=apikey_data
)

if apikey_response.status_code != 200:
    print("Failed to create API key:", apikey_response.text)
    exit()

api_key = apikey_response.json()["data"][0]["api_key"]
print("API Key created successfully!")
print("Your API Key:", api_key)
