from math import floor

from classes import *
import random

TEAM = "ВАЙБКОДЕРЫ"
START_TIME = 0  # начало симуляции с 0 часа для финального теста
SPEED_MULT = 64  # будет установлен на 64х для финального теста
SEED = 42  # будет выбран случайно для финального теста
NUM_DAYS = 7  # 7 дней для финального теста
DENS = 0.3  # плотность трафика 0.3 для финального теста

def vector(elevator: Elevator, locations):    
    current_pos = elevator.get_current_floor()
    count_up = 0
    count_down = 0

    for i in range(len(locations)):
        if locations[i] < current_pos:
            count_down += 1
        else:
            count_up += 1

    is_up = count_up > count_down

    return is_up

def get_max(elevator: Elevator, locations):    
    max_pos = 0
    for i in range(len(locations)):
        if locations[i] > max_pos:
            max_pos = locations[i]
    return max_pos

def get_min(elevator: Elevator, locations):
    min_pos = elevator.get_building_floors()
    for i in range(len(locations)):
        if locations[i] < min_pos:
            min_pos = locations[i]
    return min_pos


def near_stop(elevator: Elevator, locations):
    if vector(elevator, locations):
        return get_min(elevator, locations)
    else:
        return get_max(elevator, locations) 


def my_way(elevator: Elevator):
    elevator.unload_all()
    if elevator.get_waiting_people():
        while elevator.board_first_passenger():
            pass
    waiting_floors = elevator.get_waiting_floors()
    passes = elevator.get_passenger_destinations()
    if passes or waiting_floors:
        if passes:
            elevator.go_to_and_stop(near_stop(elevator, passes))
        elif waiting_floors:
            elevator.go_to_and_stop(near_stop(elevator, waiting_floors))
    # else:
    #     current_pos = elevator.get_current_floor()
    #     midle_pos = floor(elevator.get_building_floors() / 2)
    #     if (current_pos != midle_pos):
    #         elevator.go_to_and_stop(midle_pos)
