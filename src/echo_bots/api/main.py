import os
import discord
import telebot
import logging.config
import asyncio
from dotenv import find_dotenv, load_dotenv
from omegaconf import OmegaConf

load_dotenv(find_dotenv(usecwd=True))

# Retrieve environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Load configurations
logging_config = OmegaConf.to_container(OmegaConf.load("./src/echo_bots/conf/logging_config.yaml"), resolve=True)
config = OmegaConf.load("./src/echo_bots/conf/config.yaml")

# Set up logging
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

# Define intents
intents = discord.Intents.all()  # Enable all intents

# Initialize the Discord client with intents
discord_client = discord.Client(intents=intents)

# Initialize the Telegram bot
telegram_bot = telebot.TeleBot(TELEGRAM_TOKEN)

logger.info(f"Logged in as a Telegram bot {telegram_bot.get_me().username}")

@discord_client.event
async def on_ready():
    logger.info(f"Logged in as a Discord bot {discord_client.user}")

@discord_client.event
async def on_message(message):
    if message.author == discord_client.user or message.channel.id not in config.discord.source:
        return
    logger.info('Discord message: %s from %d', message.content, message.channel.id)

    # Send the message to Telegram
    for telegram_channel_id in config.telegram.target:
        try:
            telegram_bot.send_message(chat_id=telegram_channel_id, text=message.content)
            logger.info('Message sent to Telegram channel %d: %s', telegram_channel_id, message.content)
        except Exception as e:
            logger.error('Error sending message to Telegram channel %d: %s', telegram_channel_id, e)

def handle_telegram_message(message):
    logger.info('Telegram message: %s', message.text)
    
    for discord_channel_id in config.discord.target:
        discord_channel = discord_client.get_channel(discord_channel_id)
        if discord_channel:
            asyncio.create_task(discord_channel.send(message.text))

@telegram_bot.message_handler(func=lambda message: True)
def telegram_message_handler(message):
    handle_telegram_message(message)

@telegram_bot.channel_post_handler(func=lambda message: True)
def telegram_channel_post_handler(message):
    logger.info('Channel %s message received: %s', message.chat.title, message.text)
    handle_telegram_message(message)

async def start_discord_bot():
    await discord_client.start(DISCORD_TOKEN)

async def main():
    loop = asyncio.get_running_loop()

    # Run the Telegram bot polling in a separate thread
    telegram_task = loop.run_in_executor(None, telegram_bot.polling)

    await start_discord_bot()
    await telegram_task

if __name__ == '__main__':
    asyncio.run(main())
