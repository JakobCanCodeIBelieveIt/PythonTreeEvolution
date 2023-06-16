import pygame
import sys
import random
import os
from pygame.locals import QUIT, KEYDOWN, K_LEFT, K_RIGHT, K_UP, K_DOWN, MOUSEBUTTONDOWN, K_s

# Инициализация библиотеки pygame
pygame.init()

# Определение констант
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 600
CELL_SIZE = 10
GROUND_HEIGHT = 50
MAX_LIGHT_LEVEL = 15
GENOME_PANEL_WIDTH = 400

# Создание окна
window = pygame.display.set_mode((WINDOW_WIDTH + GENOME_PANEL_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Симуляция эволюции растений")

# Шрифт для текста
font = pygame.font.Font(None, 36)

# Скорости обновления
update_rates = [1, 2, 5, 10, 20, 50, 100]
current_rate_index = 3

# Счетчики и переменные состояния
cycle_counter = 0
current_light_level = 10
current_time = pygame.time.get_ticks()

# Множество занятых ячеек на экране
occupied_cells = set()
# Выбранное растение
selected_plant = None


class GrowingSeed:
    def __init__(self, x, y, color, genome):
        self.x = x
        self.y = y
        # Устанавливаем цвет семян на более темный оттенок
        self.color = (max(0, color[0] - 50), max(0, color[1] - 50), max(0, color[2] - 50))
        self.genome = genome

    def get_changed_cells(self):
        return [(self.x, self.y, self.color)]


# Класс растения
class Plant:
    def __init__(self, x, y, genome, color):
        self.genes = genome['genes']
        self.lifetime = genome['lifetime']
        self.color = color
        self.cells = [(x, y, 0)]  # добавим жизненный счетчик
        self.age = 0  # новый параметр "возраст"
        self.changed_cells = []

    # Рост растения
    # Рост растения
    def grow(self):
        self.age += 1  # увеличиваем "возраст" на 1
        new_cells = []
        for x, y, index in self.cells:
            if index < len(self.genes):
                current_gene = self.genes[index]
                directions = [(0, -1), (-1, 0), (1, 0), (0, 1)]  # Вверх, влево, вправо, вниз

                # Проверка условий пятого числа гена
                should_use_alt_gene = False
                gene_condition = current_gene[4]
                if 1 <= gene_condition <= 5:
                    should_use_alt_gene = 1 <= current_light_level <= 5
                elif 6 <= gene_condition <= 10:
                    should_use_alt_gene = 6 <= current_light_level <= 10
                elif 11 <= gene_condition <= 15:
                    should_use_alt_gene = 11 <= current_light_level <= 15
                elif 16 <= gene_condition <= 20:
                    should_use_alt_gene = current_light_level == 0
                elif 21 <= gene_condition <= 30:
                    continue  # клетка становится зерном и не растет
                # 31 <= gene_condition <= 40 не устанавливается условие

                # Если условие выполнено, берем схему распространения из другого гена
                if should_use_alt_gene:
                    alt_gene_index = current_gene[5]
                    if alt_gene_index < len(self.genes):
                        current_gene = self.genes[alt_gene_index]

                # Основная логика роста
                for i in range(4):
                    value = current_gene[i]
                    if value <= 20:
                        dx, dy = directions[i]
                        new_x, new_y = x + dx * CELL_SIZE, y + dy * CELL_SIZE
                        if (new_x, new_y) not in occupied_cells and new_y < WINDOW_HEIGHT - GROUND_HEIGHT:
                            occupied_cells.add((new_x, new_y))
                            new_cells.append((new_x, new_y, value - 1))

        # Добавляем старые клетки после обработки новых
        for x, y, index in self.cells:
            new_cells.append((x, y, index))

        self.cells = new_cells
        self.changed_cells = new_cells

        # Проверка, стала ли клетка семенем
        for x, y, index in self.cells:
            if index < len(self.genes):
                current_gene = self.genes[index]
                if 21 <= current_gene[4] <= 30:
                    # Если клетка стала семенем и находится на земле
                    growing_seeds.append(GrowingSeed(x, y, self.color, self.genes))

            # Создание растений
plant_objects = []
growing_seeds = []
seeds = [
        {'x': WINDOW_WIDTH // 4, 'y': WINDOW_HEIGHT - GROUND_HEIGHT - CELL_SIZE,
        'genome': {'genes': [[random.randint(1, 40) for _ in range(6)] for _ in range(20)],
                            'lifetime': random.randint(80, 90)},
                 'color': (random.randint(64, 255), random.randint(64, 255), random.randint(64, 255))},
                {'x': WINDOW_WIDTH * 3 // 4, 'y': WINDOW_HEIGHT - GROUND_HEIGHT - CELL_SIZE,
                 'genome': {'genes': [[random.randint(1, 40) for _ in range(6)] for _ in range(20)],
                            'lifetime': random.randint(80, 90)},
                 'color': (random.randint(64, 255), random.randint(64, 255), random.randint(64, 255))}
]

for seed in seeds:
    plant = Plant(seed['x'], seed['y'], seed['genome'], seed['color'])
    plant_objects.append(plant)
    occupied_cells.add((seed['x'], seed['y']))

            # Главный цикл игры
while True:
    elapsed_time = pygame.time.get_ticks() - current_time

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            # Управление скоростью обновления
            if event.key == K_RIGHT and current_rate_index < len(update_rates) - 1:
                current_rate_index += 1
            elif event.key == K_LEFT and current_rate_index > 0:
                current_rate_index -= 1
            # Управление уровнем освещения
            elif event.key == K_UP and current_light_level < MAX_LIGHT_LEVEL:
                current_light_level += 1
            elif event.key == K_DOWN and current_light_level > 0:
                current_light_level -= 1
            # Сохранение генома выбранного растения
            elif event.key == K_s and selected_plant is not None:
                with open('genome.txt', 'w') as f:
                    # Сохранение генов
                    for gene in selected_plant.genes:
                        f.write(f"{gene}\n")
                    # Сохранение времени жизни генома
                    f.write(f"Время жизни: {selected_plant.lifetime}\n")


        # Выбор растения по клику мыши
        elif event.type == MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for plant in plant_objects:
                for x, y, _ in plant.cells:
                    if (x < mouse_pos[0] < x + CELL_SIZE) and (y < mouse_pos[1] < y + CELL_SIZE):
                        selected_plant = plant
                        break

# Обновление экрана с заданной скоростью
    if elapsed_time >= 1000 / update_rates[current_rate_index]:
        cycle_counter += 1
        current_time = pygame.time.get_ticks()

        # Заполнение фона
        bg_color = (current_light_level * 17, current_light_level * 17, current_light_level * 17)
        window.fill(bg_color)

        # Отрисовка слоя земли
        pygame.draw.rect(window, (139, 69, 19),
                        (0, WINDOW_HEIGHT - GROUND_HEIGHT, WINDOW_WIDTH, GROUND_HEIGHT))

        for plant in plant_objects[
                     :]:  # Используем копию списка, чтобы избежать ошибок при его модификации во время итерации

            # Проверяем, достиг ли "возраст" растения времени жизни
            if plant.age >= plant.lifetime:
                # Удаляем клетки растения из множества занятых ячеек
                for x, y, index in plant.cells:
                    current_gene = plant.genes[index] if index < len(plant.genes) else None
                    # Если клетка не является семенем, удаляем ее
                    if not (current_gene and 21 <= current_gene[4] <= 30):
                        occupied_cells.discard((x, y))

                # Удаляем клетки растения из множества занятых ячеек
                for x, y, _ in plant.cells:
                    occupied_cells.discard((x, y))
            else:
                # Рост растения
                plant.grow()
                for x, y, _ in plant.cells:
                    # Проверка, чтобы растения не росли в панели вывода генома
                    if x < WINDOW_WIDTH:
                        pygame.draw.rect(window, plant.color, (x, y, CELL_SIZE, CELL_SIZE))
        for seed in growing_seeds:
            for x, y, color in seed.get_changed_cells():
                if x < WINDOW_WIDTH:
                    pygame.draw.rect(window, color, (x, y, CELL_SIZE, CELL_SIZE))

        # Отображение информации на экране
        cycles_text = font.render(f"Циклы: {cycle_counter}", True, (255, 255, 255))
        window.blit(cycles_text, (10, 10))

        light_text = font.render(f"Уровень света: {current_light_level}", True, (255, 255, 255))
        window.blit(light_text, (10, 50))

        # Отображение информации о геноме выбранного растения
        if selected_plant is not None:
            genome_info_text = font.render("Геном:", True, (255, 255, 255))
            window.blit(genome_info_text, (WINDOW_WIDTH + 10, 10))

            for i, gene in enumerate(selected_plant.genes):
                gene_text = font.render(f"{gene}", True, (255, 255, 255))
                window.blit(gene_text, (WINDOW_WIDTH + 10, 40 + i * 20))

            # Отображение времени жизни генома
            lifetime_text = font.render(f"Время жизни: {selected_plant.lifetime}", True, (255, 255, 255))
            window.blit(lifetime_text, (WINDOW_WIDTH + 10, 50 + len(selected_plant.genes) * 20))

            # Отображение "возраста" генома
            age_text = font.render(f"Прожитые циклы: {selected_plant.age}", True, (255, 255, 255))
            window.blit(age_text, (WINDOW_WIDTH + 10, 80 + len(selected_plant.genes) * 20))

        # Обновление дисплея
        pygame.display.update()
