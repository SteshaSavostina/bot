import telebot
from telebot import types
import sqlite3
import requests
import json
import datetime

bot = telebot.TeleBot('6841917281:AAHGyGFiPGcHLHfe6NB8h74I0IOWXVnfyX8')
API = '288df9f4e0bbd2ff2b3601b708fa4fa9'

name = ''
surname = ''
age = 0


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.from_user.id, "/bmi - узнать ИМТ \n"
                                           "/reg - зарегестрировать пользователя \n"
                                           "/weather - узнать погоду \n"
                                           "/help - узнать команды")


@bot.message_handler(commands=['reg'])
def start(message):
    if message.text == '/reg':
        conn = sqlite3.connect('reg.db')
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name varchar(50), surname varchar(50), '
                    'age integer)')
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(message.from_user.id, "Давайте познакомимся! Как Вас зовут?")
        bot.register_next_step_handler(message, get_name)


def get_name(message):  # получаем фамилию
    global name
    name = message.text
    bot.send_message(message.from_user.id, 'Напишите Вашу фамилию!')
    bot.register_next_step_handler(message, get_surname)


def get_surname(message):
    global surname
    surname = message.text
    bot.send_message(message.from_user.id, 'Сколько Вам лет?')
    bot.register_next_step_handler(message, get_age)


def get_age(message):
    global age
    age = message.text
    try:
        age = int(age)
        bot.send_message(message.from_user.id, f'Отлично! Приятно познакомиться, {name} {surname}, {age} лет.')

    except Exception:
        bot.send_message(message.from_user.id, 'Цифрами, пожалуйста. Придется регестрироваться снова')

    conn = sqlite3.connect('reg.db')
    cur = conn.cursor()
    cur.execute(f"INSERT INTO users (name, surname, age) VALUES ('{name}', '{surname}', '{age}')")
    conn.commit()
    cur.close()
    conn.close()


height = 0
weight = 0


@bot.message_handler(commands=['bmi'])
def calculate_bmi(message):
    if message.text == '/bmi':
        bot.send_message(message.from_user.id,
                         f'Здравствуйте, {message.from_user.first_name}! Если Вы хотите рассчитать свой ИМТ, то '
                         f'смело отправляйте свой рост')
        bot.register_next_step_handler(message, get_height)
    else:
        bot.send_message(message.from_user.id, 'Напишите /help')


def get_height(message):
    global height
    height = message.text

    try:
        height = int(height)
        height = float(message.text)
        bot.send_message(message.from_user.id, f'{message.from_user.first_name}, а теперь введите свой вес')
        bot.register_next_step_handler(message, get_weight)
    except ValueError:
        bot.send_message(message.from_user.id, 'Похоже, вы ошиблись. Попробуйте снова')


def get_weight(message):
    global weight
    weight = message.text

    try:
        weight = int(message.text)
        bot.send_message(message.from_user.id, f'Рассчитываем ваш ИМТ')

        bmi = round(float(int(weight) / ((int(height) / 100) ** 2)), 2)
        category = get_bmi_category(bmi)
        bot.send_message(message.from_user.id, f'Ваш ИМТ составляет {bmi}. Это соответствует категории {category}. '
                                               f'Ваш идеальный вес: {int(height) - 100}. Хотите узнать рекомендации?')

        bot.register_next_step_handler(message, recomendations)

    except Exception:
        bot.send_message(message.from_user.id, 'Похоже, вы ошиблись. Попробуйте снова')


def get_bmi_category(bmi):
    if bmi < 16:
        return "Выраженный дефицит массы тела"
    elif 16 < bmi <= 20:
        return "Недостаточная (дефицит) масса тела"
    elif 20 < bmi <= 25:
        return "Норма"
    elif 25 < bmi <= 30:
        return "Избыточная масса тела (предожирение)"
    elif 30 < bmi <= 35:
        return "Ожирение 1 степени"
    elif 35 < bmi <= 40:
        return "Ожирение 2 степени"
    elif bmi > 40:
        return "Ожирение 3 степени"


agree = ''


