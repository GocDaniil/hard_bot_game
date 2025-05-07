import telebot
import random

from telebot import types


class HardBotGame:
    def __init__(self):
        self.bot = telebot.TeleBot("YOUR_TOKEN")

        self.bot_health = 150
        self.player_health = 150
        self.sword_damage = 0.20
        self.bow_damage = 0.25
        self.medicine_boost = 0.30
        self.grenade_damage = 0.35

        self.bot_medicine_piece = 3
        self.bot_grenade_piece = 2
        self.player_medicine_piece = 3
        self.player_grenade_piece = 2

        self.protection_counter = 0

        self.location = ""
        self.is_polling = False
        self.game_over = False
        self.setup_handlers()

    def setup_handlers(self):
        @self.bot.message_handler(commands=['start'])
        def start(message):
            self.bot_health = 150
            self.player_health = 150
            self.bot_medicine_piece = 3
            self.bot_grenade_piece = 2
            self.player_medicine_piece = 3
            self.player_grenade_piece = 2

            self.game_over = False
            self.location = self.random_location()

            description = self.location
            if self.location == "Огненные каньоны":
                description += ". Меч может поджечь с шансом 10%."
            elif self.location == "Ледяные холмы":
                description += ". Стрелы имеют 8-% вероятность стать ледяными, нанося дополнительный урон."

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn_sword = types.KeyboardButton("⚔️ Меч")
            btn_bow = types.KeyboardButton("🏹 Лук")
            btn_shield = types.KeyboardButton("🛡 Щит")
            btn_evade = types.KeyboardButton("💨 Уклониться")
            btn_medicine = types.KeyboardButton("💊 Аптечка")
            btn_grenade = types.KeyboardButton("🧨 Граната")
            markup.add(btn_sword, btn_bow, btn_shield, btn_evade, btn_medicine, btn_grenade)

            self.bot.send_message(message.chat.id, f"{description}\n"
                                       "Игра начинается! Снаряжение и механика игры:\n"
                                       "\n"
                                       "Меч - 20% урона, уменьшается щитом\n"
                                       "Лук - 25% урона, можно уклониться\n"
                                       "\n"
                                       "Щит - снижает до 15% атаки\n"
                                       "Уклонение - увернуться от лука\n"
                                       "\n"
                                       "Аптечка - восстанавливает 30% здоровья (3 шт)\n"
                                       "Граната - 35% урона, пробивает защиту, нельзя уклониться (2 шт)\n"
                                       "\n"
                                       "Здоровье у вас и вашего противника: 150 HP")
            self.bot.send_message(message.chat.id, "Выберите действие:\n"
                                       "\n"
                                       "1 - Меч\n"
                                       "2 - Лук\n"
                                       "3 - Щит\n"
                                       "4 - Уклонение\n"
                                       "5 - Аптечка\n"
                                       "6 - Граната".format(message.from_user), reply_markup=markup)

        @self.bot.message_handler(func=lambda message: message.text in ['1', '2', '3', '4', '5', '6',
                         '⚔️ Меч', '🏹 Лук', '🛡 Щит', '💨 Уклониться', '💊 Аптечка', '🧨 Граната'])
        def handle_action(message):
            if self.game_over:
                return
            self.choosing_action(message)

    def choosing_action(self, message):
        if self.game_over:
            return

        if message.text == '1' or message.text == '⚔️ Меч':

            chance = random.randint(1, 100)

            if chance <= 10 and self.location == "Огненные каньоны":
                self.bot_health -= 150 * (self.sword_damage + 0.05)
                self.bot.send_message(message.chat.id, "Критический удар! Меч поджигает противника.")
            else:
                self.bot_health -= 150 * self.sword_damage
                self.bot.send_message(message.chat.id, "Вы атакуете противника мечем.")

            self.equipment = "Меч"
            self.bot_action(message.chat.id)
            self.victory(message.chat.id)

        elif message.text == '2' or message.text == '🏹 Лук':
            chance = random.randint(1, 100)
            if chance <= 8 and self.location == "Ледяные холмы":
                self.bot_health -= 150 * (self.bow_damage + 0.05)
                self.bot.send_message(message.chat.id, "Вы выпустили ледяную стрелу.")
            else:
                self.bot_health -= 150 * self.bow_damage
                self.bot.send_message(message.chat.id, "Вы выстрелили из лука.")

            self.equipment = "Лук"
            self.bot_action(message.chat.id)
            self.victory(message.chat.id)

        elif message.text == '3' or message.text == '🛡 Щит':

            self.equipment = "Щит"
            self.bot_action(message.chat.id)
            self.victory(message.chat.id)

            if self.equipment == "Меч":
                self.player_health += 150 * self.sword_damage
                self.bot.send_message(message.chat.id, f"Вы защитились. Ваше здоровье: {self.player_health}")

            elif self.equipment == "Лук":
                self.bot.send_message(message.chat.id, f"Вас прострелили через щит! Ваше здоровье: {self.player_health}")

        elif message.text == '4' or message.text == '💨 Уклониться':
            self.bot.send_message(message.chat.id, f"Вы уклонились. Ваше здоровье: {self.player_health}")

            self.equipment = "Уклонение"
            self.bot_action(message.chat.id)
            self.victory(message.chat.id)

        elif message.text == '5' or message.text == '💊 Аптечка':
            if self.player_medicine_piece >= 1:
                self.player_health += 150 * self.medicine_boost
                self.bot.send_message(message.chat.id, f"Вы использовали аптечку ({self.player_medicine_piece-1}/3). Ваше здоровье: {self.player_health}")

                self.player_medicine_piece -= 1

                self.equipment = "Аптечка"
                self.bot_action(message.chat.id)
                self.victory(message.chat.id)
            else:
                self.bot.send_message(message.chat.id, f"У вас закончились аптечки. Выберите другое действие.")

        else:
            if self.player_grenade_piece >= 1:
                self.bot_health -= 150 * self.grenade_damage
                self.bot.send_message(message.chat.id, f"Вы бросили гранату ({self.player_grenade_piece-1}/2).")

                self.player_grenade_piece -= 1

                self.equipment = "Граната"
                self.bot_action(message.chat.id)
                self.victory(message.chat.id)
            else:
                self.bot.send_message(message.chat.id, f"У вас закончились гранаты. Выберите другое действие.")

    def bot_action(self, chat_id):
        if self.game_over:
            return

        if self.bot_health <= 60:
            if self.bot_medicine_piece >= 1:
                self.bot_health += 150 * self.medicine_boost
                self.bot.send_message(chat_id, f"Противник использовал аптечку. Его здоровье: {self.bot_health}")

                self.bot_medicine_piece -= 1
                self.equipment = "Аптечка"
                self.victory(chat_id)
                return

        if self.player_health <= 52.5:
            if self.bot_grenade_piece >= 1:
                self.player_health -= 150 * self.grenade_damage
                self.bot.send_message(chat_id, f"Противник подорвал гранату. Ваше здоровье: {self.player_health}")

                self.bot_grenade_piece -= 1
                self.equipment = "Граната"
                self.victory(chat_id)
                return

        if self.equipment == "Меч":
            if self.protection_counter <= 0:
                self.bot_health += 150 * (self.sword_damage - 0.05)
                self.bot.send_message(chat_id, f"Противник защитился, вы нанесли 5% урона. Его здоровье: {self.bot_health}")

                self.protection_counter += 1
                self.equipment = "Щит"
                self.victory(chat_id)
            else:
                chance = random.randint(1, 100)
                if chance <= 8 and self.location == "Ледяные холмы":
                    self.player_health -= 150 * (self.bow_damage + 0.05)
                    self.bot.send_message(chat_id, f"Противник выпустил ледяную стрелу. Ваше здоровье: {self.player_health}")
                else:
                    self.player_health -= 150 * self.bow_damage
                    self.bot.send_message(chat_id, f"Противник использовал лук. Ваше здоровье: {self.player_health}")

                self.protection_counter = 0
                self.equipment = "Лук"
                self.victory(chat_id)

        elif self.equipment == "Лук":
            if self.protection_counter <= 1:

                self.miss_chance = random.randint(1, 100)

                if self.miss_chance <= 5:
                    self.bot_health += 150 * (self.bow_damage - 0.06)
                    self.bot.send_message(chat_id, f"Противник уклонился, но вы его задели. Его здоровье: {self.bot_health}")
                else:
                    self.bot_health += 150 * self.bow_damage
                    self.bot.send_message(chat_id,f"Противник уклонился. Его здоровье: {self.bot_health}")

                self.protection_counter += 1
                self.equipment = "Уклонение"
                self.victory(chat_id)
            else:
                chance = random.randint(1, 100)
                if chance <= 8 and self.location == "Ледяные холмы":
                    self.player_health -= 150 * (self.bow_damage + 0.05)
                    self.bot.send_message(chat_id,f"Противник выпустил ледяную стрелу. Ваше здоровье: {self.player_health}")
                else:
                    self.player_health -= 150 * self.bow_damage
                    self.bot.send_message(chat_id, f"Противник использовал лук. Ваше здоровье: {self.player_health}")

                self.protection_counter = 0
                self.equipment = "Лук"
                self.victory(chat_id)

        elif self.equipment == "Щит":
            if self.bot_grenade_piece >= 1:
                self.player_health -= 150 * self.grenade_damage
                self.bot.send_message(chat_id, f"Противник подорвал гранату. Ваше здоровье: {self.player_health}")

                self.bot_grenade_piece -= 1
                self.equipment = "Граната"
                self.victory(chat_id)
            else:
                chance = random.randint(1, 100)
                if chance <= 8 and self.location == "Ледяные холмы":
                    self.player_health -= 150 * (self.bow_damage + 0.05)
                    self.bot.send_message(chat_id,f"Противник выпустил ледяную стрелу. Ваше здоровье: {self.player_health}")
                else:
                    self.player_health -= 150 * self.bow_damage
                    self.bot.send_message(chat_id, f"Противник использовал лук. Ваше здоровье: {self.player_health}")

                self.equipment = "Лук"
                self.victory(chat_id)

        elif self.equipment == "Уклонение":
            if self.bot_grenade_piece >= 1:
                self.player_health -= 150 * self.grenade_damage
                self.bot.send_message(chat_id, f"Противник подорвал гранату. Ваше здоровье: {self.player_health}")

                self.bot_grenade_piece -= 1
                self.equipment = "Граната"
                self.victory(chat_id)
            else:
                chance = random.randint(1, 100)

                if chance <= 10 and self.location == "Огненные каньоны":
                    self.player_health -= 150 * (self.sword_damage + 0.05)
                    self.bot.send_message(chat_id, f"Критический удар! Вас поджигают мечем. Ваше здоровье: {self.player_health}.")
                else:
                    self.player_health -= 150 * self.sword_damage
                    self.bot.send_message(chat_id, f"Противник атаковал мечем. Ваше здоровье: {self.player_health}")

                self.equipment = "Меч"
                self.victory(chat_id)

        elif self.equipment == "Аптечка":
            if self.bot_grenade_piece >= 1:
                self.player_health -= 150 * self.grenade_damage
                self.bot.send_message(chat_id, f"Противник подорвал гранату. Ваше здоровье: {self.player_health}")

                self.bot_grenade_piece -= 1
                self.equipment = "Граната"
                self.victory(chat_id)
            else:
                chance = random.randint(1, 100)
                if chance <= 8 and self.location == "Ледяные холмы":
                    self.player_health -= 150 * (self.bow_damage + 0.05)
                    self.bot.send_message(chat_id,f"Противник выпустил ледяную стрелу. Ваше здоровье: {self.player_health}")
                else:
                    self.player_health -= 150 * self.bow_damage
                    self.bot.send_message(chat_id, f"Противник использовал лук. Ваше здоровье: {self.player_health}")

                self.equipment = "Лук"
                self.victory(chat_id)

        else:
            if self.bot_grenade_piece >= 1:
                self.player_health -= 150 * self.grenade_damage
                self.bot.send_message(chat_id, f"Противник подорвал гранату. Ваше здоровье: {self.player_health}")

                self.bot_grenade_piece -= 1
                self.equipment = "Граната"
                self.victory(chat_id)
            else:
                chance = random.randint(1, 100)
                if chance <= 8 and self.location == "Ледяные холмы":
                    self.player_health -= 150 * (self.bow_damage + 0.05)
                    self.bot.send_message(chat_id,f"Противник выпустил ледяную стрелу. Ваше здоровье: {self.player_health}")
                else:
                    self.player_health -= 150 * self.bow_damage
                    self.bot.send_message(chat_id, f"Противник использовал лук. Ваше здоровье: {self.player_health}")

                self.equipment = "Лук"
                self.victory(chat_id)


    def victory(self, chat_id):
        if self.game_over:
            return

        if self.player_health <= 0:
            self.bot.send_message(chat_id, "Вы проиграли! Используйте /start, чтобы начать новую игру.")
            self.game_over = True

        elif self.bot_health <= 0:
            self.bot.send_message(chat_id, "Вы выиграли! Используйте /start, чтобы начать новую игру.")
            self.game_over = True

    def random_location(self):

        type = random.randint(1, 100)

        if type <= 34:
            self.location = """"""
        elif type >= 68:
            self.location = "Огненные каньоны"
        else:
            self.location = "Ледяные холмы"

        return self.location

    def play(self):
        if self.is_polling:
            self.bot.stop_polling()
        self.is_polling = True
        self.bot.polling(none_stop=True, skip_pending=True)


if __name__ == "__main__":
    game = HardBotGame()
    game.play()
