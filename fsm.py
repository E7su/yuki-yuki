# -*- coding: utf-8 -*-

import logging as log
import re

import telegram as tm
import texts as tx

import MySQLdb
from conf.config import mysql_host, mysql_user, mysql_passwd, mysql_db

# -- base types -----------------------------------------------------------


class State(object):

    def on_trigger(self, trigger):
        pass

    def _on_trigger(self, trigger):
        log.debug('== ' + str(self))
        return self.on_trigger(trigger)

    def on_enter(self, trigger):
        pass

    def _on_enter(self, trigger):
        log.debug('-> ' + str(self))
        return self.on_enter(trigger)

    def on_exit(self, trigger):
        pass

    def _on_exit(self, trigger):
        log.debug('<- ' + str(self))
        return self.on_exit(trigger)


class Filter(object):

    def __init__(self):
        pass

    def on_process(self, current_state, trigger):
        pass

    def _on_process(self, current_state, trigger):
        log.debug(':: ' + type(self).__name__)
        return self.on_process(current_state, trigger)


class StateMachine(object):

    def __init__(self, user):
        self.state = BootStrapState()
        self.user = user
        self.filters = [StartFilter(),
                        FeedbackFilter(),
                        PoliteFilter()]

    def fire(self, trigger):
        trigger.user = self.user

        for f in self.filters:
            filtered_state = f._on_process(self.state, trigger)
            if filtered_state:
                self.to_state(filtered_state, trigger)
                return

        new_state = self.state._on_trigger(trigger)
        self.to_state(new_state, trigger)

    def to_state(self, new_state, trigger):
        if not new_state:
            return self.state

        if new_state == self.state:
            reenter_state = self.state._on_enter(trigger)
            self.to_state(reenter_state, trigger)
            return

        exit_state = self.state._on_exit(trigger)
        if exit_state:
            self.to_state(exit_state, trigger)
            return

        self.state = new_state

        enter_state = self.state._on_enter(trigger)
        if enter_state:
            self.to_state(enter_state, trigger)
            return


class TelegramTrigger(object):

    def __init__(self):
        self.user = None
        self.bot = None
        self.update = None

    def get_chat_id(self):
        return self.update.message.chat_id if self.update else None

    def get_txt(self):
        return self.update.message.text if self.update else None

    def get_name(self):
        user = self.update.message.from_user
        return user.first_name if user.first_name else user.username

    def send_msg(self, txt):
        self.bot.sendMessage(chat_id=self.chat_id,
                             text=txt,
                             disable_web_page_preview=True,
                             parse_mode=tm.ParseMode.MARKDOWN)

    def send_keys(self, txt, keyboard):
        reply_markup = tm.ReplyKeyboardMarkup(keyboard=keyboard,
                                              resize_keyboard=True,
                                              one_time_keyboard=True)

        self.bot.sendMessage(chat_id=self.chat_id,
                             text=txt,
                             disable_web_page_preview=True,
                             parse_mode=tm.ParseMode.MARKDOWN,
                             reply_markup=reply_markup)

    def send_photo(self, src):
        self.bot.sendPhoto(chat_id=self.chat_id, photo=src)

    # will call 'get_chat_id' when accessing like obj.chat_id
    chat_id = property(get_chat_id)
    txt = property(get_txt)
    name = property(get_name)


# -- states ---------------------------------------------------------------


class BootStrapState(State):

    def on_trigger(self, trigger):
        return RootState()


class RootState(State):

    def on_enter(self, trigger):
        trigger.send_keys(u'Что будем заказывать?',
                          [[u'Супы', u'Второе',
                            u'Напитки', u'Десерты', u'Суши']])

    def on_trigger(self, trigger):
        num_type = None

        msg = (u'супы')

        if tx.equals(trigger.txt, msg):
            num_type = 1

        msg = (u'второе')

        if tx.equals(trigger.txt, msg):
            num_type = 2

        msg = (u'напитки')

        if tx.equals(trigger.txt, msg):
            num_type = 3

        msg = (u'десерты')

        if tx.equals(trigger.txt, msg):
            num_type = 4

        msg = (u'суши')

        if tx.equals(trigger.txt, msg):
           num_type = 5

        if not num_type:
            trigger.send_msg(u'Извини, не понял')
            return self

        if num_type:
            return AskSystemState(num_type)

        return self


