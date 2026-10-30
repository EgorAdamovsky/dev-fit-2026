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

    results.sort(key=lambda x: x[1], reverse=True)

    fig, ax = plt.subplots(figsize=(20, 12), facecolor=BG_COLOR)
    ax.set_facecolor(PLOT_BG)

    legend_elements = []
    for idx, (name, score, history) in enumerate(results):
        x_axis = range(len(history))
        color = PALETTE[idx % len(PALETTE)]

        if idx == 0:
            ax.plot(x_axis, history, color=f"{color}30", linewidth=10, zorder=2)
            line, = ax.plot(x_axis, history, color=color, linewidth=3.5, zorder=3)
            ax.scatter(x_axis[-1], history[-1], color=color, s=200, zorder=4, edgecolor=BG_COLOR, linewidth=3)
            legend_elements.append((line, f"{name} — {score:.1f} (Победитель)"))
        else:
            line, = ax.plot(x_axis, history, color=color, linewidth=2.5, alpha=0.9, zorder=1)
            legend_elements.append((line, f"{name} — {score:.1f}"))

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(GRID_COLOR)
    ax.spines['left'].set_color(GRID_COLOR)
    ax.tick_params(colors=TEXT_MUTED, labelsize=20, width=1.5, length=8)
    ax.grid(True, linestyle='--', alpha=0.3, color=GRID_COLOR, zorder=0)

    ax.set_title('Сравнительный анализ эффективности алгоритмов управления лифтом',
                 fontsize=34, fontweight='bold', color=TEXT_MAIN, pad=20, loc='center')
    ax.set_xlabel('Шаг симуляции (время)', fontsize=24, color=TEXT_MUTED, labelpad=20)
    ax.set_ylabel('Текущий счет (Score)', fontsize=24, color=TEXT_MUTED, labelpad=20)

    top3_text = "ТОП-3 РЕЗУЛЬТАТА:\n" + "\n".join([
        f"  1. {results[0][0]}: {results[0][1]:.1f}",
        f"  2. {results[1][0]}: {results[1][1]:.1f}" if len(results) > 1 else "",
        f"  3. {results[2][0]}: {results[2][1]:.1f}" if len(results) > 2 else ""
    ])

    ax.text(0.02, 0.95, top3_text, transform=ax.transAxes, fontsize=20,
            fontweight='bold', color=TEXT_MAIN,
            bbox=dict(boxstyle='round,pad=1.2', facecolor=PLOT_BG, edgecolor=PALETTE[0], alpha=0.95, linewidth=2),
            verticalalignment='top', zorder=5)

    lines = [elem[0] for elem in legend_elements]
    labels = [elem[1] for elem in legend_elements]

    # Легенда внутри графика справа, с полупрозрачным фоном
    leg = ax.legend(lines, labels, loc='center right', bbox_to_anchor=(0.98, 0.5),
                    fontsize=18, framealpha=0.95, facecolor=PLOT_BG, edgecolor=GRID_COLOR,
                    labelcolor=TEXT_MAIN, title="УЧАСТНИКИ", title_fontsize=22)

    plt.setp(leg.get_title(), color=TEXT_MAIN)

    # Убраны subplots_adjust и pad_inches - они создавали пустые поля
    plt.tight_layout()
    plt.savefig(output_image, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f"График успешно сохранен: {output_image}")


if __name__ == '__main__':
    TARGET_FOLDER = './players'
    try:
        plot_leaderboard(TARGET_FOLDER)
    except Exception as e:
        print(f"Ошибка при генерации графика: {e}")