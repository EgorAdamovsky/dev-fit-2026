import math
from typing import List
import random
from collections import namedtuple


class Person:
    def __init__(self, destination):
        self.dest_floor = destination
        self.wait_time = 0.0
        self.boarding_time = 0.0
        self.ride_time = 0.0


class Floor:
    def __init__(self, n):
        self.number = n
        self.queue: List[Person] = []

    def get_number(self):
        return self.number


class Building:
    def __init__(self, n_floors):
        self.floors: List[Floor] = []
        for i in range(1, n_floors + 1):
            self.floors.append(Floor(i))

    def get_number_floors(self):
        return len(self.floors)


########################################################################################################################


def _poisson_events(lam):
    """Число событий за интервал. Работает корректно при любом lam."""
    if lam <= 0.0:
        return 0
    if lam < 30.0:
        # Алгоритм Кнута для малых lam
        limit = math.exp(-lam)
        p = 1.0
        k = 0
        while True:
            k += 1
            p *= random.random()
            if p <= limit:
                return k - 1
    else:
        # Нормальное приближение для больших lam
        return int(random.gauss(lam, math.sqrt(lam)))


class TrafficProfile:
    def __init__(self, rate_per_hour, start_hour=0.0, end_hour=24.0):
        self.rate_per_hour = rate_per_hour
        self.start_hour = start_hour
        self.end_hour = end_hour

    def active(self, hour):
        return self.start_hour <= hour < self.end_hour

    def spawn(self, building):
        raise NotImplementedError

    @staticmethod
    def _random_trip(building):
        idx = random.randrange(len(building.floors))
        origin = building.floors[idx].number
        dest = random.choice([f.number for f in building.floors if f.number != origin])
        return idx, dest


class ArrivalProfile(TrafficProfile):
    def spawn(self, building):
        dest = random.randrange(2, building.get_number_floors() + 1)
        return 0, [Person(dest)]


class DepartureProfile(TrafficProfile):
    def spawn(self, building):
        idx = random.randrange(1, len(building.floors))
        return idx, [Person(1)]


class InterfloorProfile(TrafficProfile):
    def spawn(self, building):
        idx, dest = self._random_trip(building)
        return idx, [Person(dest)]


class DelegationProfile(TrafficProfile):
    def __init__(self, rate_per_hour, start_hour, end_hour, min_size=2, max_size=5):
        super().__init__(rate_per_hour, start_hour, end_hour)
        self.min_size = min_size
        self.max_size = max_size

    def spawn(self, building):
        idx, dest = self._random_trip(building)
        size = random.randint(self.min_size, self.max_size)
        return idx, [Person(dest) for _ in range(size)]


class TrafficGenerator:
    def __init__(self, density=1.0):
        self.density = density
        self.profiles = [
            # Утро: сотрудники приезжают на работу с первого этажа
            ArrivalProfile(rate_per_hour=300, start_hour=7, end_hour=9),

            # Вечер: сотрудники уезжают домой на первый этаж
            DepartureProfile(rate_per_hour=300, start_hour=17, end_hour=19),

            # Рабочее время: перемещения между отделами на разных этажах
            InterfloorProfile(rate_per_hour=75, start_hour=8, end_hour=18),

            # Обед (первый час): уход в кафе на первый этаж
            DepartureProfile(rate_per_hour=100, start_hour=12, end_hour=13),

            # Обед (второй час): возвращение из кафе на рабочие места
            ArrivalProfile(rate_per_hour=100, start_hour=13, end_hour=14),

            # Рабочее время: групповые перемещения (совещания, делегации)
            DelegationProfile(rate_per_hour=20, start_hour=9, end_hour=17),

            # Ночь: смена охраны и техников
            InterfloorProfile(rate_per_hour=30, start_hour=19, end_hour=24),

            # Ночь: смена охраны и техников
            InterfloorProfile(rate_per_hour=30, start_hour=0, end_hour=7),
        ]

    def update(self, dt, building, global_time):
        if building.get_number_floors() < 2:
            return

        hour = (global_time % 1.0) * 24.0

        for profile in self.profiles:
            if not profile.active(hour):
                continue

            lam = profile.rate_per_hour * dt / 3600.0 * self.density
            for _ in range(_poisson_events(lam)):
                idx, people = profile.spawn(building)
                building.floors[idx].queue.extend(people)


########################################################################################################################


PassengerView = namedtuple('PassengerView', ['dest_floor', 'wait_time', 'index'])
CabinPassengerView = namedtuple('CabinPassengerView', ['dest_floor', 'wait_time'])


