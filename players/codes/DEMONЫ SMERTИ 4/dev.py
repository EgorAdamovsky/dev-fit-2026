from classes import *
import random

## ПАРАМЕТРЫ СИМУЛЯЦИИ (можно менять)
TEAM = "DEMONЫ SMERTИ 4"
START_TIME = 0  # начало симуляции с 0 часа для финального теста
SPEED_MULT = 100  # будет установлен на 64х для финального теста
SEED = 42  # будет выбран случайно для финального теста
NUM_DAYS = 7 # 7 дней для финального теста
DENS = 0.3  # плотность трафика 0.3 для финального теста

## ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ (можете добавлять свои)
global_stops = 0  # пример глобальной переменной, количество остановок лифта


max_people_floor = -1

N = 20
prev_floor = -1

need_to_clear = False
floor_needed_to_clear = -1


def find_priority_floor(passengers: list[int]) -> int:
    global max_people_floor
    tem_map: dict[int, int] = {}

    for floor in passengers:
        if tem_map.get(floor):
            tem_map[floor] += 1
        else:
            tem_map[floor] = 1

    max_floor = 0
    max_people_floor_loc = -1
    for floor, people_count in tem_map.items():
        if people_count > max_people_floor_loc:
            max_people_floor = floor
            max_floor = floor

    return max_floor

def my_way(elevator: Elevator):
    global max_people_floor
    global prev_floor
    global need_to_clear
    max_capacity = elevator.get_capacity()

    elevator.unload_all()

    if elevator.get_passengers_count() == 0:
        need_to_clear = False
    else:
        need_to_clear = True

    if elevator.get_waiting_people():
        while elevator.board_first_passenger():
            pass

    floors = elevator.get_waiting_floors()

    for floor in floors:
        if len(elevator.get_waiting_people(floor)) >= N:
            max_people_floor = floor

    if not need_to_clear and max_people_floor != -1:
        elevator.go_to_and_stop(max_people_floor)

    if max_people_floor != prev_floor and elevator.get_passengers_count() < max_capacity // 3 :
        elevator.go_to_and_stop(max_people_floor)
        prev_floor = max_people_floor
        max_people_floor = -1

    else:
        passes = elevator.get_passenger_destinations()
        if passes:
            max_floor = find_priority_floor(passes)

            prev_floor = max_floor
            elevator.go_to_and_stop(max_floor)

        elif floors:
            max_ = 0

            for floor in floors:
                if len(elevator.get_waiting_people(floor)) >= N:
                    max_ = floor

            if prev_floor == max_:
                find_pass = find_priority_floor(passes)


                elevator.go_to_and_stop(find_pass)
            else:

                prev_floor = max_
                if max_ == 0:
                    elevator.go_to_and_stop(find_priority_floor(elevator.get_waiting_floors()))
                elevator.go_to_and_stop(max_)


## Вариант демонстрационного my_way() без комментариев и лишних переменных
def my_way_clear(elevator: Elevator):
    global max_people_floor
    global prev_floor
    global need_to_clear
    max_capacity = elevator.get_capacity()

    elevator.unload_all()
    if elevator.get_waiting_people():
        while elevator.board_first_passenger():
            pass
    waiting_floors = elevator.get_waiting_floors()
    passes = elevator.get_passenger_destinations()
    if passes:
        passes = elevator.get_passenger_destinations()
        if passes:
            max_floor = find_priority_floor(passes)

            prev_floor = max_floor
            elevator.go_to_and_stop(max_floor)
    elif waiting_floors:
        max_ = 0

        for floor in waiting_floors:
            if len(elevator.get_waiting_people(floor)) >= N:
                max_ = floor

        if prev_floor == max_:
            find_pass = find_priority_floor(passes)

            elevator.go_to_and_stop(find_pass)
        else:

            prev_floor = max_
            if max_ == 0:
                elevator.go_to_and_stop(find_priority_floor(elevator.get_waiting_floors()))
            elevator.go_to_and_stop(max_)