def recomendations(message):
    global agree
    bmi = round(float(int(weight) / ((int(height) / 100) ** 2)), 2)
    agree = message.text
    print(agree)
    category = get_bmi_category(bmi)
    if agree == 'да' or agree == 'конечно':
        if category == "Выраженный дефицит массы тела":
            bot.send_message(message.from_user.id, 'Рекомендация: Единственный способ поправиться — больше кушать. '
                                                   'Наращивать объемы лучше с добавлением в рацион высококалорийных '
                                                   'продуктов — орехов,'
                                                   'сложных углеводов, молока, кефира, творога. Для поднятия веса '
                                                   'лучше прибегать к силовым тренировкам.'
                                                   'Эффективным будет добавление витаминов и БАДов. Однако важно '
                                                   'проконсультироваться с лечащим врачом,'
                                                   'чтобы он определил, каких именно полезных веществ не хватает '
                                                   'организму.'
                                                   'Безопасный и быстрый способ повысить вес — прием пивных дрожжей. '
                                                   'Для улучшения пищеварения врач может порекомендовать пробиотики.')
        elif category == "Недостаточная (дефицит) масса тела":
            bot.send_message(message.from_user.id, "Рекомендация:"
                                                   "Единственный способ поправиться — больше кушать. "
                                                   "Наращивать объемы лучше с добавлением в рацион высококалорийных "
                                                   "продуктов — орехов,"
                                                   "сложных углеводов, молока, кефира, творога. Для поднятия веса "
                                                   "лучше прибегать к силовым"
                                                   "тренировкам.")
        elif category == "Норма":
            bot.send_message(message.from_user.id, '''
        Рекомендация:
Нормальный вес не является гарантией богатырского здоровья, но значительно снижает риск появления нарушений и 
заболеваний, вызываемых избыточным или недостаточным весом. Кроме того, обладатели нормального веса, как правило, 
пребывают в хорошем самочувствии даже после интенсивных физических нагрузок.
                ''')
        elif category == "Избыточная масса тела (предожирение)":
            bot.send_message(message.from_user.id, '''
        Рекомендация:
Достаточно скорректировать образ жизни, питание:

- Отказаться от любого алкоголя;
- Увеличить потребление фруктов, овощей;
- Уменьшить количество калорий;
- Заниматься спортом минимум 150 минут в неделю.

Поддерживать организм в тонусе помогают зеленые, травяные чаи, цитрусовые фрукты, 
кисломолочные продукты жирностью не более 2,5%.

Бороться с лишним весом — тяжелая работа, поэтому следите за питанием, занимайтесь спортом, 
больше двигайтесь и будьте здоровы!
                ''')
        elif category == "Ожирение 1 степени":
            bot.send_message(message.from_user.id, '''
        Рекомендация:
Ожирение требует не просто коррекции образа жизни. Врач должен выяснить корень проблемы, назначить лечение. 
Причиной может быть как банальное переедание, так и гормональный сбой. 
Наряду с соответствующими лекарствами эффективным будет прием витаминов для коррекции веса. 
Их подбором должен заниматься лечащий врач или диетолог.      

Бороться с лишним весом — тяжелая работа, поэтому следите за питанием, занимайтесь спортом, 
больше двигайтесь и будьте здоровы!          
                ''')
        elif category == "Ожирение 2 степени":
            bot.send_message(message.from_user.id, '''
        Рекомендация:
Кроме коррекции питания, физических нагрузок врач должен назначить лечение в соответствии с причиной ожирения. 
Это могут быть как пищевые привычки, малоактивный образ жизни, так и гормонально-эндокринные заболевания, 
а у женщин — синдром поликистозных яичников. В большинстве случаев назначают препараты для нормализации обмена веществ.

Бороться с лишним весом — тяжелая работа, поэтому следите за питанием, занимайтесь спортом, 
больше двигайтесь и будьте здоровы!
                ''')
        elif category == "Ожирение 3 степени":
            bot.send_message(message.from_user.id, '''
        Рекомендация:
Победить ожирение высокой степени можно только комплексом мер, силой воли. Необходима лекарственная терапия, 
направленная на устранение причин, сопутствующих заболеваний, а также постепенное изменение пищевых привычек.

Бороться с лишним весом — тяжелая работа, поэтому следите за питанием, занимайтесь спортом, 
больше двигайтесь и будьте здоровы!
                ''')
    else:
        bot.send_message(message.from_user.id, 'Введите /help, если хотите еще что-то узнать!')


