from aiogram.dispatcher.filters.state import State, StatesGroup


class AddDomain(StatesGroup):
    target_link = State()