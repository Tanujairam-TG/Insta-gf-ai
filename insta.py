from instabot import Bot

def login_to_instagram(username, password):
    bot = Bot()
    bot.login(username=username, password=password)
    return bot

# Example usage:
# session = login_to_instagram("your_instagram_username", "your_instagram_password")
