import logging
import time
from instagrapi import Client
from sakura import Client as SakuraClient
from config import *

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def login_to_instagram(username, password):
    cl = Client()
    cl.login(username, password)
    return cl

class SakuraChatbot:
    def __init__(self, username, password, mongo_uri):
        self.client = SakuraClient(username=username, password=password, mongo=mongo_uri)

    def send_message_to_sakura(self, uid, char_id, prompt):
        response = self.client.sendMessage(uid, char_id, prompt)
        return response["reply"]  # Extract the relevant part of the response

# Define a constant for the wait time between requests (in seconds)
WAIT_TIME_BETWEEN_REQUESTS = 60  # Adjust as needed

def fetch_unread_messages(session):
    try:
        # Sleep for a short duration to avoid hitting rate limits
        time.sleep(WAIT_TIME_BETWEEN_REQUESTS)

        # Fetch all direct message threads
        all_threads = session.direct_threads()

        # Filter unread threads
        unread_threads = [thread for thread in all_threads if not thread.items[0].item.seen]
        logger.info(f"Fetched {len(unread_threads)} unread message threads.")

        # Log thread content for debugging
        for thread in unread_threads:
            logger.debug(f"Thread content: {thread.items}")

        return unread_threads
    except AttributeError:
        logger.info("No unread messages.")
        return []
    except Exception as e:
        logger.error(f"Error fetching unread messages: {e}")
        return []

def main():
    # Authenticate with Instagram
    session = login_to_instagram(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)

    # Initialize Sakura.fm chatbot
    sakura_bot = SakuraChatbot(SAKURA_USERNAME, SAKURA_PASSWORD, MONGODB_URI)

    # Keep track of sent messages to prevent responding to own messages
    sent_messages = set()

    # Listen for incoming messages
    while True:
        try:
            unread_messages = fetch_unread_messages(session)
            for thread in unread_messages:
                for message in thread.items:
                    user_id = message.user_id
                    received_text = message.text
                    logger.info(f"Received message from user {user_id}: {received_text}")

                    # Check if message is from the bot itself
                    if user_id == session.user_id:
                        logger.info("Skipping own message.")
                        continue

                    # Check if message is not already processed
                    if (user_id, received_text) not in sent_messages:
                        # Send the received message to Sakura.fm
                        sakura_response = sakura_bot.send_message_to_sakura(user_id, 'dmDCgmq', received_text)

                        # Log Sakura.fm response
                        logger.info(f"Sakura.fm response: {sakura_response}")

                        # Send the Sakura.fm response back to the user on Instagram
                        session.direct_send(sakura_response, [user_id])
                        logger.info(f"Replied to user {user_id} with message: {sakura_response}")

                        # Add sent message to set
                        sent_messages.add((user_id, received_text))
                    else:
                        logger.info("Skipping already processed message.")

        except KeyboardInterrupt:
            print("\nChatbot stopped by user.")
            break
        except Exception as e:
            logger.error(f"Error: {e}")

if __name__ == "__main__":
    main()
