import random
import telebot
from telebot import types
from telebot import apihelper
import database as db  # Подключаем наш файл с базой данных

# Шлюз вашей приватки
apihelper.API_URL = "http://31.76.10.121:8081/bot{0}/{1}"

# Токен вашего бота
TOKEN = '1780243268:p6o-dDeWHJUqTSrmQMXSCtNIG3D6cYxiN1K'
bot = telebot.TeleBot(TOKEN)

# Список администраторов по юзернеймам
ADMIN_USERNAMES = ["lolpop", "blacktimeusa"]

# Временные состояния для ввода (ставка или вывод)
user_states = {}

def is_admin(message):
    username = message.from_user.username
    if not username:
        return False
    return username.lower().lstrip('@') in ADMIN_USERNAMES

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🎲 Игры и казино", "✍️ Ввести свою ставку")
    markup.row("⭐ Мой баланс", "💳 Пополнить ⭐")
    markup.row("💸 Вывести звёзды")
    return markup

def games_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🎲 Кубик", "🎰 Слоты")
    markup.row("🎯 Дартс", "⚽ Футбол")
    markup.row("🏀 Баскетбол", "🔙 Назад в меню")
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    username = message.from_user.username
    
    # Регистрируем или обновляем пользователя в базе данных
    db.register_user(user_id, username)
        
    stars = db.get_stars(user_id)
    bet = db.get_bet(user_id)
    user_states[user_id] = None
    
    welcome_text = (
        f"⭐ **VirusGram Star Casino** ⭐\n\n"
        f"Привет, {user_name}!\n"
        f"💳 Твой баланс: **{stars} ⭐**\n"
        f"⚙️ Текущая ставка: **{bet} ⭐**\n\n"
        f"Данные успешно сохраняются в базу данных! Выбирай игру 👇"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=main_menu())

# --- АДМИН-ПАНЕЛЬ ---
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if not is_admin(message):
        bot.send_message(message.chat.id, "❌ У вас нет прав администратора.")
        return
        
    admin_text = (
        f"👑 **Панель Администратора**\n\n"
        f"Команды управления балансом по нику:\n"
        f"🔹 **Выдать баланс:** `/give юзер_нейм СУММА`\n"
        f"🔹 **Забрать/списать:** `/take юзер_нейм СУММА`\n\n"
        f"_Пример:_ `/give blacktimeusa 500`"
    )
    bot.send_message(message.chat.id, admin_text, parse_mode="Markdown")

@bot.message_handler(commands=['give'])
def admin_give(message):
    if not is_admin(message):
        return
    try:
        parts = message.text.split()
        target_username = parts[1].lower().lstrip('@')
        amount = int(parts[2])
        
        target_id = db.get_user_id_by_username(target_username)
        if not target_id:
            bot.send_message(message.chat.id, f"❌ Пользователь @{target_username} не найден в базе данных.")
            return
            
        current_stars = db.get_stars(target_id)
        new_stars = current_stars + amount
        db.update_stars(target_id, new_stars)
        
        bot.send_message(message.chat.id, f"✅ Успешно! @{target_username} зачислено **{amount} ⭐**.\nБаланс: {new_stars} ⭐", parse_mode="Markdown")
        try:
            bot.send_message(target_id, f"🎁 Администратор пополнил ваш баланс на **{amount} ⭐**!\n💳 Текущий баланс: {new_stars} ⭐", parse_mode="Markdown")
        except Exception:
            pass
    except Exception:
        bot.send_message(message.chat.id, "❌ Ошибка формата! Используйте: `/give юзер СУММА`", parse_mode="Markdown")

@bot.message_handler(commands=['take'])
def admin_take(message):
    if not is_admin(message):
        return
    try:
        parts = message.text.split()
        target_username = parts[1].lower().lstrip('@')
        amount = int(parts[2])
        
        target_id = db.get_user_id_by_username(target_username)
        if not target_id:
            bot.send_message(message.chat.id, f"❌ Пользователь @{target_username} не найден.")
            return
            
        current_stars = db.get_stars(target_id)
        new_stars = max(0, current_stars - amount)
        db.update_stars(target_id, new_stars)
        
        bot.send_message(message.chat.id, f"✅ Успешно! У @{target_username} списано **{amount} ⭐**.\nОстаток: {new_stars} ⭐", parse_mode="Markdown")
        try:
            bot.send_message(target_id, f"⚠️ Администратор списал с вашего баланса **{amount} ⭐**.\n💳 Баланс: {new_stars} ⭐", parse_mode="Markdown")
        except Exception:
            pass
    except Exception:
        bot.send_message(message.chat.id, "❌ Ошибка формата! Используйте: `/take юзер СУММА`", parse_mode="Markdown")
