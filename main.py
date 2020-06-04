import os   # For remove file from dirrectory
import asana    # Library for working with asana API
import telebot  # Library for working with telegram API
from telebot import types
import config
import datetime
from builtins import Exception

BOT = telebot.TeleBot(config.TOKEN)  # Initialize BOT

CLIENT = asana.Client.access_token(config.TOKEN_ASANA)  # Initialize ASANA API

keyboard_hider = types.ReplyKeyboardRemove()

task = {}

@BOT.message_handler(content_types = ['text'])
def start_handler(message):
    try:
        if message.text == 'Выход':
            task.pop(message.chat.id)
            msg = BOT.send_message(message.chat.id, config.text_level_2, reply_markup = keyboard_hider)
            BOT.register_next_step_handler(msg, head_handler)
        else:
            task.update({message.chat.id: {}})
            print(f'''
            Дата: {datetime.datetime.today()}
            Пользователь {message.chat.first_name} начинает работу.
            Данные о задаче: {task[message.chat.id]}
            ''')
            msg = BOT.send_message(message.chat.id, config.text_level_1, reply_markup = keyboard_hider)
            BOT.register_next_step_handler(msg, head_handler)
    except Exception as e:
        print('Ошибка!')
        msg = BOT.send_message(message.chat.id, config.text_level_0, reply_markup = keyboard_hider)
        BOT.register_next_step_handler(msg, start_handler)

def head_handler(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard = True, resize_keyboard = True, row_width = 2)
    markup.add('Далее', 'Выход')
    try:
        task[message.chat.id].update({'head': message.text})
        task[message.chat.id].update({'assigne':[]})
        print(f'''
        Дата: {datetime.datetime.today()}
        Пользователь {message.chat.first_name} добавил
        заголовок к задаче: {task[message.chat.id]['head']}
        ''')
        msg = BOT.send_message(message.chat.id,config.text_level_3, reply_markup = markup)
        BOT.register_next_step_handler(msg, desc_handler)
    except Exception as e:
        print('Ошибка!')
        task.pop(message.chat.id)
        msg = BOT.send_message(message.chat.id, config.text_level_0, reply_markup = keyboard_hider)
        BOT.register_next_step_handler(msg, start_handler)

def desc_handler(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard = True, resize_keyboard = True, row_width = 2)
    markup.add('Далее', 'Назад', 'Выход')
    try:
        if message.text == 'Далее':
            task[message.chat.id].update({'desc': ''})
            print(f'''
            Дата: {datetime.datetime.today()}
            Пользователь {message.chat.first_name} пропустил описание.
                  ''')
            msg = BOT.send_message(message.chat.id, config.text_level_4, reply_markup= markup)
            BOT.register_next_step_handler(msg, photo_handler)
        elif message.text == 'Выход':
            task.pop(message.chat.id)
            print(f'''
            Дата: {datetime.datetime.today()}
            Пользователь {message.chat.first_name} закончил работу.
                  ''')
            msg = BOT.send_message(message.chat.id, config.text_level_5, reply_markup= keyboard_hider)
            BOT.register_next_step_handler(msg, start_handler)
        else:
            task[message.chat.id].update({'desc': message.text})
            print(f'''
            Дата: {datetime.datetime.today()}
            Пользователь {message.chat.first_name} добавил
            описание к задаче: {task[message.chat.id]['desc']}
            ''')
            msg = BOT.send_message(message.chat.id, config.text_level_6, reply_markup= markup)
            BOT.register_next_step_handler(msg, photo_handler)
    except Exception as e:
        print('Ошибка!')
        task.pop(message.chat.id)
        msg = BOT.send_message(message.chat.id, config.text_level_0, reply_markup = keyboard_hider)
        BOT.register_next_step_handler(msg, start_handler)


