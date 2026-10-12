from random import randrange

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
GRID_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Константа допустимых переходов
ALLOWED_MOVES = {
    (UP, pygame.K_UP): UP,
    (UP, pygame.K_LEFT): LEFT,
    (UP, pygame.K_RIGHT): RIGHT,

    (DOWN, pygame.K_DOWN): DOWN,
    (DOWN, pygame.K_LEFT): LEFT,
    (DOWN, pygame.K_RIGHT): RIGHT,

    (LEFT, pygame.K_LEFT): LEFT,
    (LEFT, pygame.K_UP): UP,
    (LEFT, pygame.K_DOWN): DOWN,

    (RIGHT, pygame.K_RIGHT): RIGHT,
    (RIGHT, pygame.K_UP): UP,
    (RIGHT, pygame.K_DOWN): DOWN,
}

# Цвет фона:
BOARD_BACKGROUND_COLOR = (200, 200, 200)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (0, 128, 0)

# Цвет змейки
SNAKE_COLOR = (255, 0, 0)

# Скорость движения змейки:
SPEED = 10

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов.
    Содержит общие атрибуты позиции и цвета тела и абстрактный метод отрисовки.
    """

    def __init__(self, position=GRID_CENTER, body_color=APPLE_COLOR):
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Отрисовывает объект на экране.
        Метод должен быть переопределён в дочерних классах.
        """


class Apple(GameObject):
    """Класс, представляющий яблоко в игре.
    Отвечает за генерацию позиции яблока в пределах игрового поля
    и его отрисовку.
    """

    def __init__(self, body_color=APPLE_COLOR, locked_positions=[]):
        super().__init__((0, 0), body_color)
        self.randomize_position()
        if locked_positions is None or len(locked_positions) == 0:
            return

        while self.position in locked_positions:
            self.randomize_position()

    def randomize_position(self):
        """Генерирует случайную позицию яблока.
        Позиция выбирается так, чтобы совпадать с центром ячейки сетки.
        """
        self.position = (randrange(0, GRID_WIDTH) * GRID_SIZE,
                         randrange(0, GRID_HEIGHT) * GRID_SIZE)

    def draw(self):
        """Отрисовывает яблоко.
        Центр круга соответствует центру ячейки, радиус равен половине ячейки.
        """
        x, y = self.position
        pygame.draw.circle(screen,
                           self.body_color,
                           (x + GRID_SIZE // 2,
                            y + GRID_SIZE // 2),
                           GRID_SIZE // 2)


class Snake(GameObject):
    """Класс, реализующий логику и отрисовку змейки.
    Управляет движением, направлением, длиной змейки, а также
    обработкой столкновений с собственным хвостом и сбросом
    состояния при проигрыше.
    """

    def __init__(self, body_color=SNAKE_COLOR):
        super().__init__(GRID_CENTER, body_color)
        self.body_color = body_color
        self.reset()

    def draw(self):
        """Отрисовывает змейку на экране.
        Каждый сегмент рисуется как квадрат с цветной заливкой и обводкой.
        """
        for position in self.positions:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def move(self):
        """Обновляет позицию змейки согласно текущему направлению.
        Реализует механику прохождения сквозь границы экрана.
        Добавляет новую голову в начало списка.
        Удаляет хвост, если длина не увеличилась.
        """
        self.update_direction()

        head_x, head_y = self.positions[0]
        dir_x, dir_y = self.direction
        new_head = ((head_x + dir_x * GRID_SIZE) % SCREEN_WIDTH,
                    (head_y + dir_y * GRID_SIZE) % SCREEN_HEIGHT)

        self.positions.insert(0, new_head)

        if self.length + 1 == len(self.positions):
            self.positions.pop()

    def update_direction(self):
        """Применяет запланированное направление движения.
        Используется для предотвращения смены направления на противоположное
        """
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def get_head_position(self):
        """Возвращает текущую позицию головы змейки."""
        return self.positions[0]

    def reset(self):
        """Сбрасывает состояние змейки к начальному."""
        self.length = 1
        self.positions = [GRID_CENTER]
        self.direction = RIGHT
        self.next_direction = None


def handle_keys(game_object):
    """Обрабатывает события клавиатуры для управления змейкой.
    Также обрабатывает событие закрытия окна.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if event.type == pygame.KEYDOWN:
            new_dir = ALLOWED_MOVES.get((game_object.direction, event.key))
            if new_dir is not None:
                game_object.next_direction = new_dir


def main():
    """Основная функция.
    Инициализирует объекты игры, запускает игровой цикл,
    обрабатывает столкновения, увеличение длины змейки и сброс при проигрыше.
    """
    pygame.init()

    snake = Snake(SNAKE_COLOR)
    apple = Apple(APPLE_COLOR, snake.positions)

    while True:
        handle_keys(snake)
        screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw()
        snake.draw()
        snake.move()
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position()
            while apple.position in snake.positions:
                apple.randomize_position()
        elif snake.get_head_position() in snake.positions[1:]:
            snake.reset()

        pygame.display.update()
        clock.tick(SPEED)


if __name__ == '__main__':
    main()
