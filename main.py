import logging
import math
import os
import sys
from typing import List, Tuple

LOG_DIR = "Logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")


def setup_logging() -> None:
    """Настройка сквозного логирования: консоль + файл."""
    os.makedirs(LOG_DIR, exist_ok=True)

    log_format = "%(asctime)s | [%(levelname)-7s] | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=logging.DEBUG,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(LOG_FILE, encoding="utf-8")
        ]
    )

    # INFO — штатное событие запуска.
    logging.info("Логгер успешно сконфигурирован")
    logging.info("Приложение запущено")


def _parse_positive_float(value: str, name: str) -> float:
    """Преобразует строку в положительное float."""
    try:
        number = float(value)
    except ValueError as exc:
        # WARNING — ожидаемая ошибка валидации, без падения программы.
        logging.warning("Нечисловое значение %s='%s'", name, value)
        raise ValueError(f"Сторона {name} не является числом") from exc

    if number <= 0:
        # WARNING — число корректное, но недопустимое по условию.
        logging.warning("Недопустимое значение %s=%s (должно быть > 0)", name, number)
        raise ValueError(f"Сторона {name} должна быть > 0")

    # DEBUG — промежуточное состояние успешного разбора.
    logging.debug("Параметр %s успешно преобразован: %s", name, number)
    return number


def _triangle_type(a: float, b: float, c: float) -> str:
    """Определяет вид треугольника по трём сторонам."""
    if a + b <= c or a + c <= b or b + c <= a:
        return "не треугольник"
    if a == b == c:
        return "равносторонний"
    if a == b or a == c or b == c:
        return "равнобедренный"
    return "разносторонний"


def _calculate_vertices(a: float, b: float, c: float) -> List[Tuple[int, int]]:
    """
    Вычисляет координаты вершин для поля 100x100.
    Вершина C = (0,0), B = (a,0), A = (x,y).
    """
    # DEBUG — подробности расчёта.
    logging.debug("Расчёт координат для сторон A=%s, B=%s, C=%s", a, b, c)

    # Координаты до масштабирования.
    x = (b * b + a * a - c * c) / (2 * a)
    y = math.sqrt(max(0.0, b * b - x * x))

    raw_vertices = [(x, y), (a, 0.0), (0.0, 0.0)]

    # Масштабирование в поле 100x100.
    max_x = max(v[0] for v in raw_vertices)
    max_y = max(v[1] for v in raw_vertices)
    min_x = min(v[0] for v in raw_vertices)
    min_y = min(v[1] for v in raw_vertices)

    width = max_x - min_x
    height = max_y - min_y

    if width <= 0 or height <= 0:
        # WARNING — для валидного треугольника такой ситуации быть не должно.
        logging.warning("Нулевой размер треугольника: width=%s, height=%s", width, height)
        return [(-1, -1), (-1, -1), (-1, -1)]

    scale = min(100.0 / width, 100.0 / height)

    vertices: List[Tuple[int, int]] = []
    for vx, vy in raw_vertices:
        px = int(round((vx - min_x) * scale))
        py = int(round((vy - min_y) * scale))
        px = max(0, min(100, px))
        py = max(0, min(100, py))
        vertices.append((px, py))

    # DEBUG — итоговые координаты.
    logging.debug("Координаты вершин после масштабирования: %s", vertices)
    return vertices


def process_triangle(a_str: str, b_str: str, c_str: str) -> Tuple[str, List[Tuple[int, int]]]:
    """
    Основной метод Варианта 1.
    Возвращает: (тип треугольника, список координат вершин).
    """
    # INFO — фиксируем параметры запроса.
    logging.info("Запрос: A='%s', B='%s', C='%s'", a_str, b_str, c_str)

    # 1. Проверка на нечисловые данные.
    non_numeric = False
    for name, value in (("A", a_str), ("B", b_str), ("C", c_str)):
        try:
            float(value)
        except ValueError:
            non_numeric = True
            # ERROR — неуспешный запрос, нечисловые данные. exc_info=True добавляет traceback.
            logging.exception("Неуспешный запрос: сторона %s='%s' не является числом", name, value)

    if non_numeric:
        result_type = ""
        coords = [(-2, -2), (-2, -2), (-2, -2)]
        # ERROR — итог неуспешного запроса.
        logging.error("Итог неуспешного запроса: тип='%s', координаты=%s", result_type, coords)
        return result_type, coords

    # 2. Проверка на положительные числа.
    try:
        a = _parse_positive_float(a_str, "A")
        b = _parse_positive_float(b_str, "B")
        c = _parse_positive_float(c_str, "C")
    except ValueError:
        result_type = "не треугольник"
        coords = [(-1, -1), (-1, -1), (-1, -1)]
        # ERROR — числовые данные вне допустимого диапазона.
        logging.exception(
            "Неуспешный запрос: числовые данные <= 0. Итог: тип='%s', координаты=%s",
            result_type,
            coords
        )
        return result_type, coords

    # 3. Определение вида треугольника.
    tri_type = _triangle_type(a, b, c)

    if tri_type == "не треугольник":
        coords = [(-1, -1), (-1, -1), (-1, -1)]
        # WARNING — данные числовые, но треугольник не существует.
        logging.warning(
            "Запрос обработан: треугольник не существует. Тип='%s', координаты=%s",
            tri_type,
            coords
        )
        return tri_type, coords

    # 4. Расчёт координат.
    try:
        coords = _calculate_vertices(a, b, c)
    except Exception:
        # CRITICAL — непредвиденная ошибка расчёта, обязательно с traceback.
        logging.exception("Критическая ошибка при расчёте координат")
        return "не треугольник", [(-1, -1), (-1, -1), (-1, -1)]

    # INFO — успешный запрос: параметры и результат.
    logging.info(
        "Успешный запрос: A=%s, B=%s, C=%s | тип='%s' | координаты=%s",
        a, b, c, tri_type, coords
    )
    return tri_type, coords


def main() -> None:
    """Точка входа."""
    setup_logging()

    # DEBUG — подробность о начале ввода.
    logging.debug("Ожидание ввода трёх сторон треугольника")

    try:
        a_str = input("Введите сторону A: ")
        b_str = input("Введите сторону B: ")
        c_str = input("Введите сторону C: ")
    except EOFError:
        # ERROR — не удалось прочитать входные данные.
        logging.exception("Ошибка ввода: не удалось прочитать три строки")
        return

    result_type, vertices = process_triangle(a_str, b_str, c_str)

    print("Тип треугольника:", result_type)
    print("Координаты вершин:", vertices)

    # INFO — завершение работы.
    logging.info("Приложение завершило работу")


if __name__ == "__main__":
    main()