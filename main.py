import sys
from dev import *
from classes import *
from visual import *

FPS = 60
FIXED_DT = 1.0 / FPS
SIM_DAY_S = 24 * 3600
TIME_SCALE = 60.0
MAX_STEP_SIM = 0.5


def main():
    random.seed(dev.SEED)
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption("/dev/fit 2026 - " + TEAM)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    building = Building(11)
    generator = TrafficGenerator(density=dev.DENS)
    elevator = Elevator(building, capacity=8, speed=0.1)
    accumulator = 0.0
    sim_time_s = START_TIME * 3600
    running = True
    finished = False

    while running:
        frame_time = clock.tick(FPS) / 1000.0
        accumulator += frame_time
        while accumulator >= FIXED_DT:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                        dev.SPEED_MULT = min(dev.SPEED_MULT * 2, 64.0)
                    elif event.key == pygame.K_MINUS:
                        dev.SPEED_MULT = max(dev.SPEED_MULT / 2, 0.125)
                    elif event.key == pygame.K_RIGHTBRACKET:
                        generator.density = min(generator.density + 0.1, 3.0)
                    elif event.key == pygame.K_LEFTBRACKET:
                        generator.density = max(generator.density - 0.1, 0.1)

            dt_sim = FIXED_DT * TIME_SCALE * dev.SPEED_MULT
            max_time = NUM_DAYS * SIM_DAY_S
            if sim_time_s + dt_sim >= max_time:
                dt_sim = max_time - sim_time_s
                finished = True
            remaining_dt = dt_sim
            while remaining_dt > 0:
                step = min(remaining_dt, MAX_STEP_SIM)
                global_time = (sim_time_s % SIM_DAY_S) / SIM_DAY_S
                generator.update(step, building, global_time)
                for floor in building.floors:
                    for person in floor.queue:
                        person.wait_time += step
                elevator.update(step, sim_time_s)

                if elevator.get_state() == "IDLE":
                    my_way(elevator)

                remaining_dt -= step
                sim_time_s += step
            elevator.update_quality_history()
            if finished:
                elevator.finalize_simulation(building)
                running = False
                break
            accumulator -= FIXED_DT
        if not finished:
            current_day = int(sim_time_s // SIM_DAY_S) + 1
            global_time = (sim_time_s % SIM_DAY_S) / SIM_DAY_S
            draw_building(screen, building, elevator, global_time=global_time, speed_multiplier=dev.SPEED_MULT,
                          density=generator.density, current_day=current_day)
            pygame.display.flip()
    if finished:
        saved = False
        running_end = True
        while running_end:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running_end = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running_end = False
                    elif event.key == pygame.K_s:
                        save_results_to_file(
                            elevator.get_metrics(),
                            elevator.get_quality_history(),
                            filename="results.txt"
                        )
                        saved = True

            draw_end_screen(screen, elevator.get_metrics(),
                            elevator.get_quality_history(), font, saved)
            pygame.display.flip()
            pygame.time.delay(50)
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