def photo_handler(message):
    try:
        if message.text == 'Далее':
            task[message.chat.id].update({'photo': ''})
            print(f'''
            Дата: {datetime.datetime.today()}
            Пользователь {message.chat.first_name} пропустил фото
                  ''')
            markup = types.ReplyKeyboardMarkup(one_time_keyboard = True, resize_keyboard = True, row_width = 2)
            for key in config.members.keys():
                markup.add(key)
            markup.add('Назад', 'Далее', 'Выход')
            msg = BOT.send_message(message.chat.id, config.text_level_7, reply_markup= markup)
            BOT.register_next_step_handler(msg, assigne_handler)
        elif message.text == 'Выход':
            task.pop(message.chat.id)
            print(f'''
            Дата: {datetime.datetime.today()}
            Пользователь {message.chat.first_name} закончил работу.
            ''')
            msg = BOT.send_message(message.chat.id, config.text_level_5, reply_markup= keyboard_hider)
            BOT.register_next_step_handler(msg, start_handler)
        elif message.text == 'Назад':
            task[message.chat.id].pop('desc')
            print(f'''
            Дата: {datetime.datetime.today()}
            Пользователь {message.chat.first_name} решил исправить описание
            ''')
            msg = BOT.send_message(message.chat.id, config.text_level_3, reply_markup= keyboard_hider)
            BOT.register_next_step_handler(msg, desc_handler)
        else:
            if message.photo == None and message.document == None:
                msg = BOT.send_message(message.chat.id, config.text_level_12, reply_markup= keyboard_hider)
                BOT.register_next_step_handler(msg, photo_handler)
            else:
                if message.photo == None:
                    file_info = BOT.get_file(message.document.file_id)
                    download_file = BOT.download_file(file_info.file_path)
                    task[message.chat.id].update({'photo': message.document.file_name})
                    src = 'D:/Python/BOT_ASANA/' + task[message.chat.id]['photo']
                    print(src)
                    with open(src, 'wb') as new_file:
                        new_file.write(download_file)
                    print(f'''
                    Дата: {datetime.datetime.today()}
                    Пользователь {message.chat.first_name} добавил
                    Фото {task[message.chat.id]['photo']}
                    ''')
                    markup = types.ReplyKeyboardMarkup(one_time_keyboard = True, resize_keyboard = True, row_width = 2)
                    for key in config.members.keys():
                        markup.add(key)
                    markup.add('Назад', 'Далее', 'Выход')
                    msg = BOT.send_message(message.chat.id, config.text_level_8, reply_markup= markup)
                    BOT.register_next_step_handler(msg, assigne_handler)
                elif message.document == None:
                    file_info = BOT.get_file(message.photo[len(message.photo)-1].file_id)
                    download_file = BOT.download_file(file_info.file_path)
                    task[message.chat.id].update({'photo': message.photo[len(message.photo)-1].file_id[0:5] + '.png'})
                    src = 'D:/Python/BOT_ASANA/' + task[message.chat.id]['photo']
                    with open(src, 'wb') as new_file:
                        new_file.write(download_file)
                    print(f'''
                    Дата: {datetime.datetime.today()}
                    Пользователь {message.chat.first_name} добавил
                    Фото {task[message.chat.id]['photo']}
                    ''')
                    markup = types.ReplyKeyboardMarkup(one_time_keyboard = True, resize_keyboard = True, row_width = 2)
                    for key in config.members.keys():
                        markup.add(key)
                    markup.add('Назад', 'Далее', 'Выход')
                    msg = BOT.send_message(message.chat.id, config.text_level_8, reply_markup= markup)
                    BOT.register_next_step_handler(msg, assigne_handler)
    except Exception as e:
        print('Ошибка!')
        task.pop(message.chat.id)
        msg = BOT.send_message(message.chat.id, config.text_level_0, reply_markup = keyboard_hider)
        BOT.register_next_step_handler(msg, start_handler)

