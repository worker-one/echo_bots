import discord
import telebot
import asyncio
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(usecwd=True))
# Retrieve environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

# Define intents
intents = discord.Intents.default()
intents.messages = True  # Enable the message intent
intents = discord.Intents.all()
# Initialize the Discord client with intents
discord_client = discord.Client(intents=intents)

# Initialize the Telegram bot
telegram_bot = telebot.TeleBot(TELEGRAM_TOKEN)

@discord_client.event
async def on_ready():
    print(f'Logged in as {discord_client.user}')

@discord_client.event
async def on_message(message):
    # Don't respond to the bot's own messages
    if message.author == discord_client.user:
        return
    print(f'Discord message: {message.content}')
    # Send the message to Telegram
    try:
        telegram_bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=message.content)
        print(f'Message sent to Telegram: {message.content}')
    except Exception as e:
        print(f'Error sending message to Telegram: {e}')

# Function to handle incoming Telegram messages
@telegram_bot.message_handler(func=lambda message: True)
def handle_telegram_message(message):
    print(f'Telegram message: {message.text}')
    # Send the message to Discord
    discord_channel = discord_client.get_channel(DISCORD_CHANNEL_ID)
    if discord_channel:
        asyncio.run_coroutine_threadsafe(discord_channel.send(message.text), discord_client.loop)

@telegram_bot.channel_post_handler(func=lambda message: True)
def echo_all(message):
    print('Chanel {} message received: {}'.format(message.chat.title, message.text))
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, 'message received')
    # Send the message to Discord
    discord_channel = discord_client.get_channel(DISCORD_CHANNEL_ID)
    if discord_channel:
        asyncio.run_coroutine_threadsafe(discord_channel.send(message.text), discord_client.loop)

async def start_discord_bot():
    await discord_client.start(DISCORD_TOKEN)

# Run both the Discord client and Telegram bot in the event loop
async def main():
    loop = asyncio.get_running_loop()
    # Run the Telegram bot polling in a separate thread
    telegram_task = loop.run_in_executor(None, telegram_bot.polling)
    await start_discord_bot()
    await telegram_task

if __name__ == '__main__':
    asyncio.run(main())