class Elevator:
    def __init__(self, building, capacity: int = 8, speed: float = 0.001):
        self._building = building
        self._capacity = capacity
        self._speed = speed

        self._current_floor = 1.0
        self._target_floor = 1
        self._start_floor = 1.0
        self._passengers = 0
        self._destinations: List = []

        self._state = "IDLE"
        self._door_timer = 0.0
        self._exited_people = []

        self._total_served = 0
        self._total_wait_time = 0.0
        self._total_ride_time = 0.0
        self._total_distance = 0.0
        self._quality_history = []

        self._sim_time = 0.0

    # ПУБЛИЧНЫЙ API — для использования в student_algorithm
    pass

    # Геттеры состояния

    def get_current_floor(self) -> int:
        return int(round(self._current_floor))

    def get_target_floor(self) -> int:
        return self._target_floor

    def get_passengers_count(self) -> int:
        return self._passengers

    def get_capacity(self) -> int:
        return self._capacity

    def get_building_floors(self) -> int:
        return self._building.get_number_floors()

    # Геттеры информации о пассажирах (immutable-снимки)

    def get_passenger_destinations(self) -> list:
        return [p.dest_floor for p in self._destinations]

    def get_destinations(self) -> list:
        return [CabinPassengerView(dest_floor=p.dest_floor, wait_time=p.wait_time)
                for p in self._destinations]

    def get_waiting_floors(self) -> list:
        return [f.get_number() for f in self._building.floors if len(f.queue) > 0]

    def get_waiting_people(self, floor: int = None) -> list:
        if floor is None:
            floor = self.get_current_floor()
        floor_obj = next((f for f in self._building.floors
                          if f.get_number() == floor), None)
        if not floor_obj:
            return []
        return [p.dest_floor for p in floor_obj.queue]

    # Действия

    def go_to_and_stop(self, floor: int):
        if self._state == "DOORS_OPEN":
            return
        if self._state == "MOVING":
            return
        if 1 <= floor <= self._building.get_number_floors():
            if floor != self.get_current_floor():
                self._start_floor = self._current_floor
                self._target_floor = floor
                self._state = "MOVING"

    def unload_all(self):
        if not self._is_docked():
            return

        floor_int = self.get_current_floor()
        unloaded = [p for p in self._destinations if p.dest_floor == floor_int]
        self._destinations = [p for p in self._destinations if p.dest_floor != floor_int]

        for person in unloaded:
            person.ride_time = self._sim_time - person.boarding_time
            self._total_wait_time += person.wait_time
            self._total_ride_time += person.ride_time
            self._total_served += 1
            self._passengers -= 1

        if len(unloaded) > 0:
            self._exited_people.append((floor_int, len(unloaded)))

    def board_first_passenger(self) -> bool:
        if not self._is_docked():
            return False
        if self._passengers >= self._capacity:
            return False
        floor_int = self.get_current_floor()
        floor_obj = next((f for f in self._building.floors
                          if f.get_number() == floor_int), None)
        if not floor_obj or len(floor_obj.queue) == 0:
            return False
        person = floor_obj.queue[0]
        person.boarding_time = self._sim_time
        self._destinations.append(person)
        self._passengers += 1
        floor_obj.queue.pop(0)
        return True

    # ВНУТРЕННИЙ API — для симуляции и визуализации, НЕ для студентов

    def get_state(self) -> str:
        return self._state

    def _is_docked(self) -> bool:
        if self._state not in ("IDLE", "DOORS_OPEN"):
            return False
        return abs(self._current_floor - round(self._current_floor)) < 1e-6

    def get_position(self) -> float:
        return self._current_floor

    def get_and_clear_exited(self) -> list:
        result = self._exited_people.copy()
        self._exited_people.clear()
        return result

    def get_metrics(self) -> dict:
        awt = self._total_wait_time / self._total_served if self._total_served > 0 else 0.0
        art = self._total_ride_time / self._total_served if self._total_served > 0 else 0.0
        quality = self.calculate_quality()

        return {
            "served": self._total_served,
            "awt": awt,
            "art": art,
            "distance": self._total_distance,
            "quality": quality
        }

    def get_quality_history(self) -> list:
        return self._quality_history.copy()

    def calculate_quality(self) -> float:
        if self._total_served == 0:
            return 0.0

        awt = self._total_wait_time / self._total_served
        art = self._total_ride_time / self._total_served
        total_dist = self._total_distance / self._total_served

        denominator = awt + 3.0 * art + 60.0 * total_dist
        if denominator == 0:
            return 10000.0

        return (self._total_served * 1000.0) / denominator

    def update_quality_history(self):
        self._quality_history.append(self.calculate_quality())

    def finalize_simulation(self, building):
        for floor in building.floors:
            for person in floor.queue:
                self._total_wait_time += person.wait_time
                self._total_served += 1
            floor.queue.clear()

        for person in self._destinations:
            person.ride_time = self._sim_time - person.boarding_time
            self._total_wait_time += person.wait_time
            self._total_ride_time += person.ride_time
            self._total_served += 1
        self._destinations.clear()
        self._passengers = 0

    def update(self, dt: float, sim_time: float):
        self._sim_time = sim_time

        if self._state == "MOVING":
            direction = 1 if self._target_floor > self._current_floor else -1
            step = self._speed * dt

            epsilon = 1e-5
            if direction == 1:
                next_int_floor = math.ceil(self._current_floor + epsilon)
            else:
                next_int_floor = math.floor(self._current_floor - epsilon)

            if (direction == 1 and self._current_floor + step >= next_int_floor) or \
                    (direction == -1 and self._current_floor - step <= next_int_floor):

                self._current_floor = float(next_int_floor)

                if next_int_floor == self._target_floor:
                    dist = abs(self._target_floor - self._start_floor)
                    self._total_distance += dist

                    self._state = "DOORS_OPEN"
                    self._door_timer = 30.0

            else:
                self._current_floor += step * direction

        elif self._state == "DOORS_OPEN":
            self._door_timer -= dt
            if self._door_timer <= 0.0:
                self._state = "IDLE"
