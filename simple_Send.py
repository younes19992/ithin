import requests
import json

# URL of your Flask application
url = 'https://trtx.loca.lt/upload'

# JSON data containing file content and name
data = {
    'file_content': 'This is the content of the file.',
    'file_name': 'TEst232.txt'
}

# Convert data to JSON format
json_data = json.dumps(data)

# Set the content type header
headers = {'Content-Type': 'application/json'}

# Make the POST request
response = requests.post(url, data=json_data, headers=headers)

# Print the response
print(response.json())
