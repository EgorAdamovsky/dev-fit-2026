from classes import *
import random

## ПАРАМЕТРЫ СИМУЛЯЦИИ (можно менять)
TEAM = "BARNIE"
START_TIME = 8  # начало симуляции с 0 часа для финального теста
SPEED_MULT = 100  # будет установлен на 64х для финального теста
SEED = 42  # будет выбран случайно для финального теста
NUM_DAYS = 7  # 7 дней для финального теста
DENS = 0.3  # плотность трафика 0.3 для финального теста

## ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ (можете добавлять свои)
global_stops = 0  # пример глобальной переменной, количество остановок лифта
nap = 1  # 1 - вверх, -1 - вниз


def my_way(elevator: Elevator):
    global global_stops, nap

    passes = elevator.get_passenger_destinations()  # список целевых этажей пассажиров, уже находящихся в лифте
    current_floor = elevator.get_current_floor()  # текущий этаж, на котором находится лифт
    capacity = elevator.get_capacity()  # вместимость лифта
    pass_num = elevator.get_passengers_count()  # текущее количество пассажиров в лифте
    print(f"Нахожусь на {current_floor} этаже.")
    print(f"Загружен на {pass_num}/{capacity}.")

    # 1. Высадка на текущем этаже
    elevator.unload_all()  # высаживаем всех, чья цель — текущий этаж
    print(f"Высадил {len([p for p in passes if p == current_floor])} чел.")

    # 2. Посадка на текущем этаже
    boarded = 0
    waiting_current = elevator.get_waiting_people()  # список целевых этажей у ожидающих на текущем этаже
    if waiting_current:  # если на этаже вообще кто-то есть
        while elevator.board_first_passenger():  # начать их посадку, пока это возможно
            boarded = boarded + 1
    if boarded > 0:
        print(f"Забрал {boarded} чел.")

    # Актуализируем списки после высадки и посадки
    pass_num = elevator.get_passengers_count()  # обновляем количество пассажиров
    waiting_floors = elevator.get_waiting_floors()  # список всех этажей, где есть ожидающие пассажиры
    passes = elevator.get_passenger_destinations()  # список целевых этажей пассажиров, уже находящихся в лифте
    print(f"Загружен на {pass_num}/{capacity} чел.")

    # 3. Выбор следующего этажа
    if passes:
        target = None
        while target is None:
            if nap > 0:
                above = [p for p in passes if p > current_floor]
                if above:
                    target = min(above)  # ближайший этаж сверху
                else:
                    nap = -1  # сверху никого нет, разворачиваемся вниз
            else:
                below = [p for p in passes if p < current_floor]
                if below:
                    target = max(below)  # ближайший этаж снизу
                else:
                    nap = 1  # снизу никого нет, разворачиваемся вверх
        elevator.go_to_and_stop(target)

    elif waiting_floors:
        maxx = max(waiting_floors)
        minn = min(waiting_floors)
        # if maxx < current_floor:
        #     nap = -1
        # else:
        #     nap = 1
        if current_floor > minn: 
            elevator.go_to_and_stop(maxx)
        else: 
            elevator.go_to_and_stop(minn)

    # После go_to_and_stop() лифт нас слушаться уже не будет до следующей остановки.
    global_stops = global_stops + 1
    print(f"Всего остановок: {global_stops}.", "\n===")