description = ''


@bot.message_handler(commands=['weather'])
def weather(message):
    bot.send_message(message.chat.id, 'Как вы знаете для хорошего самочувствия важна хорошая погода. '
                                      'Введите название города, чтобы узнать сколько там градусов',
                     reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_weather)


def get_weather(message):
    code_to_smile = {
        "Clear": "Ясно \U00002600",
        "Clouds": "Облачно \U00002601",
        "Rain": "Дождь \U00002614",
        "Drizzle": "Дождь \U00002614",
        "Thunderstorm": "Гроза \U000026A1",
        "Snow": "Снег \U0001F328",
        "Mist": "Туман \U0001F32B"
    }
    city = message.text.strip().lower()
    global img
    global description
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric')
    if res.status_code == 200:
        data = json.loads(res.text)
        temp = data["main"]["temp"]
        description = data["weather"][0]["main"]
        img = ''
        if description in code_to_smile:
            wd = code_to_smile[description]
        else:
            # если эмодзи для погоды нет, выводим другое сообщение
            wd = "Посмотри в окно, я не понимаю, что там за погода..."
        bot.send_message(message.chat.id, f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                                          f"Погода в городе: {city}\n"
                                          f"Температура: {temp}°C {wd}\n")
        if description == 'Clear':
            img = 'sunny.png'
        elif description == 'Clouds':
            img = 'cloudy.png'
        elif description == 'Rain':
            img = 'rain.png'
        elif description == 'Drizzle':
            img = 'rain.png'
        elif description == 'Thunderstorm':
            img = 'thunderstorm.png'
        elif description == 'Snow':
            img = 'snow.png'
        elif description == 'Mist':
            img = 'mist.png'

        file = open('./' + img, 'rb')
        bot.send_photo(message.chat.id, file)
        bot.send_message(message.chat.id, 'Подсказать Вам, что можно поделать?')
        bot.register_next_step_handler(message, further_plans)
    else:
        bot.reply_to(message, 'Город указан неверно. Попробуйте еще раз')


def further_plans(message):
    if message.text.lower() == 'да':
        global description
        if description == 'Clear' or description == 'Clouds':
            markup = types.ReplyKeyboardMarkup()
            btn1 = types.KeyboardButton('Прогуляться по городу')
            btn2 = types.KeyboardButton('Встретиться с друзьями, семьей или любимым человеком')
            btn3 = types.KeyboardButton('Сходите в торговый центр за новыми покупочками')
            markup.row(btn1)
            markup.add()
            markup.row(btn2, btn3)
            bot.send_message(message.chat.id,
                             'Здравствуйте! Погода сегодня просто замечательная. Предлагаю Вам несколько вариантов',
                             reply_markup=markup)
            bot.register_next_step_handler(message, on_click)

        else:

            markup1 = types.ReplyKeyboardMarkup()
            btn1 = types.KeyboardButton('Ужасы')
            btn2 = types.KeyboardButton('Мелодрама')
            btn3 = types.KeyboardButton('Комедия')
            btn4 = types.KeyboardButton('Драма')
            btn5 = types.KeyboardButton('Мультфильм')
            btn6 = types.KeyboardButton('Научная фантастика')

            markup1.row(btn1, btn2)
            markup1.add()
            markup1.row(btn3, btn4)
            markup1.add()
            markup1.row(btn5, btn6)
            bot.send_message(message.chat.id,
                             'Да уж! Погодка так себе. Поэтому предлагаю устроить Вам кино-марафон! Какие фильмы вы '
                             'любите?', reply_markup=markup1)
            bot.register_next_step_handler(message, films)
    else:
        bot.send_message(message.chat.id, 'Введите /help, если хотите узнать что-то еще')


