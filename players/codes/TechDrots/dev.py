from classes import *
import random

## ПАРАМЕТРЫ СИМУЛЯЦИИ (можно менять)
TEAM = "TECHDROTS"
START_TIME = 8 # начало симуляции с 0 часа для финального теста
SPEED_MULT = 1  # будет установлен на 64х для финального теста
SEED = 42  # будет выбран случайно для финального теста
NUM_DAYS = 1  # 7 дней для финального теста
DENS = 0.3  # плотность трафика 0.3 для финального теста

## ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ (можете добавлять свои)
global_stops = 0  # пример глобальной переменной, количество остановок лифта


def my_way(elevator: Elevator):
    # Ждем пассажиров
    while len(elevator.get_waiting_floors()) == 0:
        pass

    waiting_floors = elevator.get_waiting_floors()
    max_people = len(elevator.get_waiting_people(0))
    max_p_floor = 1

    # Ищем этаж с наибольшим количеством людей на нем
    for floor in waiting_floors:
        people_count = len(elevator.get_waiting_people(floor))
        if people_count > max_people:
            max_people = people_count
            max_p_floor = floor

    # Едем на этаж с максимальным кол-вом ожидающих
    elevator.go_to_and_stop(max_p_floor)
    elevator.unload_all()
    while elevator.board_first_passenger():
        pass

    # Обновляем цели пассажиров в лифте и получаем текущий этаж
    passes = elevator.get_passenger_destinations()
    current_floor = elevator.get_current_floor()

    if len(passes) != 0:
        min_dist_floor = abs(passes[0] - current_floor)
        floor_m = 1
        for passs in passes:
            dist_floor = abs(passs - current_floor)
            if(dist_floor < min_dist_floor):
                min_dist_floor = dist_floor
                floor_m = passs

        elevator.go_to_and_stop(floor_m)
        elevator.unload_all()
        while elevator.board_first_passenger():
            pass