class AskSystemState(State):

    def __init__(self, num_type):
        self.num_type = num_type

    def on_enter(self, trigger):
        log.debug('mysql_host=%s, mysql_user=%s, mysql_passwd=%s, mysql_db=%s', 
                   mysql_host, mysql_user, mysql_passwd, mysql_db)
        db = MySQLdb.connect(host=mysql_host, user=mysql_user, passwd=mysql_passwd, db=mysql_db)
        #db = MySQLdb.connect(host=mysql_host, user=mysql_user, passwd=mysql_passwd, db=mysql_db, charset='utf8')
        cursor = db.cursor()
        # запросы с использованием cursor
        
        cursor.execute("SET NAMES utf8;") #or utf8 or any other charset you want to handle
        cursor.execute("SET CHARACTER SET utf8;") #same as above
        cursor.execute("SET character_set_connection=utf8;") #same as above
        
        cursor.execute("""select name, price, link from yuki.yuki where category = %s""", (self.num_type,))
        name, price, link = cursor.fetchone() # TODO:all
        name, link = name.encode('utf-8'), link.encode('utf-8')  # WTF?
        name = name.decode('utf-8')
        # TODO: remove hardcode
        trigger.send_msg('1 - Венгерский суп-гуляш') 
        trigger.send_msg('Цена: %s' % price)
        trigger.send_photo('http://gotovim-doma.ru/images/recipe/6/40/64098f9e72a9cc65260d1e920f68d194_l.jpg')

        name, price, link = cursor.fetchone() # TODO:all
        name, link = name.encode('utf-8'), link.encode('utf-8')  # WTF?
        name = name.decode('utf-8')
        trigger.send_msg('2 - Суп в томатном соусе') 
        trigger.send_msg('Цена: %s' % price)
        trigger.send_photo('http://natural-balkan.com/wp-content/uploads/2013/02/DSCN1738.jpg')
        db.close()
        trigger.send_keys(u'Какой выбирете?',
                        [[u'1', u'2', u'Назад']])
        


    def on_trigger(self, trigger):
        global cur_name
        cur_name = None

        if tx.equals(trigger.txt, u'1'):
            cur_name = u'Венгерский суп-гуляш'

        elif tx.equals(trigger.txt, (u'2')):
            cur_name = u'Суп в томатном соусе'
        try:
            msg = u'Выбран %s. Всё верно?' % cur_name.lower()
        except Exception:
            return AnotherState()
        trigger.send_keys(msg, [['Да, всё в порядке', 'Нет, неверно']])
        # TODO: add else statement ('Извини')

        msg = (u'нет, неверно')
        if tx.equals(trigger.txt, msg):
            return AskSystemState(self.num_state)
        else:  # tx.equals(trigger.txt, u'да, всё в порядке'):
            return AnotherState()

        return self


class AnotherState(State):
    def on_enter(self, trigger):
        trigger.send_keys(u'Хотите выбрать что-либо ещё?',
                             [[u'Да, хочу', u'Нет, спасибо']])

    def on_trigger(self, trigger):
       if tx.equals(trigger.txt, 'да, хочу'):
           return RootState()
       elif tx.equals(trigger.txt, 'нет, спасибо'):
           trigger.send_msg(u'Ваш заказ передан на исполнение. Оставайтесь на связи!')



class FeedbackState(State):

    def on_enter(self, trigger):
        trigger.send_msg(u'В целях улучшения качества обслуживания '
                         u'все разговоры записываются ;) Напиши свои мысли')

    def on_trigger(self, trigger):
        log.warn('feedback: ' + str(trigger.update))
        trigger.send_msg(u'Спасибо!')

        return RootState()


# -- filters  -------------------------------------------------------------

class StartFilter(Filter):

    def on_process(self, current_state, trigger):
        if tx.is_command(trigger.txt, '/start|/help'):

            trigger.send_msg(u'Если у тебя что-то пошло не так '
                             u'или ты хочешь поделиться с нами своими '
                             u'мыслями - просто напиши в чате /feedback '
                             u'и опиши, что случилось. '
                             u'Мы обязательно что-нибудь придумаем!')

            return RootState()


class PoliteFilter(Filter):
    def on_process(self, current_state, trigger):
        if tx.equals(trigger.txt, u'привет|здравствуй|хай|hello|hallo|hi'):
            trigger.send_msg(u'Привет, {}! ^^'.format(trigger.name))

            if type(current_state) == BootStrapState:
                return RootState()

            return current_state

        byes = (u'пока|до свидания|бб|66|бай-бай|пока-пока'
                u'|goodbye|спокойной ночи')

        if tx.equals(trigger.txt, byes):
            trigger.send_msg(u'Пока, {}! :3'.format(trigger.name))
            return BootStrapState()


class FeedbackFilter(Filter):

    def on_process(self, current_state, trigger):
        if tx.is_command(trigger.txt, '/feedback'):
            return FeedbackState()
