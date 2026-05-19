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

class GameObject(ABC):
    def __init__(self, obj_id: int, x: int, y: int, is_interactable: bool):
        self.id = obj_id
        self.x = x
        self.y = y
        self.is_interactable = is_interactable

    @abstractmethod
    def on_interact(self):
        pass


class Player(Entity):
    def __init__(self, x: int, y: int, width: int, height: int, speed: int):
        super().__init__(x, y, width, height, speed)
        self.visibility_level: int = 100
        self.is_hidden: bool = False
        self.has_objective: bool = False
        self.image.fill((0, 255, 0))

    def hide(self):
        self.is_hidden = True
        self.visibility_level = 0
        print("Player is now hidden.")

    def interact(self, obj: GameObject):
        if obj.is_interactable:
            obj.on_interact()

    def update_visibility(self):
        if not self.is_hidden:
            self.visibility_level = 100


class Tile:
    def __init__(self, x: int, y: int, is_wall: bool, texture: str):
        self.x = x
        self.y = y
        self.is_wall = is_wall
        self.texture = texture


class Room:
    def __init__(self, x: int, y: int, width: int, height: int, room_type: str):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.room_type = room_type
        self.objects: List[GameObject] = []

    def generate_objects(self):
        pass


class GameMap:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.tiles: List[List[Tile]] = []
        self.rooms: List[Room] = []
        self.tile_size = 32

    def load_map(self, file_path: str):
        self.tiles = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                is_wall = (x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1)
                row.append(Tile(x, y, is_wall, "wall_tex" if is_wall else "floor_tex"))
            self.tiles.append(row)

    def is_walkable(self, x: int, y: int) -> bool:
        if 0 <= x < self.width and 0 <= y < self.height:
            return not self.tiles[y][x].is_wall
        return False

    def draw(self, screen: pygame.Surface):
        for y in range(self.height):
            for x in range(self.width):
                tile = self.tiles[y][x]
                color = (100, 100, 100) if tile.is_wall else (200, 200, 200)
                rect = pygame.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (50, 50, 50), rect, 1)  # Grid line

class Enemy(Entity):
    def __init__(self, x, y, width, height, speed):
        super().__init__(x, y, width, height, speed)
        self.image.fill((255, 0, 0))
        self.alert_level = 0
        self.patrol_points = []
        self.current_state = None

    def change_state(self, new_state: EnemyState):
        if self.current_state:
            self.current_state.exit(self)
        self.current_state = new_state
        self.current_state.enter(self)

    def detect_player(self, player: Player) -> bool:
        return False

    def update_enemy(self, player: Player):
        if self.current_state:
            self.current_state.execute(self, player)
        super().update()


class Game:
    def __init__(self):
        self.state: str = "INIT"
        self.map: GameMap = GameMap(25, 18)  # Contoh ukuran grid 25x18 (800x576 px)
        self.player: Player = Player(64, 64, 32, 32, 5)
        self.enemies: List[Enemy] = []

    def start(self):
        self.state = "PLAYING"
        self.map.load_map("dummy_path")

        enemy1 = Enemy(400, 300, 32, 32, 2)
        enemy1.change_state(PatrolState())
        self.enemies.append(enemy1)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]: dy = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy = 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx = 1

        if dx != 0 or dy != 0:
            if dx != 0 and dy != 0:
                dx *= 0.7071
                dy *= 0.7071
            self.player.move(dx, dy, self.map)

    def update(self):
        if self.state == "PLAYING":
            self.player.update()
            for enemy in self.enemies:
                enemy.update_enemy(self.player)

    def draw(self, screen: pygame.Surface):
        screen.fill((0, 0, 0))  # Background hitam
        self.map.draw(screen)
        self.player.draw(screen)
        for enemy in self.enemies:
            enemy.draw(screen)