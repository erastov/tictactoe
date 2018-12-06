# coding: utf-8
import time
import telepot
import telepot.helper
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.delegate import (
    per_chat_id, per_callback_query_origin, create_open, pave_event_space)
from core.utils import normilize, check, worst_child, search_node, best_child, check_end, middle_child
from core.generator import get_tree_db


ICONS = ['-', '⭕️', '❌']
MESSAGES = ['Ничья :|', ' Ты выиграл :(', 'Я выиграл :)']


class GameStarter(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(GameStarter, self).__init__(*args, **kwargs)

    def on_chat_message(self, msg):
        # content_type, chat_type, chat_id = telepot.glance(msg)
        self.sender.sendMessage(
            'Давай сыграем ...',
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[
                    InlineKeyboardButton(text='ИГРАТЬ', callback_data='start'),
                ]]
            )
        )
        self.close()


class Gamer(telepot.helper.CallbackQueryOriginHandler):

    _tree: dict = None
    _matrix: list = None
    _bot_node: int = None
    _human_node: int = None
    _changes: list = None
    _stop: bool = False
    _counter: int = 0
    _get_children: callable = None

    def __init__(self, *args, **kwargs):
        super(Gamer, self).__init__(*args, **kwargs)
        self._tree = get_tree_db()
        self._matrix = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self._bot_node = 0

    @property
    def _winner(self):
        return check_end(self._matrix)

    @property
    def _bot_children(self):
        return self._tree[self._bot_node]['children']

    @property
    def _has_human_children(self):
        return len(self._tree[self._human_node]['children']) != 0

    def _new_state(self, cell):
        i, j = [int(x) for x in cell]
        if self._matrix[i][j] == 0:
            self._matrix[i][j] = 1
            self._human_node, self._changes = search_node(self._tree, self._bot_children, self._matrix)
            return True
        else:
            return False

    def _bot_answer(self):
        if self._has_human_children:
            self._bot_node = self._get_children(self._tree, self._human_node)
            self._matrix = normilize(self._changes, self._tree[self._bot_node]['value'])
        else:
            self._stop = True

    def _show_menu(self):
        self.editor.editMessageText(
            'Выбери режим:',
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[
                    InlineKeyboardButton(text='Легко', callback_data='easy'),
                    InlineKeyboardButton(text='Нормально', callback_data='normal'),
                    InlineKeyboardButton(text='Тяжело ;)', callback_data='hard'),
                ]]
            )
        )

    def _show_next_state(self, message=None):
        winner = self._winner
        stop = self._stop
        if stop or winner:
            if winner:
                message = MESSAGES[winner]
            else:
                message = MESSAGES[0]
            self.editor.editMessageText(
                message,
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[[
                        InlineKeyboardButton(text='НАЧАТЬ НОВУЮ', callback_data='start'),
                    ]]
                )
            )
        else:
            self.editor.editMessageText(
                message,
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(text=ICONS[c], callback_data='{}{}'.format(i, j))
                            for j, c in enumerate(line)
                        ] for i, line in enumerate(self._matrix)
                    ]
                )
            )

    def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        if query_data == 'start':
            self._stop = False
            self._matrix = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
            self._bot_node = 0
            self._human_node = None
            self._changes = None
            self._show_menu()
        elif query_data == 'easy':
            self._get_children = worst_child
            self._show_next_state('Ты ходишь:')
        elif query_data == 'normal':
            self._get_children = middle_child
            self._show_next_state('Ты ходишь:')
        elif query_data == 'hard':
            self._get_children = best_child
            self._show_next_state('Ты ходишь:')
        else:
            ok = self._new_state(query_data)
            if ok:
                self._counter = 0
                self._show_next_state('Я хожу:')
                if not (self._stop or self._winner):
                    self._bot_answer()
                    self._show_next_state('Ты ходишь:')
            else:
                self._counter += 1
                self._show_next_state('Ты слепой? ({}):'.format(self._counter))

    def on__idle(self, event):
        self.editor.editMessageText(
            'Слишком долго думаешь :(\nЯ пошёл 👋',
            reply_markup=None)
        time.sleep(5)
        self.editor.deleteMessage()
        self.close()


if __name__ == "__main__":
    TOKEN = '705103229:AAF20n1fAtMQn-1Askb9BKwdKEGyylBG51U'

    bot = telepot.DelegatorBot(TOKEN, [
        pave_event_space()(
            per_chat_id(), create_open, GameStarter, timeout=3),
        pave_event_space()(
            per_callback_query_origin(), create_open, Gamer, timeout=10),
    ])

    MessageLoop(bot).run_as_thread()
    print('Listening ...')

    while 1:
        time.sleep(10)
