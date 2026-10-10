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
        pass


class Apple(GameObject):
    """Класс, представляющий яблоко в игре.
    Отвечает за генерацию позиции яблока в пределах игрового поля
    и его отрисовку.
    """

    def __init__(self, body_color=APPLE_COLOR):
        super().__init__((0, 0), body_color)  # сначала базовый init
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
        pygame.draw.circle(screen,
                           self.body_color,
                           (self.position[0] + GRID_SIZE // 2,
                            self.position[1] + GRID_SIZE // 2),
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
        new_head = ()
        if head_x + dir_x * GRID_SIZE > SCREEN_WIDTH:
            new_head = (0, head_y + dir_y * GRID_SIZE)
        elif head_y + dir_y * GRID_SIZE > SCREEN_HEIGHT:
            new_head = (head_x + dir_x * GRID_SIZE, 0)
        elif head_x + dir_x * GRID_SIZE < 0:
            new_head = (SCREEN_WIDTH + dir_x * GRID_SIZE,
                        head_y + dir_y * GRID_SIZE)
        elif head_y + dir_y * GRID_SIZE < 0:
            new_head = (head_x + dir_x * GRID_SIZE,
                        SCREEN_HEIGHT + dir_y * GRID_SIZE)
        else:
            new_head = (head_x + dir_x * GRID_SIZE, head_y + dir_y * GRID_SIZE)

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
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Основная функция.
    Инициализирует объекты игры, запускает игровой цикл,
    обрабатывает столкновения, увеличение длины змейки и сброс при проигрыше.
    """
    pygame.init()

    apple = Apple(APPLE_COLOR)
    snake = Snake(SNAKE_COLOR)

    running = True
    while running:
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

        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()

        pygame.display.update()
        clock.tick(SPEED)


if __name__ == '__main__':
    main()
