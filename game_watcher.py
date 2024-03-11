from flask import Flask, request, jsonify
import threading
import os
import time
import requests
import json
import uuid
app = Flask(__name__)

# Define a dictionary to store active threads and their last activity time
active_threads = {}

# Discord webhook URL to send messages
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1216376021977268275/NkKk119q9SlfYSDDGdBxp7f5D7Xpv1mtUYVgDi4NqaRMOMKn_NgSr_nhBtXnE6HyncSh"

def send_discord_message(message):
    """
    Function to send a message to Discord using a webhook.
    """
    payload = {"content": message}
    headers = {"Content-Type": "application/json"}
    response = requests.post(DISCORD_WEBHOOK_URL, data=json.dumps(payload), headers=headers)
    if response.status_code != 204:
        print("Failed to send message to Discord")

def create_directory_and_send_url():
    """
    Function to create a new directory with a unique ID, set its URL, and send the URL to the sender.
    """
    try:
        # Generate a unique directory name
        directory_name = str(uuid.uuid4())

        # Create the directory
        os.mkdir(directory_name)

        # Set the URL
        url = f"http://your_domain/{directory_name}"

        # Send the URL to the sender
        sender_ip = request.remote_addr
        print(f"URL: {url} sent to {sender_ip}")

        # Function to wait for POST requests
        def wait_for_post():
            start_time = time.time()
            while directory_name in active_threads:
                time.sleep(1)  # Check every 1 second
                current_time = time.time()
                if current_time - start_time >= 5:
                    del active_threads[directory_name]
                    os.rmdir(directory_name)
                    send_discord_message(f"A connection in directory {directory_name} has been cut!")
                    break

        # Start a thread to wait for POST requests
        thread = threading.Thread(target=wait_for_post)
        thread.start()

        # Store the thread object and its start time for tracking
        active_threads[directory_name] = {"thread": thread, "start_time": time.time()}

        return directory_name
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/register', methods=['GET'])
def register():
    """
    Endpoint to initiate the creation of a new directory and sending its URL.
    """
    directory_name = create_directory_and_send_url()
    if directory_name:
        return jsonify({"directory_name": directory_name}), 200
    else:
        return jsonify({"error": "Failed to create directory"}), 500

@app.route('/<directory_name>', methods=['POST'])
def receive_post(directory_name):
    """
    Endpoint to handle POST requests. If a POST request is received, keep the directory active.
    """
    if directory_name in active_threads:
        # Reset the timer for this directory thread
        active_threads[directory_name]["start_time"] = time.time()
        return jsonify({"message": "Received POST request."}), 200
    else:
        return jsonify({"error": "Directory not found."}), 404

def check_inactive_connections():
    """
    Function to check inactive connections and delete them if no POST request is received within 5 seconds.
    """
    while True:
        for directory_name, thread_info in list(active_threads.items()):
            current_time = time.time()
            if current_time - thread_info["start_time"] >= 5:
                del active_threads[directory_name]
                thread_info["thread"].join()  # Wait for the thread to finish
                os.rmdir(directory_name)
                send_discord_message(f"A connection in directory {directory_name} has been cut!")
        time.sleep(1)

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not Found"}), 404

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    # Start a separate thread to check for inactive connections
    checker_thread = threading.Thread(target=check_inactive_connections)
    checker_thread.start()

    # Start the Flask application
    app.run(debug=True)
