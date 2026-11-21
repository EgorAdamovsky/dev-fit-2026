import ast
import re
import sys


# ANSI escape коды для цветного вывода
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


API_METHODS = {
    'get_current_floor', 'get_target_floor', 'get_passengers_count',
    'get_capacity', 'get_building_floors', 'get_passenger_destinations',
    'get_waiting_floors', 'get_waiting_people', 'go_to_and_stop',
    'unload_all', 'board_first_passenger'
}

DANGEROUS_PATTERNS = [
    (r'\bopen\s*\(', 'вызов open() (работа с файловой системой)'),
    (r'\bexec\s*\(', 'вызов exec()'),
    (r'\beval\s*\(', 'вызов eval()'),
    (r'\b__import__\s*\(', 'вызов __import__()'),
    (r'\b(subprocess|os|sys)\s*\.', 'обращение к модулям subprocess/os/sys'),
]


def check(filepath='dev.py'):
    results = []  # список кортежей: (passed: bool, message: str, critical: bool)

    def add(passed, msg, critical=True):
        results.append((passed, msg, critical))

    # 1. Чтение файла
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        add(True, f'файл {filepath} найден и прочитан')
    except FileNotFoundError:
        add(False, f'файл {filepath} не найден')
        return results
    except Exception as e:
        add(False, f'не удалось прочитать файл: {e}')
        return results

    # 2. Синтаксический разбор
    try:
        tree = ast.parse(source)
        add(True, 'синтаксис python корректен')
    except SyntaxError as e:
        add(False, f'синтаксическая ошибка: {e}')
        return results

    # 3. Переменная TEAM
    team_found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == 'TEAM':
                    team_found = True
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        if node.value.value.strip():
                            add(True, f'переменная TEAM определена: "{node.value.value}"')
                        else:
                            add(False, 'переменная TEAM не должна быть пустой строкой')
                    else:
                        add(False, 'переменная TEAM должна быть строковой константой')
    if not team_found:
        add(False, 'переменная TEAM не найдена')

    # 4. Функция my_way и её сигнатура
    my_way_node = None
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef) and node.name == 'my_way':
            my_way_node = node
            break

    if my_way_node is None:
        add(False, 'функция my_way не найдена')
        return results
    add(True, 'функция my_way определена')

    # 4.1. Сигнатура
    args = my_way_node.args.args
    if len(args) == 1 and args[0].arg == 'elevator':
        ann = args[0].annotation
        if isinstance(ann, ast.Name) and ann.id == 'Elevator':
            add(True, 'сигнатура my_way(elevator: Elevator) корректна')
        else:
            add(False, 'аргумент elevator должен иметь аннотацию типа Elevator')
    else:
        add(False, 'функция my_way должна принимать ровно один аргумент elevator')

    # 5. Использование методов API
    used_methods = set()
    forbidden_methods = set()
    for node in ast.walk(my_way_node):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            name = node.func.attr
            if name.startswith(('get_', 'go_', 'unload', 'board')):
                used_methods.add(name)
                if name not in API_METHODS:
                    forbidden_methods.add(name)

    if forbidden_methods:
        add(False, f'используются неразрешённые методы API: {", ".join(sorted(forbidden_methods))}')
    else:
        if used_methods:
            add(True, f'все используемые методы входят в API: {", ".join(sorted(used_methods))}')
        else:
            add(False, 'не обнаружено вызовов методов API лифта')

    # 6. Вызов go_to_and_stop
    has_go_to = any(
        isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'go_to_and_stop'
        for n in ast.walk(my_way_node)
    )
    if has_go_to:
        add(True, 'присутствует вызов go_to_and_stop()')
    else:
        add(False, 'отсутствует вызов go_to_and_stop() — лифт не будет перемещаться')

    # 7. Запрещённые конструкции
    dangerous_found = []
    for pattern, desc in DANGEROUS_PATTERNS:
        if re.search(pattern, source):
            dangerous_found.append(desc)
    if dangerous_found:
        add(False, f'обнаружены запрещённые конструкции: {"; ".join(dangerous_found)}')
    else:
        add(True, 'запрещённые конструкции (open/exec/eval/os/sys/subprocess) отсутствуют')

    # 8. Наличие вызова unload_all и board_first_passenger (эвристика)
    has_unload = any(
        isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'unload_all'
        for n in ast.walk(my_way_node)
    )
    has_board = any(
        isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'board_first_passenger'
        for n in ast.walk(my_way_node)
    )
    if has_unload:
        add(True, 'присутствует вызов unload_all()')
    else:
        add(False, 'отсутствует вызов unload_all() — пассажиры не будут высаживаться', critical=False)
    if has_board:
        add(True, 'присутствует вызов board_first_passenger()')
    else:
        add(False, 'отсутствует вызов board_first_passenger() — пассажиры не будут сажаться', critical=False)

    return results


def print_report(results):
    print(f'\n{Colors.BOLD}{Colors.CYAN}ОТЧЁТ ПРОВЕРКИ{Colors.RESET}\n')
    for passed, msg, critical in results:
        mark = f'{Colors.GREEN}✓{Colors.RESET}' if passed else f'{Colors.RED}✗{Colors.RESET}'
        severity = '' if critical else f' {Colors.YELLOW}[некритично]{Colors.RESET}'
        print(f'  {mark}  {msg}{severity}')

    failed_critical = [r for r in results if not r[0] and r[2]]
    failed_noncritical = [r for r in results if not r[0] and not r[2]]

    print(f'\n{Colors.BOLD}ИТОГ:{Colors.RESET} ', end='')
    if not failed_critical and not failed_noncritical:
        print(f'{Colors.GREEN}{Colors.BOLD}все проверки пройдены{Colors.RESET}')
    elif not failed_critical:
        print(f'{Colors.YELLOW}{Colors.BOLD}критических ошибок нет, есть замечания{Colors.RESET}')
    else:
        print(f'{Colors.RED}{Colors.BOLD}обнаружены критические ошибки ({len(failed_critical)}){Colors.RESET}')


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'dev.py'
    results = check(path)
    print_report(results)
