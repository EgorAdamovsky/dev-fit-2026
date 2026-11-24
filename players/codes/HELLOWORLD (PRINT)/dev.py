from classes import *
import random
import math

## ПАРАМЕТРЫ СИМУЛЯЦИИ (можно менять)
TEAM = "HELLOWORLD (PRINT)"
START_TIME = 8  # начало симуляции с 0 часа для финального теста
SPEED_MULT = 64  # будет установлен на 64х для финального теста
SEED = 42  # будет выбран случайно для финального теста
NUM_DAYS = 7  # 7 дней для финального теста
DENS = 0.3  # плотность трафика 0.3 для финального теста

global_stops = 0

def get_max_wait(waiting_f, elevator):
    max = 0
    fl = 0
    for f in waiting_f:
        if len(elevator.get_waiting_people(f)) > max:
            max = len(elevator.get_waiting_people(f)) 
            fl = f
            print("MAX WAIT: ", waiting_f, len(elevator.get_waiting_people(f)), elevator.get_waiting_people(f))
    return fl

def get_nearest_floor(waiting_f, currect_f):
    print("WAITING F: ")
    r = 1000000000
    n = currect_f
    for f in waiting_f:
        if abs(currect_f - f) < r:
            r = abs(currect_f - f)
            n = f
    return [n, r]


def my_way(elevator: Elevator):
    global global_stops 

    call_stack = []

    passes = elevator.get_passenger_destinations()  
    current_floor = elevator.get_current_floor()  
    capacity = elevator.get_capacity() 
    pass_num = elevator.get_passengers_count() 
    print(f"Нахожусь на {current_floor} этаже.")
    print(f"Загружен на {pass_num}/{capacity}.")

    
    elevator.unload_all()  
    print(f"Высадил {len([p for p in passes if p == current_floor])} чел.")

   
    boarded = 0
    waiting_current = elevator.get_waiting_people() 
    if waiting_current:  
        while elevator.board_first_passenger():  
            boarded = boarded + 1
    if boarded > 0:
        print(f"Забрал {boarded} чел.")

    
    pass_num = elevator.get_passengers_count() 
    waiting_floors = elevator.get_waiting_floors() 
    passes = elevator.get_passenger_destinations() 
    print(f"Загружен на {pass_num}/{capacity} чел.")

   
    if passes:  
        current_floor = elevator.get_current_floor()
        
        if capacity > elevator.get_passengers_count():
            if get_nearest_floor(passes, current_floor)[1] < get_nearest_floor(waiting_floors, current_floor)[1]:
                target = get_nearest_floor(passes, current_floor)[0]
            else:
                target = get_nearest_floor(waiting_floors, current_floor)[0]
        target = get_nearest_floor(passes, current_floor)[0]
        elevator.go_to_and_stop(target) 
        print(f"Еду на {target} этаж.")
    elif waiting_floors:
        target = get_max_wait(waiting_floors, elevator) 
        elevator.go_to_and_stop(target) 
        print(f"MAX {get_max_wait(waiting_floors, elevator)} этаж.")

   
    global_stops = global_stops + 1
    print(f"Всего остановок: {global_stops}.", "\n===")


def my_way_clear(elevator: Elevator):
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
