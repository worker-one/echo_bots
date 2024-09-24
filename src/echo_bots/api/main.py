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

# Load logging configuration with OmegaConf
logging_config = OmegaConf.to_container(
    OmegaConf.load("./src/echo_bots/conf/logging_config.yaml"),
    resolve=True
)
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)



config = OmegaConf.load("./src/echo_bots/conf/config.yaml")


# Define intents
intents = discord.Intents.default()
intents.messages = True  # Enable the message intent
intents = discord.Intents.all()
# Initialize the Discord client with intents
discord_client = discord.Client(intents=intents)

# Initialize the Telegram bot
telegram_bot = telebot.TeleBot(TELEGRAM_TOKEN)

logger.info(f"Logged as a telegram bot {telegram_bot.me}")

@discord_client.event
async def on_ready():
    logger.info(f"Logged as a discord bot {discord_client.user}")

@discord_client.event
async def on_message(message):
    # Don't respond to the bot's own messages
    if message.author == discord_client.user:
        return
    logger.info(f'Discord message: {message.content} from {message.channel}')
    # Send the message to Telegram
    for telegram_channel_id in config.telegram.target:
        try:
            telegram_bot.send_message(chat_id=telegram_channel_id, text=message.content)
            logger.info(f'Message sent to Telegram channel {telegram_channel_id}: {message.content}')
        except Exception as e:
            logger.info(f'Error sending message to Telegram channel {telegram_channel_id}: {e}')

@telegram_bot.channel_post_handler(func=lambda message: True)
def echo_all(message):
    logger.info('Chanel {} message received: {}'.format(message.chat.title, message.text))
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, 'message received')
    # Send the message to Discord
    for discord_channel_id in config.discord.target:
        discord_channel = discord_client.get_channel(discord_channel_id)
        if discord_channel:
            logger.info(f"Message sent to discord channel {discord_channel_id}")
            asyncio.run_coroutine_threadsafe(discord_channel.send(message.text), discord_client.loop)
        else:
            logger.info(f"Discord channel {discord_channel_id} has been not found")

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
