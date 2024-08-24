import telebot
import pandas as pd
from fuzzywuzzy import process
from itertools import permutations
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Replace 'YOUR_API_TOKEN' with your actual Telegram API token
API_TOKEN = 'API_TOKEN'
bot = telebot.TeleBot(API_TOKEN)

# Load teacher information from Excel files
teachers_info_arabic = pd.read_excel('teachers_info_arabic.xlsx')
teachers_info_french = pd.read_excel('teachers_info_french.xlsx')

def find_teacher_name(input_name, teachers_df):
    names = teachers_df['name'].tolist()
    name_parts = input_name.split()
    name_permutations = [' '.join(p) for p in permutations(name_parts)]
    
    best_match = None
    highest_score = 0
    
    for name in name_permutations:
        match = process.extractOne(name, names)
        if match[1] > highest_score:
            best_match = teachers_df.loc[teachers_df['name'] == match[0]]
            highest_score = match[1]
    
    return best_match if highest_score > 80 else None

@bot.message_handler(func=lambda message: True)
def send_teacher_info(message):
    user_input = message.text
    user_id = message.from_user.id
    logger.info(f"User {user_id} requested information for: {user_input}")

    if user_input.isascii():  # Assumes input in French
        teachers_info = find_teacher_name(user_input, teachers_info_french)
        if teachers_info is not None:
            name = teachers_info['name'].values[0]
            email = teachers_info['email'].values[0]
            department = teachers_info['department'].values[0]
            response = f"Nom: {name}\nEmail: {email}\nDepartment: {department}"
        else:
            response = "Non trouvé, vérifiez l'orthographe ou le nom."
    else:  # Assumes input in Arabic
        teachers_info = find_teacher_name(user_input, teachers_info_arabic)
        if teachers_info is not None:
            name = teachers_info['name'].values[0]
            email = teachers_info['email'].values[0]
            department = teachers_info['department'].values[0]
            response = f"الاسم: {name}\nالبريد الإلكتروني: {email}\nالقسم: {department}"
        else:
            response = "لم يتم العثور على المعلم، تحقق من الإملاء أو الاسم."

    bot.send_message(message.chat.id, response)
    logger.info(f"Response sent to user {user_id}: {response}")

# Start polling
bot.polling()
