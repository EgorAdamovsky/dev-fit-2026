import pygame
import math

import dev
import main

WINDOW_W = 1100
WINDOW_H = 600
FLOOR_HEIGHT = 50
BUILDING_X = 100
BUILDING_W = 100
ELEVATOR_W = 60
ELEVATOR_H = FLOOR_HEIGHT - 10
MAX_WAIT_TIME = 3600.0
MAX_VISIBLE_QUEUE = 15

animating_exited = []


def floor_y(floor_number):
    return WINDOW_H - floor_number * FLOOR_HEIGHT


def _lerp_color(ratio):
    ratio = max(0.0, min(1.0, ratio))
    r = int(200 * ratio)
    g = int(200 * (1.0 - ratio))
    return r, g, 0


def _person_color(wait_time):
    ratio = min(wait_time / MAX_WAIT_TIME, 1.0)
    base = (220, 180, 80)
    return tuple(int(c * (1.0 - ratio)) for c in base)


def draw_metrics(screen, metrics, font, speed_multiplier, density):
    x, y = 720, 10
    color = (210, 215, 225)
    speed_color = (100, 200, 255)
    formula_color = (140, 150, 170)

    lines = [
        ("Обслужено (P):", f"{metrics['served']} чел."),
        ("Среднее T ожидания (AWT):", f"{metrics['awt']:.1f} с"),
        ("Среднее T поездки (ART):", f"{metrics['art']:.1f} с"),
        ("Пройдено этажей (L):", f"{metrics['distance']:.0f}"),
        ("Счет:", f"{metrics['quality']:.1f}"),
        ("", ""),
        ("Скорость ( - + ):", f"{speed_multiplier:.1f}x"),
        ("Трафик ( [ ] ):", f"{density:.1f}x"),
    ]

    for i, (label, value) in enumerate(lines):
        if label == "Качество:":
            if metrics['quality'] > 50:
                q_color = (100, 255, 100)
            elif metrics['quality'] > 0:
                q_color = (255, 255, 100)
            else:
                q_color = (255, 100, 100)
            text = font.render(f"{label} {value}", True, q_color)
        elif label in ("Скорость:", "Плотность:"):
            text = font.render(f"{label} {value}", True, speed_color)
        elif label:
            text = font.render(f"{label} {value}", True, color)
        else:
            continue
        screen.blit(text, (x, y + i * 25))

    formula_y = y + len(lines) * 25 + 10
    formula_lines = [
        "Формула оценки:",
        "Счет = (1000 х P) / (AWT + ART + L)",
        "+ больше людей за меньшее время",
        "- лишние или долгие поездки"
    ]
    for i, line in enumerate(formula_lines):
        text = font.render(line, True, formula_color)
        screen.blit(text, (x, formula_y + i * 20))


