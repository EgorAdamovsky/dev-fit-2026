from classes import *
import random

## ПАРАМЕТРЫ СИМУЛЯЦИИ (можно менять)
TEAM = "ЕНОТИКИ"
START_TIME = 0  # начало симуляции с 0 часа для финального теста
SPEED_MULT = 1  # будет установлен на 64х для финального теста
SEED = 42  # будет выбран случайно для финального теста
NUM_DAYS = 7  # 7 дней для финального теста
DENS = 0.3  # плотность трафика 0.3 для финального теста

## ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ (можете добавлять свои)
global_stops = 0  # пример глобальной переменной, количество остановок лифта


def my_way(elevator: Elevator):
    global global_stops

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

    # 3. Выбираем следующий этаж для движения.
    if passes:  # если в лифте еще есть пассажиры
        target = passes[random.randint(0, len(passes) - 1)]  # выбираем случайного пассажира из списка
        elevator.go_to_and_stop(target)  # отправляем лифт на целевой этаж этого пассажира
        print(f"Еду на {target} этаж.")
    elif waiting_floors:  # если лифт пуст, но где-то есть вызовы
        target = waiting_floors[random.randint(0, len(waiting_floors) - 1)]  # выбираем случайный этаж с вызовом
        elevator.go_to_and_stop(target)  # отправляем лифт на выбранный этаж
        print(f"Еду на {target} этаж.")

    # После go_to_and_stop() лифт нас слушаться уже не будет до следующей остановки.
    global_stops = global_stops + 1
    print(f"Всего остановок: {global_stops}.", "\n===")


## Вариант демонстрационного my_way() без комментариев и лишних переменных
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
