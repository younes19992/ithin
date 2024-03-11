import requests
import time

# Define the URL for the register endpoint
register_url = "https://trtx.loca.lt/register"

# Define the game name
game_name = "Coolgame"  # Replace with your actual game name

# Send a POST request to register the game
response = requests.post(register_url, json={"game_name": game_name})

# Check if the registration was successful
if response.status_code == 200:
    data = response.json()
    directory_name = data.get("directory_name")
    print("Game Name:", game_name)
    print("Directory Name:", directory_name)

    # Define the URL for the directory endpoint
    post_url = f"https://trtx.loca.lt/{directory_name}"

    # Continuously send POST requests to maintain the connection
    while True:
        # Send a POST request to the directory endpoint
        response = requests.post(post_url)

        # Check the status code of the response
        if response.status_code == 200:
            print("Connection is still active.")
        else:
            print("Connection lost.")

        # Wait for 2 seconds before sending the next POST request
        time.sleep(2)
else:
    print("Failed to register the game.")
