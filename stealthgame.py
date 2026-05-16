import pygame
import math
import random
from abc import ABC, abstractmethod

class Entity(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, width: int, height: int, speed: int):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.sprite = self.image 

    def move(self, dx: float, dy: float, game_map=None):
        """Menggerakkan entitas dengan validasi collision sederhana jika ada map."""
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed

        if game_map:
            tile_x = int(new_x // 32)
            tile_y = int(new_y // 32)
            if game_map.is_walkable(tile_x, tile_y):
                self.x = new_x
                self.y = new_y
        else:
            self.x = new_x
            self.y = new_y

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def update(self):
        """Method overridable untuk update logika entitas di setiap frame."""
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def draw(self, screen: pygame.Surface):
        """Menggambar entitas ke layar."""
        screen.blit(self.image, self.rect)

    def check_collision(self, other_rect: pygame.Rect) -> bool:
        """Mengecek tabrakan dengan rect lain."""
        return self.rect.colliderect(other_rect)


class EnemyState(ABC):
    def __init__(self, state_name: str):
        self.state_name = state_name

    @abstractmethod
    def enter(self, enemy):
        """Dijalankan sekali saat enemy memasuki state ini."""
        pass

    @abstractmethod
    def execute(self, enemy, player):
        """Dijalankan setiap frame (game loop) untuk memperbarui logika state."""
        pass

    @abstractmethod
    def exit(self, enemy):
        """Dijalankan sekali saat enemy keluar dari state ini."""
        pass


class PatrolState(EnemyState):
    def __init__(self):
        super().__init__("Patrol")
        self.current_point_index = 0
        self.wait_time = 0.0 
        self.stay_timer = 0   

    def enter(self, enemy):
        enemy.alert_level = 0
        if enemy.patrol_points:
            self.current_point_index = 0

    def execute(self, enemy, player):
        if enemy.detect_player(player):
            from __main__ import ChaseState
            enemy.change_state(ChaseState())
            return

        if not enemy.patrol_points:
            return

        target_point = enemy.patrol_points[self.current_point_index]
        dx = target_point[0] - enemy.x
        dy = target_point[1] - enemy.y
        distance = math.hypot(dx, dy)

        if distance < 5: 
            if self.stay_timer == 0:
                self.stay_timer = pygame.time.get_ticks()
            
            if pygame.time.get_ticks() - self.stay_timer > 1000:
                self.move_to_next_point(enemy)
                self.stay_timer = 0
        else:
            direction_x = dx / distance
            direction_y = dy / distance
            enemy.move(direction_x, direction_y)

    def move_to_next_point(self, enemy):
        """Beralih ke indeks rute patroli berikutnya."""
        if enemy.patrol_points:
            self.current_point_index = (self.current_point_index + 1) % len(enemy.patrol_points)

    def exit(self, enemy):
        pass


class ChaseState(EnemyState):
    def __init__(self):
        super().__init__("Chase")
        self.chase_speed_multiplier = 1.5
        self.last_seen_position = (0, 0)

    def enter(self, enemy):
        enemy.alert_level = 100
        self.original_speed = enemy.speed
        enemy.speed = int(enemy.speed * self.chase_speed_multiplier)

    def execute(self, enemy, player):
        if enemy.detect_player(player):
            self.last_seen_position = (player.x, player.y)
            self.follow_player(enemy, player)
        else:
            dx = self.last_seen_position[0] - enemy.x
            dy = self.last_seen_position[1] - enemy.y
            dist = math.hypot(dx, dy)

            if dist > 10:
                self.follow_player(enemy, player)
            else:
                enemy.change_state(SearchState(self.last_seen_position))

    def follow_player(self, enemy, player):
        target_x = player.x if enemy.detect_player(player) else self.last_seen_position[0]
        target_y = player.y if enemy.detect_player(player) else self.last_seen_position[1]
        
        dx = target_x - enemy.x
        dy = target_y - enemy.y
        distance = math.hypot(dx, dy)
        
        if distance > 0:
            enemy.move(dx / distance, dy / distance)

    def exit(self, enemy):
        enemy.speed = self.original_speed


class SearchState(EnemyState):
    def __init__(self, search_position: tuple):
        super().__init__("Search")
        self.search_position = search_position
        self.search_timer = 5.0  
        self.start_ticks = 0
        self.sub_target = None

    def enter(self, enemy):
        enemy.alert_level = 50
        self.start_ticks = pygame.time.get_ticks()
        self.generate_random_sub_target(enemy)

    def execute(self, enemy, player):
        if enemy.detect_player(player):
            enemy.change_state(ChaseState())
            return

        seconds_passed = (pygame.time.get_ticks() - self.start_ticks) / 1000.0
        if seconds_passed >= self.search_timer:
            enemy.change_state(PatrolState())
            return

        self.search_area(enemy)

    def generate_random_sub_target(self, enemy):
        """Membuat titik acak di sekitar lokasi terakhir player terlihat."""
        radius = 80
        random_angle = random.uniform(0, 2 * math.pi)
        random_radius = random.uniform(20, radius)
        
        self.sub_target = (
            self.search_position[0] + math.cos(random_angle) * random_radius,
            self.search_position[1] + math.sin(random_angle) * random_radius
        )

    def search_area(self, enemy):
        if not self.sub_target:
            return

        dx = self.sub_target[0] - enemy.x
        dy = self.sub_target[1] - enemy.y
        distance = math.hypot(dx, dy)

        if distance < 10:
            self.generate_random_sub_target(enemy)
        else:
            enemy.move(dx / distance, dy / distance)

    def exit(self, enemy):
        pass