def assigne_handler(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard = True, resize_keyboard = True, row_width = 2)
    markup.add('Далее', 'Выход')
    try:
        if message.text == 'Далее':
            print(f'''
            Дата: {datetime.datetime.today()}
            Пользователь {message.chat.first_name} закончил работу.
            Заголовок {task[message.chat.id]['head']}
            Описание {task[message.chat.id]['desc']}
            Фото {task[message.chat.id]['photo']}
            ''')
            if task[message.chat.id]['assigne'] != []:
                CLIENT.tasks.create_in_workspace(
                    '719460696846217',
                    {'name': task[message.chat.id]['head'],
                     'notes': task[message.chat.id]['desc'],
                     'projects': '1154959099440115',
                     'followers':task[message.chat.id]['assigne']}
                )
            else:
                CLIENT.tasks.create_in_workspace(
                    '719460696846217',
                    {'name': task[message.chat.id]['head'],
                     'notes': task[message.chat.id]['desc'],
                     'projects': '1154959099440115'}
                )
            if len(task[message.chat.id]['photo']) > 0:
                for tasks in CLIENT.tasks.find_all({'project':'1154959099440115'}):
                    print(tasks)
                    if tasks['name'] == task[message.chat.id]['head']:
                        CLIENT.attachments.create_on_task(
                            task_id= tasks['gid'],
                            file_content= open('D:/Python/BOT_ASANA/' + task[message.chat.id]['photo'], 'rb'),
                            file_name= task[message.chat.id]['photo'],
                            file_content_type= None
                        )
                        os.remove('D:/Python/BOT_ASANA/' + task[message.chat.id]['photo'])
            msg = BOT.send_message(message.chat.id, config.text_level_9, reply_markup= keyboard_hider)
            BOT.register_next_step_handler(msg, start_handler)
        elif message.text == 'Выход':
            task.pop(message.chat.id)
            print(f'''
            Дата: {datetime.datetime.today()}
            Пользователь {message.chat.first_name} закончил работу.
            ''')
            msg = BOT.send_message(message.chat.id, config.text_level_5, reply_markup= keyboard_hider)
            BOT.register_next_step_handler(msg, start_handler)
        elif message.text == 'Назад':
            task[message.chat.id].pop('photo')
            print(f'''
            Дата: {datetime.datetime.today()}
            Пользователь {message.chat.first_name} решил добавить другое фото.
            ''')
            msg = BOT.send_message(message.chat.id, config.text_level_6, reply_markup= keyboard_hider)
            BOT.register_next_step_handler(msg, photo_handler)
        else:
            if message.text not in list(config.members.keys()):
                markup = types.ReplyKeyboardMarkup(one_time_keyboard = True, resize_keyboard = True, row_width = 2)
                for key in config.members.keys():
                    markup.add(key)
                markup.add('Назад', 'Далее', 'Выход')
                msg = BOT.send_message(message.chat.id, config.text_level_11, reply_markup= markup)
                BOT.register_next_step_handler(msg, _handler)
            else:
                task[message.chat.id]['assigne'].append({'gid':config.members[message.text], 'name': message.text, 'resource_type': 'user'})
                print(f'''
                Дата: {datetime.datetime.today()}
                Пользователь {message.chat.first_name} добавил
                фоловера {task[message.chat.id]['assigne']}
                ''')
                markup = types.ReplyKeyboardMarkup(one_time_keyboard = True, resize_keyboard = True, row_width = 2)
                markup.add('Добавить еще', 'Назад', 'Далее', 'Выход')
                msg = BOT.send_message(message.chat.id, config.text_level_10, reply_markup= markup)
                BOT.register_next_step_handler(msg, register_handler)
    except Exception as e:
        print('Ошибка!')
        msg = BOT.send_message(message.chat.id, config.text_level_0, reply_markup = keyboard_hider)
        BOT.register_next_step_handler(msg, start_handler)

def register_handler(message):
    try:
        if message.text == 'Добавить еще':
            print(f'''
            Дата: {datetime.datetime.today()}
            Пользователь {message.chat.first_name} решил добавить еще фоловера.
            ''')
            markup = types.ReplyKeyboardMarkup(one_time_keyboard = True, resize_keyboard = True, row_width = 2)
            for key in config.members.keys():
                markup.add(key)
            markup.add('Назад', 'Далее', 'Выход')
            msg = BOT.send_message(message.chat.id, config.text_level_10, reply_markup= markup)
            BOT.register_next_step_handler(msg, assigne_handler)
        elif message.text == 'Далее':
            print(f'''
            Дата: {datetime.datetime.today()}
            Пользователь {message.chat.first_name} закончил работу
            Заголовок {task[message.chat.id]['head']}
            Описание {task[message.chat.id]['desc']}
            Фото {task[message.chat.id]['photo']}
            Фоловеры {task[message.chat.id]['assigne']}
            ''')
            if task[message.chat.id]['assigne'] != []:
                CLIENT.tasks.create_in_workspace(
                    '719460696846217',
                    {'name': task[message.chat.id]['head'],
                     'notes': task[message.chat.id]['desc'],
                     'projects': '1154959099440115',
                     'followers':task[message.chat.id]['assigne']}
                )
            else:
                CLIENT.tasks.create_in_workspace(
                    '719460696846217',
                    {'name': task[message.chat.id]['head'],
                     'notes': task[message.chat.id]['desc'],
                     'projects': '1154959099440115'}
                )
            if len(task[message.chat.id]['photo']) > 0:
                for tasks in CLIENT.tasks.find_all({'project':'1154959099440115'}):
                    if tasks['name'] == task[message.chat.id]['head']:
                        CLIENT.attachments.create_on_task(
                            task_id= tasks['gid'],
                            file_content= open('D:/Python/BOT_ASANA/' + task[message.chat.id]['photo'], 'rb'),
                            file_name= task[message.chat.id]['photo'],
                            file_content_type= None
                        )
                        os.remove('D:/Python/BOT_ASANA/' + task[message.chat.id]['photo'])
            msg = BOT.send_message(message.chat.id, config.text_level_9, reply_markup= keyboard_hider)
            BOT.register_next_step_handler(msg, start_handler)
    except Exception as e:
        print('Ошибка!')
        msg = BOT.send_message(message.chat.id, config.text_level_0, reply_markup = keyboard_hider)
        BOT.register_next_step_handler(msg, start_handler)

def main():
    BOT.polling(none_stop=True, interval=0)


if __name__ == '__main__':
    main()
