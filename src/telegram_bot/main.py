import telebot
import random

from models import BertModel, LLM
from utils import parse_page

TOKEN = "5131531473:AAH4gNtBfBogjqr3gFRiELpomg1fSUvgoDE"
URL_REGEX = r"(https?://[^\s]+)"
bot = telebot.TeleBot(TOKEN, parse_mode=None)
model_type = "llm"

print(f"loading language model type {model_type} ... ")

if model_type == "llm":
    language_model = LLM()
else:
    language_model = BertModel("G:/My Drive/workspace/Orders/00108/transformer_model.pt")
print("language loaded")

@bot.message_handler(regexp=URL_REGEX)
def send_welcome(message):
    bot.reply_to(message, "Ссылку получил, обрабатываю...")
    response = parse_page(message.text)

    if response['status']['code'] == 0:
        bot.reply_to(message, response['content']['paragraphs'])
        language_model_output = language_model.run(response["content"]['paragraphs'])
        print(f"language_model_output {language_model_output}")

        if model_type == "llm":
            bot.reply_to(message, language_model_output)
        else:
            bot.reply_to(message, f"Вероятность фейковой новости: {1 - language_model_output['score']}")

    if response['status']['code'] == 1:
        bot.reply_to(message, response['status']['message'])

print("bot started")
bot.infinity_polling()
