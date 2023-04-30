import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import datetime
import deadline
import Messages
from dotenv import load_dotenv

load_dotenv()


class StatesGroups(StatesGroup):
    """Состояния для создания"""
    choosing_date = State()
    choosing_name = State()
    choosing_priority = State()
    choosing_difficult = State()
    """Состояния для изменения"""
    choosing_num_edit = State()
    choosing_edit = State()
    edit_time = State()
    edit_name = State()
    edit_priority = State()
    edit_difficult = State()
    """Состояния для удаления"""
    choosing_num_delete = State()
    """Состояния для сортировки"""
    choosing_sort = State()


logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

deadlines = dict()


def check_date(text: str):
    """Праверка даты на корректность"""
    try:
        lst = deadline.parser(text)
        date = datetime.datetime(lst[0], lst[1], lst[2], lst[3], lst[4])
    except:
        return Messages.invalid_date_format
    now = datetime.datetime.now()
    if date < now:
        return Messages.date_gone
    return ""


def check_number(input: str):
    """Праверка числа из приоритета и сложности на корректность"""
    try:
        number = int(input)
    except:
        return Messages.invalid_number_format
    if number > 10 or number < 1:
        return Messages.invalid_number_format
    return ""


def get_list_of_dl(usr_id):
    """Получение списка дедлайнов"""
    ans = ""
    for i in range(len(deadlines[usr_id])):
        dl = deadlines[usr_id][i]
        data = (
            str(dl.date)
            + " "
            + dl.name
            + "_"
            + str(dl.priority)
            + "_"
            + str(dl.difficult)
        )
        ans += str(i + 1) + ". " + data + "\n"
    return ans


@dp.message(Command("start"))
async def process_start_command(message: types.Message):
    await message.reply(Messages.start_message)


@dp.message(Command("help"))
async def process_help_command(message: types.Message):
    await message.reply(Messages.help_message)


@dp.message(Command("deletedeadline"))
async def process_delete_command(message: types.Message, state: FSMContext):
    """Удаление дедлайна. Вывод номеров для удаления"""
    usr_id = int(message.from_user.id)
    await message.answer(Messages.num_to_del)
    ans = get_list_of_dl(usr_id)
    await message.answer(ans)
    await state.set_state(StatesGroups.choosing_num_delete)


@dp.message(StatesGroups.choosing_num_delete)
async def input_num(message: types.Message, state: FSMContext):
    """Выбор номера дедлайна для удаления"""
    await state.clear()
    usr_id = int(message.from_user.id)
    try:
        deadlines[usr_id].pop(int(message.text) - 1)
    except:
        await message.answer(Messages.invalid_index)
        return
    await state.clear()
    await message.answer(Messages.successful_deletion)


@dp.message(Command("editdeadline"))
async def process_edit_command(message: types.Message, state: FSMContext):
    """Редактирование дедлайна. Вывод номеров для редактирования"""
    usr_id = int(message.from_user.id)
    await message.answer(Messages.num_to_edit)
    ans = get_list_of_dl(usr_id)
    await message.answer(ans)
    await state.set_state(StatesGroups.choosing_num_edit)


@dp.message(StatesGroups.choosing_num_edit)
async def input_num(message: types.Message, state: FSMContext):
    """Выбор номера дедлайна для редактирования"""
    usr_id = int(message.from_user.id)
    try:
        ind = int(message.text) - 1
        deadlines[usr_id][-1], deadlines[usr_id][ind] = (
            deadlines[usr_id][ind],
            deadlines[usr_id][-1],
        )
    except:
        await message.answer(Messages.invalid_index)
        return
    kb = [
        [types.KeyboardButton(text=Messages.time)],
        [types.KeyboardButton(text=Messages.name)],
        [types.KeyboardButton(text=Messages.priority)],
        [types.KeyboardButton(text=Messages.difficult)],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder=Messages.choose_parameter,
    )
    await message.answer(Messages.which_to_edit, reply_markup=keyboard)
    await state.set_state(StatesGroups.choosing_edit)


@dp.message(StatesGroups.choosing_edit)
async def edit_parameter(message: types.Message, state: FSMContext):
    """Изменение параметра. Установка состояния для редактируемого параметра"""
    if message.text == Messages.time:
        await state.set_state(StatesGroups.edit_time)
        await message.answer(
            Messages.deadline_date, reply_markup=types.ReplyKeyboardRemove()
        )
    if message.text == Messages.name:
        await state.set_state(StatesGroups.edit_name)
        await message.answer(
            Messages.input_name, reply_markup=types.ReplyKeyboardRemove()
        )
    if message.text == Messages.priority:
        await state.set_state(StatesGroups.edit_priority)
        await message.answer(
            Messages.deadline_priority, reply_markup=types.ReplyKeyboardRemove()
        )
    if message.text == Messages.difficult:
        await state.set_state(StatesGroups.edit_difficult)
        await message.answer(
            Messages.deadline_difficult, reply_markup=types.ReplyKeyboardRemove()
        )


@dp.message(StatesGroups.edit_time)
async def edit_date(message: types.Message, state: FSMContext):
    """Редактирование даты"""
    usr_id = int(message.from_user.id)
    if check_date(message.text) != "":
        await message.answer(check_date(message.text))
    else:
        lst = deadline.parser(message.text)
        date = datetime.datetime(lst[0], lst[1], lst[2], lst[3], lst[4])
        deadlines[usr_id][-1].date = date
        await message.answer(Messages.successful_edited)
        await state.clear()


