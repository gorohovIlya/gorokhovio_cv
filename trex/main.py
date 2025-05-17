import cv2
import numpy as np
import pyautogui
import mss
import time


class AdaptiveDinoGame:
    def __init__(self):
        self.game_area = {'top': 300, 'left': 100, 'width': 800, 'height': 150}
        self.sct = mss.mss()

        # Базовые параметры
        self.dino_width = 70
        self.dino_height = 60
        self.dino_position = None

        # Адаптивные параметры
        self.game_speed = 1.0
        self.last_obstacle_time = time.time()
        self.speed_update_interval = 5.0
        self.last_speed_update = time.time()

        # Для отладки
        self.debug_window = "Adaptive Dino AI"
        cv2.namedWindow(self.debug_window, cv2.WINDOW_NORMAL)

    def update_game_speed(self):
        """Адаптивно обновляем скорость игры на основе времени между препятствиями"""
        current_time = time.time()
        if current_time - self.last_speed_update > self.speed_update_interval:
            # Эмпирическая формула для скорости (чем чаще препятствия, тем выше скорость)
            if current_time - self.last_obstacle_time < 1.0:
                self.game_speed = min(3.0, self.game_speed + 0.2)
            else:
                self.game_speed = max(1.0, self.game_speed - 0.1)
            self.last_speed_update = current_time

    def get_reaction_distance(self):
        """Динамически вычисляем дистанцию реакции в зависимости от скорости"""
        base_distance = 60
        return int(base_distance * self.game_speed)

    def get_screenshot(self):
        screenshot = np.array(self.sct.grab(self.game_area))
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2GRAY)

        # Автоматически находим динозавра (левый нижний угол)
        dino_roi = gray[-self.dino_height:, :25 ]  # Ищем в левой нижней части
        _, dino_binary = cv2.threshold(dino_roi, 200, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(dino_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if w > 20 and h > 30:  # Фильтруем по размеру (чтобы не захватить шум)
                self.dino_position = x + w  # Правая граница динозавра
                break

        return screenshot, gray

    def preprocess_image(self, gray_img):
        if self.dino_position is None:
            return np.zeros_like(gray_img)
        # _, binary = cv2.threshold(gray_img, self.obstacle_threshold, 255, cv2.THRESH_BINARY_INV)
        binary = cv2.adaptiveThreshold(gray_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
        binary[:, :self.dino_position + self.dino_width] = 0

        # Адаптивное морфологическое преобразование
        kernel_size = int(3 * self.game_speed)
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        processed = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        return processed

    def detect_obstacles(self, processed_img):
        search_area = processed_img[:, self.dino_position + self.dino_width:]
        contours, _ = cv2.findContours(search_area, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        obstacles = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            # Адаптивные минимальные размеры
            min_width = max(5, int(5 / self.game_speed))
            min_height = max(12, int(12 / self.game_speed))

            if w > min_width and h > min_height:
                x += self.dino_position + self.dino_width

                # Критерии для птиц становятся строже с  увеличением скорости
                if h < max(30, int(40 / self.game_speed)) and y < 80:
                    obstacles.append(('bird', x, x + w, y, y + h))
                else:
                    obstacles.append(('cactus', x, x + w, y, y + h))
                    self.last_obstacle_time = time.time()

        return obstacles

    def should_jump(self, obstacles):
        reaction_distance = self.get_reaction_distance()

        for obstacle in obstacles:
            type_obstacle, min_x, max_x, min_y, max_y = obstacle
            distance = min_x - (self.dino_position + self.dino_width)

            # Адаптивный порог реакции
            if distance < reaction_distance:
                if type_obstacle == 'bird' and min_y < 80:
                    return 'jump'
                elif type_obstacle == 'bird':
                    return 'duck'
                else:
                    return 'jump'

        return None

    def update_debug_view(self, screenshot, obstacles, processed_img):
        debug_img = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

        # Показываем обработанное изображение
        processed_colored = cv2.cvtColor(processed_img, cv2.COLOR_GRAY2BGR)
        debug_img = np.hstack((debug_img, processed_colored))

        # Область динозавра
        cv2.rectangle(debug_img,
                      (self.dino_position, self.dino_height),
                      (self.dino_position + self.dino_width, self.dino_height * 2),
                      (255, 0, 255), 2)

        # Линия реакции (динамическая)
        reaction_line = self.dino_position // 2  + self.get_reaction_distance()
        cv2.line(debug_img,
                 (reaction_line, 0),
                 (reaction_line, debug_img.shape[0]),
                 (0, 255, 255), 2)

        # Препятствия
        for obstacle in obstacles:
            type_obstacle, min_x, max_x, min_y, max_y = obstacle
            color = (0, 0, 255) if type_obstacle == 'cactus' else (255, 0, 0)
            cv2.rectangle(debug_img,
                          (int(min_x), int(min_y)),
                          (int(max_x), int(max_y)),
                          color, 2)

        # Отображаем скорость
        cv2.putText(debug_img, f"Speed: {self.game_speed:.1f}x",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow(self.debug_window, debug_img)
        cv2.waitKey(1)

    def run(self):
        print("Запуск адаптивного Dino AI... Нажмите Ctrl+C для остановки")
        time.sleep(2)

        try:
            while True:
                self.update_game_speed()
                screenshot, gray = self.get_screenshot()
                processed = self.preprocess_image(gray)
                obstacles = self.detect_obstacles(processed)
                action = self.should_jump(obstacles)

                # Адаптивное время реакции
                if action == 'jump':
                    pyautogui.keyDown('space')
                    pyautogui.keyUp('space')
                elif action == 'duck':
                    pyautogui.keyDown('down')
                    pyautogui.keyUp('down')

                self.update_debug_view(screenshot, obstacles, processed)

        except KeyboardInterrupt:
            cv2.destroyAllWindows()
            print("Остановка")


if __name__ == "__main__":
    game = AdaptiveDinoGame()
    game.run()