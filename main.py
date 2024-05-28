from instabot import Bot
from sakura_fm import Client
from config import *

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

def main():
    # Authenticate with Instagram
    session = login_to_instagram(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)

    # Initialize Sakura.fm chatbot
    sakura_bot = SakuraChatbot(SAKURA_USERNAME, SAKURA_PASSWORD, MONGODB_URI)

    # Listen for incoming messages
    while True:
        try:
            # Get new messages from Instagram
            new_messages = session.get_pending_inbox()
            for message in new_messages:
                user_id = message["user_id"]
                received_text = message["text"]

                # Send the received message to Sakura.fm
                response = sakura_bot.send_message_to_sakura(user_id, 'dmDCgmq', received_text)

                # Send the Sakura.fm response back to the user on Instagram
                session.send_message(user_id, response)
        except KeyboardInterrupt:
            print("\nChatbot stopped by user.")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
