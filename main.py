from config import *
from insta import login_to_instagram
from sakura import SakuraChatbot

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

                # Process the received message (you can customize this logic)
                response = sakura_bot.send_message_to_sakura(user_id, 'dmDCgmq', received_text)

                # Send the response back to the user on Instagram
                session.send_message(user_id, response)
        except KeyboardInterrupt:
            print("\nChatbot stopped by user.")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