@dp.message(StatesGroups.edit_name)
async def edit_name(message: types.Message, state: FSMContext):
    """Редактирование названия"""
    usr_id = int(message.from_user.id)
    deadlines[usr_id][-1].name = message.text
    await message.answer(Messages.successful_edited)
    await state.clear()


@dp.message(StatesGroups.edit_priority)
async def edit_priority(message: types.Message, state: FSMContext):
    """Редактирование приоритета"""
    usr_id = int(message.from_user.id)
    if check_number(message.text) != "":
        await message.answer(check_number(message.text))
        return
    else:
        deadlines[usr_id][-1].priority = int(message.text)
        await message.answer(Messages.successful_edited)
        await state.clear()


@dp.message(StatesGroups.edit_difficult)
async def edit_difficult(message: types.Message, state: FSMContext):
    """Редактирование сложности"""
    usr_id = int(message.from_user.id)
    if check_number(message.text) != "":
        await message.answer(check_number(message.text))
        return
    else:
        deadlines[usr_id][-1].difficult = int(message.text)
        await message.answer(Messages.successful_edited)
        await state.clear()


@dp.message(Command("newdeadline"))
async def create_new_dl(message: types.Message, state: FSMContext):
    """Создание нового дедлайна. Установка состояния выбора даты"""
    await state.set_state(StatesGroups.choosing_date)
    await message.answer(Messages.deadline_date)


@dp.message(StatesGroups.choosing_date)
async def input_date(message: types.Message, state: FSMContext):
    """Создание нового дедлайна. Установка состояния выбора названия"""
    usr_id = int(message.from_user.id)
    if check_date(message.text) != "":
        await message.answer(check_date(message.text))
    else:
        dl = deadline.Deadline(str(message.text), "test", 1, 1)
        if usr_id not in deadlines:
            deadlines[usr_id] = []
        deadlines[usr_id].append(dl)
        await state.set_state(StatesGroups.choosing_name)
        await message.answer(Messages.input_name)


@dp.message(StatesGroups.choosing_name)
async def input_name(message: types.Message, state: FSMContext):
    """Создание нового дедлайна. Установка состояния выбора приоритета"""
    usr_id = int(message.from_user.id)
    deadlines[usr_id][-1].name = message.text
    await state.set_state(StatesGroups.choosing_priority)
    await message.answer(Messages.deadline_priority)


@dp.message(StatesGroups.choosing_priority)
async def input_priority(message: types.Message, state: FSMContext):
    """Создание нового дедлайна. Установка состояния выбора сложности"""
    usr_id = int(message.from_user.id)
    if check_number(message.text) != "":
        await message.answer(check_number(message.text))
        return
    else:
        deadlines[usr_id][-1].priority = int(message.text)
        await state.set_state(StatesGroups.choosing_difficult)
        await message.answer(Messages.deadline_difficult)


@dp.message(StatesGroups.choosing_difficult)
async def input_difficult(message: types.Message, state: FSMContext):
    """Завершение создания. Вывод сообщения о новом дедлайне"""
    usr_id = int(message.from_user.id)
    dl = deadlines[usr_id][-1]
    if check_number(message.text) != "":
        await message.answer(check_number(message.text))
        return
    else:
        dl.difficult = int(message.text)
        await state.clear()
        await state.clear()
        await message.answer(
            Messages.created
            + str(dl.date)
            + "\nНазвание: "
            + dl.name
            + "\nПриоритет: "
            + str(dl.priority)
            + "\nСложность: "
            + str(dl.difficult)
        )


@dp.message(Command("deadlines"))
async def get_deadlines(message: types.Message, state: FSMContext):
    """Создание клавиатуры для выбора параметра сортировки"""
    kb = [
        [types.KeyboardButton(text=Messages.by_time)],
        [types.KeyboardButton(text=Messages.by_priority)],
        [types.KeyboardButton(text=Messages.by_difficult)],
        [types.KeyboardButton(text=Messages.unknown_formula)],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb, resize_keyboard=True, input_field_placeholder=Messages.choose_sort
    )
    await message.answer(Messages.which_to_sort, reply_markup=keyboard)
    await state.set_state(StatesGroups.choosing_sort)


@dp.message(StatesGroups.choosing_sort)
async def choose_sort(message: types.Message, state: FSMContext):
    """Сортировка дедлайна и их вывод на экран"""
    usr_id = int(message.from_user.id)
    new_dict = dict()
    ans = ""
    if len(deadlines[usr_id]) == 0:
        await message.answer(
            Messages.no_deadlines, reply_markup=types.ReplyKeyboardRemove()
        )
        await state.clear()
        return
    for i in range(len(deadlines[usr_id])):
        parameter = 0
        dl = deadlines[usr_id][i]
        if message.text == Messages.by_time:
            parameter = dl.hours_to_dl()
        if message.text == Messages.by_priority:
            parameter = 11 - dl.priority
        if message.text == Messages.by_difficult:
            parameter = dl.difficult
        if message.text == Messages.unknown_formula:
            parameter = dl.hours_to_dl() / (dl.difficult * dl.priority)
        if parameter not in new_dict:
            new_dict[parameter] = []
        new_dict[parameter].append(dl)
    sorted_new_dict = dict(sorted(new_dict.items()))
    i = 1
    for lst in sorted_new_dict:
        for dl in sorted_new_dict[lst]:
            hours = dl.hours_to_dl()
            data = (
                str(hours)
                + Messages.hours_to
                + dl.name
                + "_"
                + str(dl.priority)
                + "_"
                + str(dl.difficult)
            )
            ans += str(i) + ". " + data + "\n"
            i += 1
    await message.answer(ans, reply_markup=types.ReplyKeyboardRemove())
    await state.clear()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
