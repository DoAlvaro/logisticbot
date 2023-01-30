import telebot
import config
from telebot import types
import googleapiclient.discovery
import httplib2
from oauth2client.service_account import ServiceAccountCredentials

CREDENTIALS_FILE = 'gs_credentials.json'
# Читаем ключи из файла
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                               ['https://www.googleapis.com/auth/spreadsheets',
                                                                'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
service = googleapiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API

spreadsheetId = '1XMxDr6yRQQdkXWF_7OxHhi7DLS5KlqUBEqNLGmmyHMI'  # сохраняем идентификатор файла
driveService = googleapiclient.discovery.build('drive', 'v3',
                                               http=httpAuth)  # Выбираем работу с Google Drive и 3 версию API


def sheet_finder(service, key):
    ranges = ["Лист номер один!A1:B999"]  # нужный диапазон

    results = service.spreadsheets().values().batchGet(spreadsheetId=spreadsheetId,
                                                       ranges=ranges,
                                                       valueRenderOption='FORMATTED_VALUE',
                                                       dateTimeRenderOption='FORMATTED_STRING').execute()
    sheet_values = results['valueRanges'][0]['values']
    for pair in sheet_values:
        try:
            if pair[0] == key:
                return pair[1]
        except:
            pass
    return 0


bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
def welcome(message):
    global status_user
    sti = open('stick/wel.webp', 'rb')
    status_user = 0
    bot.send_sticker(message.chat.id, sti)
    # клава
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Узнать статус заказа")
    item2 = types.KeyboardButton("Нужна помощь")
    markup.add(item1, item2)
    bot.send_message(message.chat.id,
                     "Приветствуем вас на борту нашей компании Logistics Jet!\nВыберете нужный пункт для продолжения:",
                     parse_mode='html', reply_markup=markup)



try:
    if states:
        pass

except:
    states = dict()


@bot.message_handler(content_types=['text'])
def lalala(message):
    global status_user
    global service
    personal_id = message.chat.id
    try:
        pos = states[personal_id]
    except:
        states[personal_id] = 0
    if True:
        if states[personal_id] == 0:
            if message.text == "Узнать статус заказа":
                states[personal_id] = 1
                bot.send_message(message.chat.id, "Введите, пожалуйста, номер вашего заказа, выданного менеджером.")
                return 0
            elif message.text == "Нужна помощь":
                bot.send_message(message.chat.id, "@abwannammm - Руководитель ( обращаться по остальным вопросам )\n@Aj1ka - Директор отдела доставки.\n@petrrryashin - Директор отдела заказов.")
            else:
                bot.send_message(message.chat.id, "Я вас не понимаю :)")
        if states[personal_id] == 1:
            key = str(message.text)
            state = sheet_finder(service, key)
            if state != 0:
                bot.send_message(message.chat.id, "Статус заказа:\n{0}".format(state))
            else:
                bot.send_message(message.chat.id,
                                 "Похоже, Вы неправильно ввели номер вашего заказа.\nВведите заново номер заказа, предварительно нажав на левую кнопку.\nЛибо обратитесь к менеджеру за дополнительной помощью, нажав кнопку справа.")
            states[personal_id] = 0


bot.polling(none_stop=True)
