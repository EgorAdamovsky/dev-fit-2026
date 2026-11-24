import matplotlib
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Tuple

matplotlib.use('Agg')

PALETTE = [
    '#FFD700', '#00FFFF', '#FF00FF', '#39FF14', '#FF3131',
    '#00BFFF', '#FF7F50', '#9370DB', '#FFA500', '#00FA9A',
    '#FF69B4', '#1E90FF', '#FFFF00', '#FF1493', '#00FF7F',
    '#7B68EE', '#FF4500', '#48D1CC', '#DA70D6', '#ADFF2F'
]

BG_COLOR = '#14161F'
PLOT_BG = '#1A1D26'
TEXT_MAIN = '#E2E8F0'
TEXT_MUTED = '#94A3B8'
GRID_COLOR = '#334155'

# Организации команд — по организационной табличке
TEAM_ORIGINS = {
    'БРИКИ': 'ПГЭК',
    'ПРОДАМ ДРОВА': 'ПГЭК',
    'TECHDROTS': 'ФИТ',
    'ВАЙБ КОДЕРЫ': 'ФИТ',
    'ТАПАТЕЛИ ХОМЯКОВ': 'ФИТ',
    'BIBA&BOBA': 'ФКНЭ',
    'DEMOНЫ SMERTИ 4': 'ФИТ',
    'HELLOWORLD (PRINT)': 'ФИТ',
    'КБШНИКИ': 'ФКНЭ',
    'BARNIE': 'ФКНЭ',
    'ДЕНДРИТЫ': 'ФИТ',
}


def parse_results_file(filepath: str) -> Tuple[str, float, List[float]]:
    filename = Path(filepath).stem
    final_score = 0.0
    history = []
    in_history_section = False

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('Score:'):
                try:
                    final_score = float(line.split(':')[1].strip())
                except (ValueError, IndexError):
                    pass
            elif line == 'Quality History:':
                in_history_section = True
            elif in_history_section:
                try:
                    history.append(float(line))
                except ValueError:
                    in_history_section = False

    return filename, final_score, history


def plot_leaderboard(folder_path: str, output_image: str = 'RESULTS.png') -> None:
    path = Path(folder_path)
    if not path.is_dir():
        raise ValueError(f"указанный путь не является директорией: {folder_path}")

    results = []
    for file_path in path.glob('*.txt'):
        name, score, history = parse_results_file(str(file_path))
        if history:
            results.append((name, score, history))

    if not results:
        raise ValueError("в указанной папке не найдено файлов с корректными данными.")

    results.sort(key=lambda x: (-x[1], x[0]))

    # Плотная нумерация мест: одинаковый счёт -> одно и то же место (1, 1, 2, ...)
    places = []
    place = 0
    prev_score = None
    for _, score, _ in results:
        if prev_score is None or score != prev_score:
            place += 1
            prev_score = score
        places.append(place)

    # Команды с идентичной историей: линии лягут друг на друга,
    # поэтому рисуем их разными штрихами, чтобы обе были видны.
    history_groups = {}
    for name, score, history in results:
        key = tuple(round(v, 6) for v in history)
        history_groups.setdefault(key, []).append(name)

    dash_styles = ['-', (0, (9, 5)), (0, (2, 3)), (0, (14, 4, 3, 4))]

    fig, ax = plt.subplots(figsize=(14, 9.5), facecolor=BG_COLOR)
    ax.set_facecolor(PLOT_BG)

    legend_elements = []
    for idx, (name, score, history) in enumerate(results):
        x_axis = range(len(history))
        color = PALETTE[idx % len(PALETTE)]

        group = history_groups[tuple(round(v, 6) for v in history)]
        dup_pos = group.index(name)
        linestyle = dash_styles[dup_pos % len(dash_styles)]

        is_winner = places[idx] == 1
        line, = ax.plot(
            x_axis, history, color=color,
            linewidth=3.4 if is_winner else 2.4,
            alpha=0.95, zorder=3 + dup_pos * 0.1,
            linestyle=linestyle,
            solid_capstyle='butt', dash_capstyle='butt',
        )

        origin = TEAM_ORIGINS.get(name, '')
        label = f"{places[idx]}. {name}" + (f" ({origin})" if origin else "")
        legend_elements.append((line, label))

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(GRID_COLOR)
    ax.spines['left'].set_color(GRID_COLOR)
    ax.tick_params(colors=TEXT_MUTED, labelsize=15, width=1.4, length=7, pad=9)
    ax.grid(True, linestyle='--', alpha=0.3, color=GRID_COLOR, zorder=0)

    fig.suptitle('/dev/fit 2026',
                 fontsize=30, fontweight='bold', color=TEXT_MAIN, y=0.965)
    ax.set_xlabel('Шаг симуляции', fontsize=17, color=TEXT_MUTED, labelpad=14)
    ax.set_ylabel('Счёт', fontsize=17, color=TEXT_MUTED, labelpad=14)

    # Отступы от краёв, чтобы крайние точки не прилипали к рамке
    n = len(results[0][2])
    ax.set_xlim(-0.015 * n, 1.015 * n)
    top_score = max(history[-1] for _, _, history in results)
    ax.set_ylim(0, top_score * 1.07)

    lines = [elem[0] for elem in legend_elements]
    labels = [elem[1] for elem in legend_elements]

    # Легенда справа от графика, одним столбцом, растянутая по высоте графика
    fig.subplots_adjust(left=0.09, right=0.61, top=0.89, bottom=0.13)

    legend_fontsize = 15
    legend_kwargs = dict(
        loc='upper left', bbox_to_anchor=(1.035, 1.0), ncol=1,
        fontsize=legend_fontsize, framealpha=0.95, facecolor=PLOT_BG,
        edgecolor=GRID_COLOR, labelcolor=TEXT_MAIN,
        title="УЧАСТНИКИ", title_fontsize=18,
        borderpad=1.3, handlelength=2.8, handletextpad=0.9,
        borderaxespad=0.0,
    )

    leg = ax.legend(lines, labels, labelspacing=0.6, **legend_kwargs)
    plt.setp(leg.get_title(), color=TEXT_MAIN)

    # Подбираем межстрочный интервал так, чтобы легенда была ровно высотой с график
    fig.canvas.draw()
    ax_height = ax.get_window_extent().height
    row_step = max(1, len(labels) - 1) * legend_fontsize * fig.dpi / 72.0
    target_height = ax_height - 1.0

    spacing = 0.6
    for _ in range(6):
        leg = ax.legend(lines, labels, labelspacing=spacing, **legend_kwargs)
        plt.setp(leg.get_title(), color=TEXT_MAIN)
        fig.canvas.draw()
        legend_height = leg.get_window_extent().height
        if abs(legend_height - target_height) <= 1.5:
            break
        spacing = max(0.2, spacing + (target_height - legend_height) / row_step * 0.8)

    plt.savefig(output_image, dpi=300, bbox_inches='tight', pad_inches=0.35,
                facecolor=fig.get_facecolor())
    print(f"График успешно сохранен: {output_image}")


if __name__ == '__main__':
    TARGET_FOLDER = './players/test'
    try:
        plot_leaderboard(TARGET_FOLDER)
    except Exception as e:
        print(f"Ошибка при генерации графика: {e}")
