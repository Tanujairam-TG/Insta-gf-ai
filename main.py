import logging
import time
from instagram_private_api import Client
from sakura import Client as SakuraClient
from config import *

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def login_to_instagram(username, password):
    api = Client(username, password)
    return api

class SakuraChatbot:
    def __init__(self, username, password, mongo_uri):
        self.client = SakuraClient(username=username, password=password, mongo=mongo_uri)

    def send_message_to_sakura(self, uid, char_id, prompt):
        response = self.client.sendMessage(uid, char_id, prompt)
        return response["reply"]  # Extract the relevant part of the response

# Define a constant for the wait time between requests (in seconds)
WAIT_TIME_BETWEEN_REQUESTS = 60  # Adjust as needed

def fetch_unread_messages(api):
    try:
        # Sleep for a short duration to avoid hitting rate limits
        time.sleep(WAIT_TIME_BETWEEN_REQUESTS)

        # Fetch all direct messages
        inbox = api.direct_v2_inbox()
        unread_messages = [thread["items"][0]["text"] for thread in inbox["inbox"]["threads"] if not thread["items"][0]["item_id"]]
        logger.info(f"Fetched {len(unread_messages)} unread messages.")

        # Log message content for debugging
        for message in unread_messages:
            logger.debug(f"Message content: {message}")

        return unread_messages
    except Exception as e:
        logger.error(f"Error fetching unread messages: {e}")
        return []

def main():
    # Authenticate with Instagram
    api = login_to_instagram(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)

    # Initialize Sakura.fm chatbot
    sakura_bot = SakuraChatbot(SAKURA_USERNAME, SAKURA_PASSWORD, MONGODB_URI)

    # Keep track of sent messages to prevent responding to own messages
    sent_messages = set()

    # Listen for incoming messages
    while True:
        try:
            unread_messages = fetch_unread_messages(api)
            for message in unread_messages:
                # Check if message is not already processed
                if message not in sent_messages:
                    # Send the received message to Sakura.fm
                    sakura_response = sakura_bot.send_message_to_sakura(api.authenticated_user_id, 'dmDCgmq', message)

                    # Log Sakura.fm response
                    logger.info(f"Sakura.fm response: {sakura_response}")

                    # Send the Sakura.fm response back to the user on Instagram
                    api.direct_v2_send(sakura_response, [api.authenticated_user_id])
                    logger.info(f"Replied to user {api.authenticated_user_id} with message: {sakura_response}")

                    # Add sent message to set
                    sent_messages.add(message)
                else:
                    logger.info("Skipping already processed message.")

        except KeyboardInterrupt:
            print("\nChatbot stopped by user.")
            break
        except Exception as e:
            logger.error(f"Error: {e}")

if __name__ == "__main__":
    main()
