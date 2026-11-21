import os
from classes import Elevator

TEAM = ""


def my_way(lift):
    os.system("echo test")
    f = open("log.txt", "w")
    secret_floor = lift.get_secret_floor()
    lift.move_up()
    print("Некорректный алгоритм!")
