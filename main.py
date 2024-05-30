import logging
import time
from ensta import Mobile as EnstaClient
from sakura import Client as SakuraClient
from config import *

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def login_to_instagram(username, password):
    api = EnstaClient(username, password)
    api.login()
    return api

class SakuraChatbot:
    def __init__(self, username, password, mongo_uri):
        self.client = SakuraClient(username=username, password=password, mongo=mongo_uri)

    def send_message_to_sakura(self, uid, char_id, prompt):
        response = self.client.sendMessage(uid, char_id, prompt)
        return response["reply"]  # Extract the relevant part of the response

def fetch_unread_messages(api):
    try:
        inbox = api.get_inbox()
        unread_messages = []
        for thread in inbox['inbox']['threads']:
            for item in thread['items']:
                if not item['is_seen']:
                    unread_messages.append((thread['thread_id'], item['text']))
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
            for thread_id, message in unread_messages:
                # Check if message is not already processed
                if message not in sent_messages:
                    # Send the received message to Sakura.fm
                    sakura_response = sakura_bot.send_message_to_sakura(api.username_id, 'dmDCgmq', message)

                    # Log Sakura.fm response
                    logger.info(f"Sakura.fm response: {sakura_response}")

                    # Send the Sakura.fm response back to the user on Instagram
                    api.send_message(thread_id, sakura_response)
                    logger.info(f"Replied to thread {thread_id} with message: {sakura_response}")

                    # Add sent message to set
                    sent_messages.add(message)

            # Sleep for a short duration to avoid rate limits
            time.sleep(10)
        except KeyboardInterrupt:
            print("\nChatbot stopped by user.")
            break
        except Exception as e:
            logger.error(f"Error: {e}")

if __name__ == "__main__":
    main()