def on_click(message):
    if message.text == 'Прогуляться по городу':
        bot.send_message(message.chat.id,
                         'Подсказать вам полный адрес и координаты какого-нибудь места? Если да, введите адрес!')
        bot.register_next_step_handler(message, coord)
    elif message.text == 'Встретиться с друзьями, семьей или любимым человеком':
        bot.send_message(message.chat.id, 'Вот вам несколько идей')
        bot.send_message(message.chat.id, '1. Организуйте поочерёдный «званый ужин» \n'
                                          '2. Поиграйте в настольные игры\n'
                                          '3. Посетите «ночь кино» или организуйте её самостоятельно \n'
                                          '4. Займитесь волонтерской деятельностью \n'
                                          '5. Отправьтесь на природу')

    elif message.text == 'Сходите в торговый центр за новыми покупочками':
        bot.send_message(message.chat.id,
                         'Кажется, сейчас все уже можно найти в интернете. Ловите ссылку на сайт, где вы найдете все, '
                         'чего душе угодно')
        bot.send_message(message.chat.id, 'https://www.wildberries.ru/')


def films(message):
    if message.text == 'Ужасы':
        bot.send_message(message.chat.id,
                         'Предлагаем посмотреть Вам фильм: "Оцепеневшие от страха"')
        bot.send_message(message.chat.id,
                         'Вот ссылка на него:"https://lo1.lordfilm1.co/31130-ocepenevshie-ot-straha-2018.html"')
    if message.text == 'Мелодрама':
        bot.send_message(message.chat.id,
                         'Предлагаем посмотреть Вам фильм: "Это все он"')
        bot.send_message(message.chat.id,
                         'Вот ссылка на него:" https://kinotom.me/eto-vse-on-2021"')
    if message.text == 'Комедия':
        bot.send_message(message.chat.id,
                         'Предлагаем посмотреть Вам фильм: "Смешанные"')
        bot.send_message(message.chat.id,
                         'Вот ссылка на него:"https://www.hdfilmfinest.com/load/komedii/9854-smeshannye.html"')
    if message.text == 'Драма':
        bot.send_message(message.chat.id,
                         'Предлагаем посмотреть Вам фильм: "Семья по быстрому"')
        bot.send_message(message.chat.id,
                         'Вот ссылка на него:"https://www.hdfilmfinest.com/load/komedii/13828-semya-po-bystromu.html"')
    if message.text == 'Мультфильм':
        bot.send_message(message.chat.id,
                         'Предлагаем посмотреть Вам фильм: "Большой кошачий побег"')
        bot.send_message(message.chat.id,
                         'Вот ссылка на него:"https://www.youtube.com/watch?v=GVE74QM-9A4&themeRefresh=1"')
    if message.text == 'Научная фантастика':
        bot.send_message(message.chat.id,
                         'Предлагаем посмотреть Вам фильм: "Мятежная луна"')
        bot.send_message(message.chat.id,
                         'Вот ссылка на него:"https://lordserials.cx/3152-rebel-moon-part-one-a-child-of-fire.html"')


def coord(message):
    adr = message.text
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode" \
                       f"='{adr}'&format=json"

    # Выполняем запрос.
    response = requests.get(geocoder_request)
    if response:
        # Преобразуем ответ в json-объект
        json_response = response.json()

        # Получаем первый топоним из ответа геокодера.
        # Согласно описанию ответа, он находится по следующему пути:
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        # Полный адрес топонима:
        toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
        # Координаты центра топонима:
        toponym_coodrinates = toponym["Point"]["pos"]
        # Печатаем извлечённые из ответа поля:
        bot.send_message(message.chat.id, f'{toponym_address} имеет координаты: {toponym_coodrinates}')
    else:
        bot.send_message(message.chat.id, "Ошибка выполнения запроса:")
        bot.send_message(message.chat.id, f'{geocoder_request}')
        bot.send_message(message.chat.id, f"Http статус: {response.status_code} ({response.reason})")


@bot.message_handler(content_types=['text'])
def info(message):
    if message.text.lower() == 'привет':
        bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}')
    elif message.text.lower() == 'id':
        bot.reply_to(message, f'ID: {message.from_user.id}')


bot.polling(none_stop=True)