# --------------------

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    username = message.from_user.username
    
    # Обновляем юзернейм в базе при каждом сообщении
    db.register_user(user_id, username)
        
    user_username = f"@{username}" if username else f"ID: {user_id}"
    text = message.text.strip()
    current_state = user_states.get(user_id)
    
    if text == "⭐ Мой баланс":
        user_states[user_id] = None
        stars = db.get_stars(user_id)
        bet = db.get_bet(user_id)
        bot.send_message(message.chat.id, f"💳 Твой баланс: **{stars} ⭐**\n⚙️ Текущая ставка: **{bet} ⭐**\n👤 Ник: @{username if username else 'нет'}", parse_mode="Markdown")
        
    elif text == "💳 Пополнить ⭐":
        user_states[user_id] = None
        bot.send_message(
            message.chat.id, 
            f"💳 **Пополнение баланса звёздами:**\n\n"
            f"1. Переведите нужную сумму звёзд администратору: **@lolpop** или **@Blacktimeusa**\n"
            f"2. Напишите админу в ЛС и укажите свой юзернейм (`@{username if username else str(user_id)}`).\n"
            f"Админ зачислит монеты через команду `/give`!", 
            parse_mode="Markdown"
        )
        
    elif text == "✍️ Ввести свою ставку":
        user_states[user_id] = "waiting_for_bet"
        bot.send_message(message.chat.id, "✍️ **Введите желаемую сумму ставки числом в чат**\n_Например:_ `100`", parse_mode="Markdown")
        
    elif text == "🎲 Игры и казино":
        user_states[user_id] = None
        bot.send_message(message.chat.id, "🎮 Выберите игру из каталога ниже:", reply_markup=games_menu())
        
    elif text == "🔙 Назад в меню":
        user_states[user_id] = None
        bot.send_message(message.chat.id, "Главное меню:", reply_markup=main_menu())
        
    elif text == "💸 Вывести звёзды":
        stars = db.get_stars(user_id)
        if stars < 100:
            bot.send_message(message.chat.id, f"❌ Минимальная сумма для вывода: **100 ⭐**.\nУ тебя на балансе: {stars} ⭐.")
            return
            
        user_states[user_id] = "waiting_for_withdraw"
        bot.send_message(
            message.chat.id,
            f"💸 **Вывод звёзд**\n💳 Твой баланс: **{stars} ⭐**\n📉 Мин. сумма: **100 ⭐**\n\n👉 **Введите числом количество звёзд для вывода:**",
            parse_mode="Markdown"
        )
            
    elif text.isdigit():
        number = int(text)
        stars = db.get_stars(user_id)
        
        if current_state == "waiting_for_bet":
            if number <= 0:
                bot.send_message(message.chat.id, "❌ Ставка должна быть больше нуля!")
                return
            if stars < number:
                bot.send_message(message.chat.id, f"❌ Недостаточно звёзд! Баланс: **{stars} ⭐**", parse_mode="Markdown")
                return
                
            db.update_bet(user_id, number)
            user_states[user_id] = None
            bot.send_message(message.chat.id, f"✅ Ставка установлена: **{number} ⭐**!", parse_mode="Markdown", reply_markup=games_menu())
            
        elif current_state == "waiting_for_withdraw":
            if number < 100:
                bot.send_message(message.chat.id, "❌ Минимальная сумма вывода — **100 ⭐**!", parse_mode="Markdown")
                return
            if stars < number:
                bot.send_message(message.chat.id, f"❌ Недостаточно звёзд для вывода **{number} ⭐**.\nБаланс: **{stars} ⭐**", parse_mode="Markdown")
                return
                
            new_balance = stars - number
            db.update_stars(user_id, new_balance)
            user_states[user_id] = None
            
            bot.send_message(
                message.chat.id, 
                f"🚀 **Заявка на вывод {number} ⭐ создана!**\nОстаток: {new_balance} ⭐", 
                parse_mode="Markdown",
                reply_markup=main_menu()
            )
            
            admin_notification = (
                f"🚨 **ЗАЯВКА НА ВЫВОД ЗВЁЗД!**\n\n"
                f"👤 Пользователь: {user_username} (ID: `{user_id}`)\n"
                f"💰 Сумма: **{number} ⭐**"
            )
            for adm_name in ADMIN_USERNAMES:
                adm_id = db.get_user_id_by_username(adm_name)
                if adm_id:
                    try:
                        bot.send_message(adm_id, admin_notification, parse_mode="Markdown")
                    except Exception:
                        pass
        else:
            bot.send_message(message.chat.id, "Используйте кнопки меню 👇", reply_markup=main_menu())

    # --- ИГРОВАЯ ЛОГИКА ---
    elif text in ["🎲 Кубик", "🎰 Слоты", "🎯 Дартс", "⚽ Футбол", "🏀 Баскетбол"]:
        user_states[user_id] = None
        bet = db.get_bet(user_id)
        stars = db.get_stars(user_id)
        
        if stars < bet:
            bot.send_message(message.chat.id, f"❌ Недостаточно звёзд! Ставка {bet} ⭐, баланс {stars} ⭐.")
            return
            
        # Списываем ставку
        db.update_stars(user_id, stars - bet)
        current_stars = db.get_stars(user_id)
        
        if text == "🎲 Кубик":
            val = random.randint(1, 6)
            if val >= 4:
                win = bet * 2
                db.update_stars(user_id, current_stars + win)
                bot.send_message(message.chat.id, f"🎲 Кубик: **{val}**\n🏆 Победа! +{win} ⭐\n💳 Баланс: {db.get_stars(user_id)} ⭐", parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, f"🎲 Кубик: **{val}**\n😢 Проигрыш (-{bet} ⭐).\n💳 Баланс: {db.get_stars(user_id)} ⭐", parse_mode="Markdown")
                
        elif text == "🎰 Слоты":
            chance = random.randint(1, 10)
            if chance == 10:
                win = bet * 10
                db.update_stars(user_id, current_stars + win)
                bot.send_message(message.chat.id, f"🎰 **ДЖЕКПОТ!** 7️⃣ 7️⃣ 7️⃣\n🔥 Выиграно **{win} ⭐**!\n💳 Баланс: {db.get_stars(user_id)} ⭐", parse_mode="Markdown")
            elif chance >= 7:
                win = bet * 2
                db.update_stars(user_id, current_stars + win)
                bot.send_message(message.chat.id, f"🎰 **Удача!** 🍋 🍋 🍒\n✨ Выиграно **{win} ⭐**!\n💳 Баланс: {db.get_stars(user_id)} ⭐", parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, f"🎰 **Мимо!**\n😢 Ставка {bet} ⭐ сгорела.\n💳 Баланс: {db.get_stars(user_id)} ⭐", parse_mode="Markdown")
                
        elif text == "🎯 Дартс":
            hit = random.choice([True, False, False])
            if hit:
                win = int(bet * 2.5)
                db.update_stars(user_id, current_stars + win)
                bot.send_message(message.chat.id, f"🎯 **В яблочко!**\n🏆 Выиграно **{win} ⭐**!\n💳 Баланс: {db.get_stars(user_id)} ⭐", parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, f"🎯 Мимо мишени!\n😢 Ставка {bet} ⭐ сгорела.\n💳 Баланс: {db.get_stars(user_id)} ⭐", parse_mode="Markdown")
                
        elif text == "⚽ Футбол":
            goal = random.choice([True, False])
            if goal:
                win = bet * 2
                db.update_stars(user_id, current_stars + win)
                bot.send_message(message.chat.id, f"⚽ **ГОЛ!**\n🏆 Выиграно **{win} ⭐**!\n💳 Баланс: {db.get_stars(user_id)} ⭐", parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, f"⚽ Вратарь поймал мяч!\n😢 Ставка {bet} ⭐ сгорела.\n💳 Баланс: {db.get_stars(user_id)} ⭐", parse_mode="Markdown")
                
        elif text == "🏀 Баскетбол":
            basket = random.choice([True, False, False])
            if basket:
                win = int(bet * 3)
                db.update_stars(user_id, current_stars + win)
                bot.send_message(message.chat.id, f"🏀 **ТРИ ОЧКА!**\n🏆 Выиграно **{win} ⭐**!\n💳 Баланс: {db.get_stars(user_id)} ⭐", parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, f"🏀 Мяч отскочил от кольца!\n😢 Ставка {bet} ⭐ сгорела.\n💳 Баланс: {db.get_stars(user_id)} ⭐", parse_mode="Markdown")
    else:
        user_states[user_id] = None
        bot.send_message(message.chat.id, "Используйте кнопки меню 👇", reply_markup=main_menu())

if __name__ == '__main__':
    print("Бот запущен с базой данных SQLite!")
    bot.infinity_polling(skip_pending=True)
