import time
import logging
from instabot import Bot
from sakura import Client
from config import *

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def login_to_instagram(username, password):
    bot = Bot()
    bot.login(username=username, password=password)
    return bot

class SakuraChatbot:
    def __init__(self, username, password, mongo_uri):
        self.client = Client(username=username, password=password, mongo=mongo_uri)

    def send_message_to_sakura(self, uid, char_id, prompt):
        response = self.client.sendMessage(uid, char_id, prompt)
        return response["reply"]  # Extract the relevant part of the response

def handle_rate_limit(bot):
    logger.warning("Rate limit hit. Sleeping for 5 minutes.")
    for _ in range(5):  # Sleep in 1-minute increments to avoid Heroku timeout
        time.sleep(60)

def main():
    # Authenticate with Instagram
    session = login_to_instagram(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)

    # Initialize Sakura.fm chatbot
    sakura_bot = SakuraChatbot(SAKURA_USERNAME, SAKURA_PASSWORD, MONGODB_URI)

    try:
        # Listen for incoming messages
        while True:
            try:
                # Get new messages from Instagram
                new_messages = session.get_pending_inbox()
                for message in new_messages:
                    user_id = message["user_id"]
                    received_text = message["text"]

                    # Log user message and username
                    logger.info(f"Received message from user {user_id}: {received_text}")

                    # Send the received message to Sakura.fm
                    sakura_response = sakura_bot.send_message_to_sakura(user_id, 'dmDCgmq', received_text)

                    # Log Sakura.fm response
                    logger.info(f"Sakura.fm response: {sakura_response}")

                    # Send the Sakura.fm response back to the user on Instagram
                    session.send_message(user_id, sakura_response)

                # Delay between requests to avoid hitting rate limits
                time.sleep(10)  # Adjust the sleep time as needed

            except Exception as e:
                if '429' in str(e):
                    handle_rate_limit(session)
                else:
                    logger.error(f"Error processing messages: {e}")

    except KeyboardInterrupt:
        print("\nChatbot stopped by user.")
    finally:
        # Ensure session is properly logged out
        session.logout()
        logger.info("Instagram session logged out.")

if __name__ == "__main__":
    main()
