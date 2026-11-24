from classes import *
import random

## ПАРАМЕТРЫ СИМУЛЯЦИИ (можно менять)
TEAM = "КБШНИКИ"
START_TIME = 8  # начало симуляции с 0 часа для финального теста
SPEED_MULT = 164  # будет установлен на 64х для финального теста
SEED = 42  # будет выбран случайно для финального теста
NUM_DAYS = 7  # 7 дней для финального теста
DENS = 0.3  # плотность трафика 0.3 для финального теста

## ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ (можете добавлять свои)
global_stops = 0  # пример глобальной переменной, количество остановок лифта


def my_way(elevator: Elevator):
    # высадить всех кто выходит на текущем этаже
    elevator.unload_all()
    # подобрать людей с этого этажа
    if elevator.get_waiting_people():
        # подбираем пассажиров
        while elevator.board_first_passenger():
            pass
    # список этажей где есть ожидающие
    waiting_floors = elevator.get_waiting_floors()
    # список этажей куда на нам надо и наш этаж
    current_floor = elevator.get_current_floor()
    passes = elevator.get_passenger_destinations()

    passengers = elevator.get_passengers_count()

    if passes:
        # едем на ближайший этаж
        state = 11
        for passenger in passes:
            num = abs(current_floor - passenger)
            if num < state:
                state = num
                floor = passenger



        elevator.go_to_and_stop(floor)


    elif waiting_floors:
        # едем на этаж где больше пассажиров
        max_pass = 0
        for waiting_floor in waiting_floors:
            peoples = len(elevator.get_waiting_people(waiting_floor))
            if peoples > max_pass:
                max_pass = peoples
                floor1 = waiting_floor
        elevator.go_to_and_stop(floor1)
