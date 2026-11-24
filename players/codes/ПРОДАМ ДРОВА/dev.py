from classes import *
import random

## ПАРАМЕТРЫ СИМУЛЯЦИИ (можно менять)
TEAM = "ПРОДАМ ДРОВА"
START_TIME = 7  # начало симуляции с 0 часа для финального теста
SPEED_MULT = 1  # будет установлен на 64х для финального теста
SEED = 42  # будет выбран случайно для финального теста
NUM_DAYS = 7  # 7 дней для финального теста
DENS = 0.3  # плотность трафика 0.3 для финального теста

## ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ (можете добавлять свои)
global_stops = 0  # пример глобальной переменной, количество остановок лифта
global_list = []
final_list = []

def my_way(elevator: Elevator):
    global global_stops
    global final_list
    # Переменный
    passes = elevator.get_passenger_destinations()  # список целевых этажей пассажиров, уже находящихся в лифте
    current_floor = elevator.get_current_floor()  # текущий этаж, на котором находится лифт
    capacity = elevator.get_capacity()  # вместимость лифта
    pass_num = elevator.get_passengers_count()  # текущее количество пассажиров в лифте

    # Посадка на текущем этаже
    boarded = 0
    waiting_current = elevator.get_waiting_people()  # список целевых этажей у ожидающих на текущем этаже

    # Актуализируем списки после высадки и посадки
    pass_num = elevator.get_passengers_count()  # обновляем количество пассажиров
    waiting_floors = elevator.get_waiting_floors()  # список всех этажей, где есть ожидающие пассажиры
    passes = elevator.get_passenger_destinations()  # список целевых этажей пассажиров, уже находящихся в лифте
    # вывод
    print(f"Нахожусь на {current_floor} этаже.")
    print(f"Загружен на {pass_num}/{capacity}.")
    print(f"Высадил {len([p for p in passes if p == current_floor])} чел.")
    print(f"Загружен на {pass_num}/{capacity} чел.")

    # ///////////////////////////
    elevator.unload_all()

    # Посадка на текущем этаже
    if waiting_current:  # если на этаже вообще кто-то есть
        while elevator.board_first_passenger():  # начать их посадку, пока это возможно
            boarded = boarded + 1
    if boarded > 0:
        print(f"Забрал {boarded} чел.")

    # 3. Выбираем следующий этаж для движения.
    if passes:  # если в лифте еще есть пассажиры
        if len(passes) > 0:
            final_list = sorted(passes)
        elevator.go_to_and_stop(final_list[0])  # выбираем случайного пассажира из списка и отправляем
        print(f"Еду на {passes[0]} этаж.")
    elif waiting_floors:  # если лифт пуст, но где-то есть вызовы
        if len(waiting_floors) > 0:
            final_list = sorted(waiting_floors)
        elevator.go_to_and_stop(final_list[0])  # выбираем случайный этаж с вызовом из списка и отправляем
        print(f"Еду на {waiting_floors[0]} этаж.")
    elif len(waiting_floors) <= 0 and len(passes) <= 0:
        elevator.go_to_and_stop(0)

    # остановка
    global_stops = global_stops + 1
    print(f"Всего остановок: {global_stops}.", "\n===")
    print(passes)
    print(waiting_floors)
    print(elevator)
    print(final_list)