def draw_quality_graph(screen, elevator, font):
    graph_x = 720
    graph_y = 350
    graph_w = 280
    graph_h = 150

    pygame.draw.rect(screen, (35, 38, 48), (graph_x, graph_y, graph_w, graph_h), border_radius=4)
    pygame.draw.rect(screen, (75, 85, 105), (graph_x, graph_y, graph_w, graph_h), 1, border_radius=4)

    title = font.render("Счет:", True, (210, 215, 225))
    screen.blit(title, (graph_x + 5, graph_y - 20))
    history = elevator.get_quality_history()
    if len(history) < 2:
        return
    max_q = max(history)
    min_q = min(history)
    q_range = max_q - min_q
    if q_range < 1.0:
        q_range = 1.0
        min_q = max_q - 1.0

    axis_x = graph_x + graph_w + 5
    font_axis = pygame.font.SysFont(None, 16)

    max_text = font_axis.render(f"{max_q:.0f}", True, (100, 255, 100))
    screen.blit(max_text, (axis_x, graph_y))

    min_text = font_axis.render(f"{min_q:.0f}", True, (255, 100, 100))
    screen.blit(min_text, (axis_x, graph_y + graph_h - 15))

    mid_q = (max_q + min_q) / 2
    mid_text = font_axis.render(f"{mid_q:.0f}", True, (150, 150, 150))
    screen.blit(mid_text, (axis_x, graph_y + graph_h // 2 - 8))

    mid_y = graph_y + graph_h // 2
    for px in range(graph_x, graph_x + graph_w, 6):
        pygame.draw.rect(screen, (60, 65, 80), (px, mid_y, 3, 1))

    if len(history) > graph_w:
        step = len(history) // graph_w
        sampled = history[::step]
    else:
        sampled = history

    points = []
    for i, q in enumerate(sampled):
        px = graph_x + int(i * graph_w / max(len(sampled) - 1, 1))
        py = graph_y + graph_h - int((q - min_q) * graph_h / q_range)
        py = max(graph_y, min(graph_y + graph_h, py))
        points.append((px, py))

    if len(points) > 1:
        pygame.draw.lines(screen, (100, 255, 100), False, points, 2)


def draw_end_screen(screen, metrics, quality_history, font, saved=False):
    screen.fill((20, 22, 30))

    title_font = pygame.font.SysFont(None, 56)
    title = title_font.render("СИМУЛЯЦИЯ ЗАВЕРШЕНА", True, (255, 215, 0))
    screen.blit(title, (WINDOW_W // 2 - title.get_width() // 2, 15))

    metric_font = pygame.font.SysFont(None, 35)
    mx = 40
    my = 110

    metrics_lines = [
        (f"Обслужено (P): {metrics['served']} чел.", (210, 215, 225)),
        (f"Среднее t ожидания (AWT): {metrics['awt']:.1f} с", (210, 215, 225)),
        (f"Среднее t поездки (ART): {metrics['art']:.1f} с", (210, 215, 225)),
        (f"Пройдено этажей (L): {metrics['distance']:.0f}", (210, 215, 225)),
        (f"Итоговый счет: {metrics['quality']:.1f}", (255, 215, 0)),
    ]

    for i, (text, color) in enumerate(metrics_lines):
        surf = metric_font.render(text, True, color)
        screen.blit(surf, (mx, my + i * 40))

    # Название команды большими буквами
    team_font = pygame.font.SysFont(None, 100, bold=True)
    team_text = team_font.render(main.TEAM, True, (0, 255, 255))
    team_shadow = team_font.render(main.TEAM, True, (0, 100, 150))
    screen.blit(team_shadow, (mx + 3, my + 253))
    screen.blit(team_text, (mx, my + 250))

    gx = 520
    gy = 100
    gw = 480
    gh = WINDOW_H - gy - 110

    pygame.draw.rect(screen, (25, 28, 42), (gx, gy, gw, gh), border_radius=6)
    pygame.draw.rect(screen, (70, 75, 95), (gx, gy, gw, gh), 2, border_radius=6)

    graph_title = font.render("Динамика счета:", True, (210, 215, 225))
    screen.blit(graph_title, (gx + 15, gy - 30))

    if len(quality_history) > 1:
        max_q = max(quality_history)
        min_q = min(quality_history)
        q_range = max_q - min_q if max_q > min_q else 1.0

        padding = q_range * 0.15
        min_plot = min_q - padding
        max_plot = max_q + padding
        plot_range = max_plot - min_plot

        for i in range(5):
            ratio = i / 4.0
            y_pos = gy + gh - int(ratio * gh)
            val = min_plot + ratio * plot_range

            pygame.draw.line(screen, (45, 50, 65), (gx + 1, y_pos), (gx + gw - 1, y_pos), 1)

            val_text = font.render(f"{val:.0f}", True, (140, 145, 165))
            screen.blit(val_text, (gx + gw + 10, y_pos - 10))

        step = max(1, len(quality_history) // (gw - 20))
        sampled = quality_history[::step]

        points = []
        for i, q in enumerate(sampled):
            if len(sampled) > 1:
                px = gx + 10 + int(i * (gw - 20) / (len(sampled) - 1))
            else:
                px = gx + gw // 2
            py = gy + gh - 10 - int(((q - min_plot) / plot_range) * (gh - 20))
            py = max(gy + 10, min(gy + gh - 10, py))
            points.append((px, py))

        if len(points) > 1:
            pygame.draw.lines(screen, (80, 240, 80), False, points, 2)
            pygame.draw.circle(screen, (255, 215, 0), (int(points[-1][0]), int(points[-1][1])), 5)

    hint_y = WINDOW_H - 50

    esc_text = font.render("[ESC] ВЫХОД", True, (140, 145, 165))
    save_text = font.render("[S] СОХРАНИТЬ", True, (100, 220, 100) if not saved else (80, 120, 80))

    total_width = esc_text.get_width() + 40 + save_text.get_width()
    start_x = WINDOW_W // 2 - total_width // 2

    screen.blit(esc_text, (start_x, hint_y))
    screen.blit(save_text, (start_x + esc_text.get_width() + 40, hint_y))

    if saved:
        saved_msg = font.render("Сохранено в " + main.TEAM + ".txt", True, (100, 255, 100))
        screen.blit(saved_msg, (WINDOW_W // 2 - saved_msg.get_width() // 2, hint_y - 30))


def save_results_to_file(metrics, quality_history, filename="results.txt"):
    """Сохраняет метрики и историю качества в текстовый файл."""
    from datetime import datetime
    with open(dev.TEAM + ".txt", "w", encoding="utf-8") as f:
        f.write("# Hackathon Results\n")
        f.write(f"# Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# Seed: {dev.SEED}\n")
        f.write(f"# Days: {dev.NUM_DAYS}\n")
        f.write(f"# Density: {dev.DENS}\n\n")
        f.write("Metrics:\n")
        f.write(f"  Served (P): {metrics['served']}\n")
        f.write(f"  AWT: {metrics['awt']:.1f} s\n")
        f.write(f"  ART: {metrics['art']:.1f} s\n")
        f.write(f"  Distance (L): {metrics['distance']:.0f}\n")
        f.write(f"  Score: {metrics['quality']:.1f}\n\n")
        f.write("Quality History:\n")
        for q in quality_history:
            f.write(f"{q}\n")


def draw_building(screen, building, elevator, global_time=0.0, speed_multiplier=1.0, density=1.0, current_day=1):
    screen.fill((22, 24, 32))

    hour = int(global_time * 24)
    minute = int((global_time * 24 - hour) * 60)
    font = pygame.font.SysFont(None, 24)
    font_small = pygame.font.SysFont(None, 16)
    font_tiny = pygame.font.SysFont(None, 12)

    time_text = font.render(f"День {current_day} | {hour:02d}:{minute:02d}", True, (210, 215, 225))
    screen.blit(time_text, (20, 10))

    draw_metrics(screen, elevator.get_metrics(), font, speed_multiplier, density)
    draw_quality_graph(screen, elevator, font_small)
    draw_calls_list(screen, elevator, font_small)

    waiting_floors = elevator.get_waiting_floors()

    # Плавное синусоидальное мерцание
    pulse = (math.sin(pygame.time.get_ticks() * 0.006) + 1) / 2

    floor_platform_end = BUILDING_X + BUILDING_W + 20 + MAX_VISIBLE_QUEUE * 25 + 15

    for floor in building.floors:
        f_num = floor.get_number()
        y = floor_y(f_num)

        # Фоновая заливка офисного пространства этажа
        floor_bg = (32, 36, 48) if f_num % 2 == 0 else (28, 32, 42)
        pygame.draw.rect(screen, floor_bg, (BUILDING_X, y, BUILDING_W, FLOOR_HEIGHT))

        # Офисные крылья (перегородки)
        pygame.draw.rect(screen, (42, 48, 64), (BUILDING_X + 4, y + 8, 12, FLOOR_HEIGHT - 16), border_radius=2)
        pygame.draw.rect(screen, (42, 48, 64), (BUILDING_X + BUILDING_W - 16, y + 8, 12, FLOOR_HEIGHT - 16),
                         border_radius=2)
        pygame.draw.line(screen, (55, 62, 80), (BUILDING_X + 4, y + FLOOR_HEIGHT // 2),
                         (BUILDING_X + 16, y + FLOOR_HEIGHT // 2), 1)
        pygame.draw.line(screen, (55, 62, 80), (BUILDING_X + BUILDING_W - 16, y + FLOOR_HEIGHT // 2),
                         (BUILDING_X + BUILDING_W - 4, y + FLOOR_HEIGHT // 2), 1)

        # Шахта лифта
        shaft_x = BUILDING_X + 20
        shaft_w = BUILDING_W - 40
        pygame.draw.rect(screen, (22, 25, 33), (shaft_x, y, shaft_w, FLOOR_HEIGHT))

        # Плавное свечение вызванного этажа
        if f_num in waiting_floors:
            r = int(30 + (70 - 30) * pulse)
            g = int(40 + (150 - 40) * pulse)
            b = int(60 + (220 - 60) * pulse)
            pygame.draw.rect(screen, (r, g, b), (shaft_x + 2, y + 2, shaft_w - 4, FLOOR_HEIGHT - 4), border_radius=2)
            border_color = (int(100 + 155 * pulse), int(200 + 55 * pulse), 255)
        else:
            border_color = (50, 58, 76)

        # pygame.draw.rect(screen, border_color, (BUILDING_X, y, BUILDING_W, FLOOR_HEIGHT), 1)

        # Нижняя плита перекрытия (пол этажа)
        pygame.draw.line(screen, (75, 85, 110), (BUILDING_X, y + FLOOR_HEIGHT), (floor_platform_end, y + FLOOR_HEIGHT),
                         2)
        pygame.draw.line(screen, (15, 17, 22), (BUILDING_X, y + FLOOR_HEIGHT + 1),
                         (floor_platform_end, y + FLOOR_HEIGHT + 1), 1)

        # Линия потолка для самого верхнего этажа здания
        if f_num == max(f.get_number() for f in building.floors):
            pygame.draw.line(screen, (75, 85, 110), (BUILDING_X, y), (floor_platform_end, y), 2)

        # Текст этажа слева
        text = font.render(f"Этаж {f_num}", True, (210, 215, 225))
        screen.blit(text, (20, y + 15))

        queue_len = len(floor.queue)
        visible = min(queue_len, MAX_VISIBLE_QUEUE)

        # Очередь людей (по центру этажа по вертикали)
        for i in range(visible):
            person = floor.queue[i]
            px = BUILDING_X + BUILDING_W + 20 + i * 25
            py = y + FLOOR_HEIGHT // 2
            radius = 10

            p_color = _person_color(person.wait_time)
            pygame.draw.circle(screen, (15, 15, 20), (px + 1, py + 1), radius)
            pygame.draw.circle(screen, (p_color), (px, py), radius)
            pygame.draw.circle(screen, (50, 50, 50), (px, py), radius, 1)

            text_color = (255, 255, 255) if person.wait_time > MAX_WAIT_TIME / 2 else (30, 30, 30)
            dest_text = font_small.render(str(person.dest_floor), True, text_color)
            text_rect = dest_text.get_rect(center=(px, py))
            screen.blit(dest_text, text_rect)

        if queue_len > 0:
            queue_text = font.render(f"{queue_len} чел.", True, (255, 120, 120))
            text_rect = queue_text.get_rect(center=(
                BUILDING_X + BUILDING_W + 20 + MAX_VISIBLE_QUEUE * 25 + 35,
                y + FLOOR_HEIGHT // 2
            ))
            screen.blit(queue_text, text_rect)

    ey = floor_y(elevator.get_position()) + 5
    ex = BUILDING_X + (BUILDING_W - ELEVATOR_W) // 2
    lift_cx = ex + ELEVATOR_W // 2
    lift_cy = ey + ELEVATOR_H // 2

    # Исправление бага со стрелкой направления в последнем кадре
    if elevator.get_state() == "MOVING":
        current_floor_val = elevator.get_current_floor()
        target_floor_val = elevator.get_target_floor()

        # Рисуем стрелку только если лифт еще не доехал до целевого этажа
        if abs(elevator.get_position() - target_floor_val) > 0.01:
            target_y = floor_y(target_floor_val) + FLOOR_HEIGHT // 2
            pygame.draw.line(screen, (255, 255, 100), (lift_cx, lift_cy), (lift_cx, target_y), 2)
            if target_floor_val > elevator.get_position():
                pygame.draw.polygon(screen, (255, 255, 100),
                                    [(lift_cx, target_y), (lift_cx - 6, target_y + 10), (lift_cx + 6, target_y + 10)])
            else:
                pygame.draw.polygon(screen, (255, 255, 100),
                                    [(lift_cx, target_y), (lift_cx - 6, target_y - 10), (lift_cx + 6, target_y - 10)])

    # Кабина лифта
    ratio = elevator.get_passengers_count() / elevator.get_capacity() if elevator.get_capacity() > 0 else 0
    lift_color = _lerp_color(ratio)
    if elevator.get_state() == "DOORS_OPEN":
        lift_color = tuple(min(c + 40, 255) for c in lift_color)

    pygame.draw.rect(screen, lift_color, (ex, ey, ELEVATOR_W, ELEVATOR_H), border_radius=4)
    pygame.draw.rect(screen, (200, 210, 220), (ex, ey, ELEVATOR_W, ELEVATOR_H), 1, border_radius=4)

    # Пассажиры внутри лифта
    cols = 4
    for i, person in enumerate(elevator.get_destinations()):
        col = i % cols
        row = i // cols
        px = ex + 10 + col * 14
        py = ey + 12 + row * 16

        pygame.draw.circle(screen, (220, 180, 80), (px, py), 7)
        dest_text = font_tiny.render(str(person.dest_floor), True, (30, 30, 30))
        text_rect = dest_text.get_rect(center=(px, py))
        screen.blit(dest_text, text_rect)

    global animating_exited
    for floor_num, count in elevator.get_and_clear_exited():
        y = floor_y(floor_num)
        for i in range(count):
            animating_exited.append({
                'x': BUILDING_X + BUILDING_W // 2,
                'y': y + FLOOR_HEIGHT // 2 + i * 3,
                'alpha': 255,
                'dx': -2
            })

    for person in animating_exited[:]:
        color = (220, 180, 80, int(person['alpha']))
        surf = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (6, 6), 6)
        screen.blit(surf, (int(person['x']), int(person['y'])))
        person['x'] += person['dx']
        person['alpha'] -= 5
        if person['x'] < 0 or person['alpha'] <= 0:
            animating_exited.remove(person)


def draw_calls_list(screen, elevator, font):
    x = 720
    y = 520

    waiting = elevator.get_waiting_floors()
    if waiting:
        waiting_str = ", ".join(map(str, sorted(waiting)))
    else:
        waiting_str = "нет"
    calls_text = font.render(f"Вызовы: {waiting_str}", True, (100, 200, 255))
    screen.blit(calls_text, (x, y))

    y += 15
    passes = elevator.get_destinations()
    if passes:
        dests = [p.dest_floor for p in passes]
    else:
        dests = []
    dests_str = ", ".join(map(str, dests)) if dests else "пусто"
    dest_text = font.render(f"Пассажиры ({len(passes)}/{elevator.get_capacity()}): {dests_str}", True, (255, 200, 100))
    screen.blit(dest_text, (x, y))

    y += 15
    now_state = elevator.get_state()
    state_text = font.render(f"Статус: {now_state}", True, (210, 215, 225))
    screen.blit(state_text, (x, y))

    y += 15
    now_pos = elevator.get_current_floor()
    goal_pos = elevator.get_target_floor()
    pos_text = font.render(f"Этаж: {now_pos} -> {goal_pos}", True, (210, 215, 225))
    screen.blit(pos_text, (x, y))
