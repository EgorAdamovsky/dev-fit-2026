from classes import *
import random

## ПАРАМЕТРЫ СИМУЛЯЦИИ
TEAM = "ЕНОТИКИ"
START_TIME = 0  # начало симуляции с 0 часа для финального теста
SPEED_MULT = 64  # будет установлен на 64х для финального теста
SEED = 42  # будет выбран случайно для финального теста
NUM_DAYS = 7  # 7 дней для финального теста
DENS = 0.3  # плотность трафика 0.3 для финального теста

def my_way(elevator: Elevator):
    elevator.unload_all()
    if elevator.get_waiting_people():
        while elevator.board_first_passenger():
            pass
    waiting_floors = elevator.get_waiting_floors()
    passes = elevator.get_passenger_destinations()
    if passes:
        elevator.go_to_and_stop(passes[random.randint(0, len(passes) - 1)])
    elif waiting_floors:
        elevator.go_to_and_stop(waiting_floors[random.randint(0, len(waiting_floors) - 1)])
