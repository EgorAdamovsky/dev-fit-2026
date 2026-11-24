from classes import *
import random

## ПАРАМЕТРЫ СИМУЛЯЦИИ (можно менять)
TEAM = "ДЕНДРИТЫ"
START_TIME = 0  # начало симуляции с 0 часа для финального теста
SPEED_MULT = 64 # будет установлен на 64х для финального теста
SEED = 67  # будет выбран случайно для финального теста
NUM_DAYS = 7 # 7 дней для финального теста
DENS = 0.3  # плотность трафика 0.3 для финального теста

## ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ (можете добавлять свои)
global_stops = 0  # пример глобальной переменной, количество остановок лифта


def my_way(elevator: Elevator):
    # e = elevator
    elevator.unload_all()
    if elevator.get_waiting_people():
        while elevator.board_first_passenger():
            pass
    waiting_floors = elevator.get_waiting_floors() # на какие этажи нужно за пассажирами
    passes = elevator.get_passenger_destinations() # куда нужно текущим пассажирам
    if passes:
        distances = [p - elevator.get_current_floor() for p in passes]
        elevator.go_to_and_stop(passes[distances.index(min(distances))])
    if waiting_floors:
        distances = [p - elevator.get_current_floor() for p in waiting_floors]
        elevator.go_to_and_stop(waiting_floors[distances.index(min(distances))])
    else:
        elevator.go_to_and_stop(elevator.get_building_floors() // 2 -1)