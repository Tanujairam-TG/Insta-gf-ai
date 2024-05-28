import time
import logging
from InstagramAPI import InstagramAPI
from sakura import Client  
from config import *  

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class InstagramChatbot:
    def __init__(self, username, password):
        self.api = InstagramAPI(username, password)
        self.api.login()

    def get_direct_messages(self):
        self.api.getv2Inbox()
        inbox = self.api.LastJson
        messages = []

        if 'inbox' in inbox and 'threads' in inbox['inbox']:
            for thread in inbox['inbox']['threads']:
                for item in thread['items']:
                    if item['item_type'] == 'text':
                        messages.append({
                            'user_id': item['user_id'],
                            'text': item['text']
                        })
        return messages

    def send_message(self, user_id, text):
        self.api.direct_message(text, user_id)

def main():
    # Initialize Instagram chatbot
    insta_bot = InstagramChatbot(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)

    # Initialize Sakura.fm chatbot
    sakura_bot = Client(SAKURA_USERNAME, SAKURA_PASSWORD, MONGODB_URI)

    try:
        while True:
            try:
                # Get new messages from Instagram
                new_messages = insta_bot.get_direct_messages()
                for message in new_messages:
                    user_id = message['user_id']
                    received_text = message['text']

                    # Log received message
                    logger.info(f"Received message from user {user_id}: {received_text}")

                    # Send the received message to Sakura.fm
                    sakura_response = sakura_bot.sendMessage(user_id, 'dmDCgmq', received_text)['reply']

                    # Log Sakura.fm response
                    logger.info(f"Sakura.fm response: {sakura_response}")

                    # Send the Sakura.fm response back to the user on Instagram
                    insta_bot.send_message(user_id, sakura_response)

                # Delay between checks to avoid rate limits
                time.sleep(10)
            except Exception as e:
                logger.error(f"Error processing messages: {e}")
                time.sleep(60)  # Wait a minute before retrying in case of an error

    except KeyboardInterrupt:
        print("\nChatbot stopped by user.")
    finally:
        insta_bot.api.logout()
        logger.info("Instagram session logged out.")

if __name__ == "__main__":
    main()
