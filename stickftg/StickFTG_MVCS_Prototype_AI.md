# StickFTG（火柴人 2D FTG）最小可玩 Prototype + MVCS + OOP + AI 對戰架構（Python / Pygame / Docker）

> 目標：**沒有任何動畫素材**也能做出「能打、能判定、能結束回合」的 2D 火柴人 FTG。  
> 特色：**MVCS 分層、OOP 實體、Frame-based 戰鬥、可 Headless 模擬、可 AI 自對戰**。

---

## 1) 你會得到什麼

### ✅ A. 最小可玩 FTG Prototype（本機可跑）
- 兩個火柴人（P1 / P2）
- 左右移動、跳躍、面向
- 輕攻擊（可造成傷害）
- Hitbox / Hurtbox 判定（Frame-based）
- 生命值條、倒數計時、勝負判定（KO / Time Over）

### ✅ B. 完整 MVCS + OOP 範本（可擴充）
- **Model**：Fighter/State/Hitbox
- **View**：Renderer / StickmanDrawer
- **Controller**：InputController / AIController
- **Service**：Physics / Combat / Collision / MatchRule
- **Core**：Game Loop / Scene / Clock

### ✅ C. AI 對戰架構規劃（可 Headless、可自對戰）
- `GameEnv.step(action_p1, action_p2)`：可用於 RL / 搜尋 / 自對戰
- Replay：只記錄 input + seed，可 100% 重播
- Deterministic：frame 為單位更新，利於訓練與回放
- Docker：跑測試、跑 headless 模擬、跑 batch self-play

---

## 2) 專案樹（建議）

```
stickftg/
├─ README.md
├─ requirements.txt
├─ main.py
├─ game/
│  ├─ core/
│  │  ├─ game.py
│  │  ├─ config.py
│  │  ├─ constants.py
│  │  └─ clock.py
│  ├─ models/
│  │  ├─ fighter.py
│  │  ├─ state.py
│  │  ├─ hitbox.py
│  │  └─ types.py
│  ├─ services/
│  │  ├─ physics_service.py
│  │  ├─ collision_service.py
│  │  ├─ combat_service.py
│  │  └─ match_service.py
│  ├─ controllers/
│  │  ├─ input_controller.py
│  │  └─ ai_controller.py
│  ├─ views/
│  │  ├─ renderer.py
│  │  └─ stickman_drawer.py
│  └─ env/
│     ├─ ftg_env.py
│     └─ replay.py
├─ tests/
│  └─ test_combat.py
└─ docker/
   ├─ Dockerfile
   └─ docker-compose.yml
```

---

## 3) 快速開始（本機）

### 3.1 安裝
```bash
cd stickftg
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python main.py
```

### 3.2 操作
- P1：A/D 移動、W 跳、J 攻擊
- P2：←/→ 移動、↑ 跳、Numpad1（或你可改成 `,`）攻擊
- F1：顯示 debug boxes
- F2：P2 切換 AI / 2P
- R：回合結束後重開

---

## 4) 依賴（requirements.txt）
```txt
pygame==2.5.2
```

---

## 5) 代碼（可直接照檔名建立）

> ⚠️ 下面是「最小可玩 + 分層完整」版本：  
> 你只要照檔名建立、貼上，即可跑起來。

---

### 5.1 main.py
```python
from game.core.game import Game

if __name__ == "__main__":
    Game().run()
```

---

### 5.2 game/core/constants.py
```python
FPS = 60
DT = 1.0 / FPS

SCREEN_W = 960
SCREEN_H = 540

GROUND_Y = 420

GRAVITY = 2400.0           # px/s^2
MOVE_SPEED = 340.0         # px/s
JUMP_VELOCITY = -900.0     # px/s

MAX_HP = 100
ROUND_TIME_SEC = 60
```

---

### 5.3 game/core/config.py
```python
from dataclasses import dataclass
from .constants import SCREEN_W, SCREEN_H

@dataclass(frozen=True)
class GameConfig:
    width: int = SCREEN_W
    height: int = SCREEN_H
    title: str = "StickFTG - MVCS Prototype"
```

---

### 5.4 game/core/clock.py
```python
from dataclasses import dataclass
from .constants import FPS

@dataclass
class FixedClock:
    fps: int = FPS
    frame: int = 0

    def tick(self):
        self.frame += 1
```

---

### 5.5 game/models/types.py
```python
from dataclasses import dataclass

@dataclass
class Vec2:
    x: float
    y: float
```

---

### 5.6 game/models/state.py
```python
from enum import Enum, auto

class FighterState(Enum):
    IDLE = auto()
    MOVE = auto()
    JUMP = auto()
    ATTACK = auto()
    HITSTUN = auto()
    DEAD = auto()
```

---

### 5.7 game/models/hitbox.py
```python
from dataclasses import dataclass
import pygame

@dataclass
class Box:
    x: float
    y: float
    w: float
    h: float

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), int(self.w), int(self.h))

@dataclass
class AttackFrame:
    startup: int     # frames before active
    active: int      # active frames
    recovery: int    # frames after active
    damage: int
    knockback_x: float
    hitbox_w: int
    hitbox_h: int
    hitbox_offset_x: int
    hitbox_offset_y: int

    @property
    def total(self) -> int:
        return self.startup + self.active + self.recovery
```

---

### 5.8 game/models/fighter.py
```python
from dataclasses import dataclass, field
from .types import Vec2
from .state import FighterState
from .hitbox import Box, AttackFrame

@dataclass
class Fighter:
    name: str
    pos: Vec2
    vel: Vec2
    facing: int  # +1 right, -1 left
    hp: int = 100
    state: FighterState = FighterState.IDLE

    on_ground: bool = True
    state_frame: int = 0          # current frame inside current state
    hitstun_left: int = 0

    # For attack
    attack_def: AttackFrame = field(default_factory=lambda: AttackFrame(
        startup=6, active=4, recovery=10,
        damage=10, knockback_x=320.0,
        hitbox_w=70, hitbox_h=40,
        hitbox_offset_x=40, hitbox_offset_y=-70
    ))

    def reset_state_frame(self):
        self.state_frame = 0

    def set_state(self, st: FighterState):
        if self.state != st:
            self.state = st
            self.reset_state_frame()

    def step_state_frame(self):
        self.state_frame += 1

    def hurtbox(self) -> Box:
        # Simple body box (stickman) — tune as you like
        return Box(self.pos.x - 18, self.pos.y - 90, 36, 90)

    def current_hitbox(self) -> Box | None:
        # Only during ATTACK active frames
        if self.state != FighterState.ATTACK:
            return None
        f = self.state_frame
        a = self.attack_def
        if f < a.startup:
            return None
        if f >= a.startup + a.active:
            return None

        # Place hitbox in front of fighter depending on facing
        x = self.pos.x + self.facing * a.hitbox_offset_x
        y = self.pos.y + a.hitbox_offset_y
        if self.facing < 0:
            x -= a.hitbox_w  # mirror
        return Box(x, y, a.hitbox_w, a.hitbox_h)

    def is_dead(self) -> bool:
        return self.hp <= 0
```

---

### 5.9 game/services/physics_service.py
```python
from ..core.constants import GRAVITY, GROUND_Y

class PhysicsService:
    def apply(self, fighter, dt: float):
        fighter.vel.y += GRAVITY * dt
        fighter.pos.x += fighter.vel.x * dt
        fighter.pos.y += fighter.vel.y * dt

        if fighter.pos.y >= GROUND_Y:
            fighter.pos.y = GROUND_Y
            fighter.vel.y = 0.0
            fighter.on_ground = True
        else:
            fighter.on_ground = False
```

---

### 5.10 game/services/collision_service.py
```python
class CollisionService:
    def overlap(self, box_a, box_b) -> bool:
        return box_a.rect().colliderect(box_b.rect())
```

---

### 5.11 game/services/combat_service.py
```python
from ..models.state import FighterState

class CombatService:
    def __init__(self, collision):
        self.collision = collision

    def resolve(self, attacker, defender):
        hb = attacker.current_hitbox()
        if hb is None:
            return

        if self.collision.overlap(hb, defender.hurtbox()):
            # Damage once per attack (hit only on first active frame)
            if attacker.state_frame != attacker.attack_def.startup:
                return

            defender.hp = max(0, defender.hp - attacker.attack_def.damage)

            defender.vel.x = attacker.facing * attacker.attack_def.knockback_x
            defender.vel.y = -240.0

            defender.hitstun_left = 16
            defender.set_state(FighterState.HITSTUN)
```

---

### 5.12 game/services/match_service.py
```python
from ..core.constants import ROUND_TIME_SEC, FPS
from ..models.state import FighterState

class MatchService:
    def __init__(self):
        self.round_frames = ROUND_TIME_SEC * FPS
        self.frame_left = self.round_frames
        self.winner = None

    def step(self, p1, p2):
        if self.winner is not None:
            return

        self.frame_left -= 1
        if p1.is_dead():
            self.winner = p2.name
            p1.set_state(FighterState.DEAD)
            return
        if p2.is_dead():
            self.winner = p1.name
            p2.set_state(FighterState.DEAD)
            return

        if self.frame_left <= 0:
            if p1.hp > p2.hp:
                self.winner = p1.name
            elif p2.hp > p1.hp:
                self.winner = p2.name
            else:
                self.winner = "DRAW"
```

---

### 5.13 game/controllers/input_controller.py
```python
import pygame
from ..core.constants import MOVE_SPEED, JUMP_VELOCITY
from ..models.state import FighterState

class InputController:
    def __init__(self, scheme: dict):
        self.scheme = scheme

    def update(self, fighter):
        keys = pygame.key.get_pressed()

        if fighter.state in (FighterState.HITSTUN, FighterState.DEAD):
            return

        # Attack priority
        if keys[self.scheme["attack"]]:
            if fighter.state != FighterState.ATTACK:
                fighter.set_state(FighterState.ATTACK)
                fighter.vel.x = 0
            return

        move = 0
        if keys[self.scheme["left"]]:
            move -= 1
        if keys[self.scheme["right"]]:
            move += 1

        if move != 0:
            fighter.vel.x = move * MOVE_SPEED
            fighter.facing = 1 if move > 0 else -1
            if fighter.on_ground:
                fighter.set_state(FighterState.MOVE)
        else:
            fighter.vel.x = 0
            if fighter.on_ground:
                fighter.set_state(FighterState.IDLE)

        if keys[self.scheme["jump"]] and fighter.on_ground:
            fighter.vel.y = JUMP_VELOCITY
            fighter.set_state(FighterState.JUMP)
```

---

### 5.14 game/controllers/ai_controller.py
```python
from ..core.constants import MOVE_SPEED
from ..models.state import FighterState

class SimpleAIController:
    def update(self, fighter, opponent):
        if fighter.state in (FighterState.HITSTUN, FighterState.DEAD):
            return

        dx = opponent.pos.x - fighter.pos.x

        if abs(dx) < 90 and fighter.state != FighterState.ATTACK:
            fighter.set_state(FighterState.ATTACK)
            fighter.vel.x = 0
            fighter.facing = 1 if dx > 0 else -1
            return

        if dx > 10:
            fighter.vel.x = MOVE_SPEED * 0.8
            fighter.facing = 1
            if fighter.on_ground:
                fighter.set_state(FighterState.MOVE)
        elif dx < -10:
            fighter.vel.x = -MOVE_SPEED * 0.8
            fighter.facing = -1
            if fighter.on_ground:
                fighter.set_state(FighterState.MOVE)
        else:
            fighter.vel.x = 0
            if fighter.on_ground:
                fighter.set_state(FighterState.IDLE)
```

---

### 5.15 game/views/stickman_drawer.py
```python
import pygame

class StickmanDrawer:
    def draw(self, screen, fighter, color=(255,255,255)):
        x = int(fighter.pos.x)
        y = int(fighter.pos.y)

        head = (x, y - 105)
        neck = (x, y - 90)
        hip  = (x, y - 45)

        shoulder_l = (x - 20, y - 80)
        shoulder_r = (x + 20, y - 80)

        if fighter.state.name == "ATTACK":
            hand = (x + fighter.facing * 55, y - 75)
        else:
            hand = (x + fighter.facing * 30, y - 65)

        knee_l = (x - 15, y - 20)
        foot_l = (x - 25, y)
        knee_r = (x + 15, y - 20)
        foot_r = (x + 25, y)

        pygame.draw.circle(screen, color, head, 12, 2)
        pygame.draw.line(screen, color, neck, hip, 2)

        pygame.draw.line(screen, color, shoulder_l, hip, 2)
        pygame.draw.line(screen, color, shoulder_r, hip, 2)

        pygame.draw.line(screen, color, shoulder_r if fighter.facing > 0 else shoulder_l, hand, 3)

        pygame.draw.line(screen, color, hip, knee_l, 2)
        pygame.draw.line(screen, color, knee_l, foot_l, 2)
        pygame.draw.line(screen, color, hip, knee_r, 2)
        pygame.draw.line(screen, color, knee_r, foot_r, 2)
```

---

### 5.16 game/views/renderer.py
```python
import pygame
from ..core.constants import SCREEN_W, GROUND_Y

class Renderer:
    def __init__(self):
        self.font = pygame.font.SysFont("consolas", 20)

    def draw_ui(self, screen, p1, p2, match):
        pygame.draw.line(screen, (120, 120, 120), (0, GROUND_Y), (SCREEN_W, GROUND_Y), 2)

        self._hp_bar(screen, 60, 40, p1.hp, (60, 200, 60))
        self._hp_bar(screen, SCREEN_W-260, 40, p2.hp, (200, 60, 60))

        screen.blit(self.font.render(p1.name, True, (220,220,220)), (60, 15))
        screen.blit(self.font.render(p2.name, True, (220,220,220)), (SCREEN_W-260, 15))

        sec_left = max(0, match.frame_left // 60)
        t = self.font.render(f"TIME {sec_left:02d}", True, (240,240,240))
        screen.blit(t, (SCREEN_W//2 - 50, 15))

        if match.winner is not None:
            msg = self.font.render(f"WINNER: {match.winner}  (R to restart)", True, (255, 220, 60))
            screen.blit(msg, (SCREEN_W//2 - 190, 80))

    def _hp_bar(self, screen, x, y, hp, color):
        w, h = 200, 16
        hp = max(0, min(100, hp))
        fill = int(w * (hp/100.0))
        pygame.draw.rect(screen, (60,60,60), (x, y, w, h))
        pygame.draw.rect(screen, color, (x, y, fill, h))
        pygame.draw.rect(screen, (220,220,220), (x, y, w, h), 2)

    def draw_debug_boxes(self, screen, fighter, show_hitbox=False):
        pygame.draw.rect(screen, (80, 160, 255), fighter.hurtbox().rect(), 1)
        if show_hitbox:
            hit = fighter.current_hitbox()
            if hit:
                pygame.draw.rect(screen, (255, 120, 80), hit.rect(), 1)
```

---

### 5.17 game/core/game.py
```python
import pygame
from .config import GameConfig
from .constants import FPS, DT, SCREEN_W, GROUND_Y
from .clock import FixedClock

from ..models.types import Vec2
from ..models.fighter import Fighter
from ..models.state import FighterState

from ..services.physics_service import PhysicsService
from ..services.collision_service import CollisionService
from ..services.combat_service import CombatService
from ..services.match_service import MatchService

from ..controllers.input_controller import InputController
from ..controllers.ai_controller import SimpleAIController

from ..views.renderer import Renderer
from ..views.stickman_drawer import StickmanDrawer

class Game:
    def __init__(self):
        self.cfg = GameConfig()
        pygame.init()
        pygame.display.set_caption(self.cfg.title)
        self.screen = pygame.display.set_mode((self.cfg.width, self.cfg.height))
        self.clock = pygame.time.Clock()
        self.fixed = FixedClock()

        self.physics = PhysicsService()
        self.collision = CollisionService()
        self.combat = CombatService(self.collision)
        self.match = MatchService()

        self.renderer = Renderer()
        self.drawer = StickmanDrawer()

        self.p1 = Fighter("P1", pos=Vec2(280, GROUND_Y), vel=Vec2(0,0), facing=1, hp=100)
        self.p2 = Fighter("P2", pos=Vec2(680, GROUND_Y), vel=Vec2(0,0), facing=-1, hp=100)

        self.p1_ctrl = InputController({
            "left": pygame.K_a,
            "right": pygame.K_d,
            "jump": pygame.K_w,
            "attack": pygame.K_j,
        })

        self.p2_ctrl = InputController({
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
            "jump": pygame.K_UP,
            "attack": pygame.K_KP1,
        })
        self.p2_ai = SimpleAIController()
        self.use_ai_for_p2 = False

        self.show_debug = False

    def restart(self):
        self.__init__()

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F1:
                        self.show_debug = not self.show_debug
                    if event.key == pygame.K_F2:
                        self.use_ai_for_p2 = not self.use_ai_for_p2
                    if event.key == pygame.K_r and self.match.winner is not None:
                        self.restart()
                        return

            self.p1_ctrl.update(self.p1)
            if self.use_ai_for_p2:
                self.p2_ai.update(self.p2, self.p1)
            else:
                self.p2_ctrl.update(self.p2)

            # Face each other (basic)
            if self.p1.state not in (FighterState.ATTACK, FighterState.HITSTUN):
                self.p1.facing = 1 if (self.p2.pos.x - self.p1.pos.x) > 0 else -1
            if self.p2.state not in (FighterState.ATTACK, FighterState.HITSTUN):
                self.p2.facing = 1 if (self.p1.pos.x - self.p2.pos.x) > 0 else -1

            self._step_fighter(self.p1)
            self._step_fighter(self.p2)

            self.combat.resolve(self.p1, self.p2)
            self.combat.resolve(self.p2, self.p1)

            self.match.step(self.p1, self.p2)
            self.fixed.tick()

            self.screen.fill((20, 20, 26))

            self.drawer.draw(self.screen, self.p1, color=(220,220,220))
            self.drawer.draw(self.screen, self.p2, color=(220,220,220))

            self.renderer.draw_ui(self.screen, self.p1, self.p2, self.match)

            if self.show_debug:
                self.renderer.draw_debug_boxes(self.screen, self.p1, show_hitbox=True)
                self.renderer.draw_debug_boxes(self.screen, self.p2, show_hitbox=True)
                self._debug_text()

            pygame.display.flip()

        pygame.quit()

    def _debug_text(self):
        font = pygame.font.SysFont("consolas", 16)
        msg = f"F1 debug | F2 toggle AI(P2)={self.use_ai_for_p2}"
        self.screen.blit(font.render(msg, True, (200,200,200)), (20, 500))

    def _step_fighter(self, f):
        if f.state == FighterState.HITSTUN:
            f.hitstun_left -= 1
            if f.hitstun_left <= 0 and not f.is_dead():
                f.set_state(FighterState.IDLE)

        if f.state == FighterState.ATTACK:
            f.step_state_frame()
            if f.state_frame >= f.attack_def.total:
                f.set_state(FighterState.IDLE)
        else:
            f.step_state_frame()

        if f.is_dead():
            f.set_state(FighterState.DEAD)
            f.vel.x = 0

        self.physics.apply(f, DT)

        if f.pos.x < 40:
            f.pos.x = 40
        if f.pos.x > SCREEN_W - 40:
            f.pos.x = SCREEN_W - 40
```

---

## 6) Docker（建議用法：跑測試 / Headless）

### 6.1 docker/Dockerfile
```dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y     build-essential     && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "pytest", "-q"]
```

### 6.2 docker/docker-compose.yml
```yaml
version: "3.9"
services:
  stickftg:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    container_name: stickftg
    working_dir: /app
    volumes:
      - ..:/app
```

---

## 7) AI 對戰架構（Headless Env / Replay / 自對戰）

### 7.1 Action Space（離散）
| Action | 意義 |
|---|---|
| 0 | NOOP |
| 1 | LEFT |
| 2 | RIGHT |
| 3 | JUMP |
| 4 | ATTACK |

### 7.2 game/env/ftg_env.py（接口雛形）
```python
from dataclasses import dataclass

@dataclass
class StepResult:
    obs: dict
    reward_p1: float
    reward_p2: float
    done: bool
    info: dict

class FTGEnv:
    # Headless environment:
    # - 不 render
    # - 每 step = 1 frame
    # - 可 deterministic (seed + fixed update)
    def __init__(self, game_factory):
        self.game = game_factory(headless=True)

    def reset(self, seed: int = 0) -> dict:
        self.game.restart_with_seed(seed)
        return self._obs()

    def step(self, action_p1: int, action_p2: int) -> StepResult:
        self.game.apply_action(self.game.p1, action_p1)
        self.game.apply_action(self.game.p2, action_p2)
        self.game.step_one_frame()

        obs = self._obs()
        done = self.game.match.winner is not None

        # reward: 差分血量（入門很好用）
        r1 = (self.game.p2_hp_prev - self.game.p2.hp) * 0.1
        r2 = (self.game.p1_hp_prev - self.game.p1.hp) * 0.1

        if done:
            if self.game.match.winner == "P1":
                r1 += 10.0
                r2 -= 10.0
            elif self.game.match.winner == "P2":
                r2 += 10.0
                r1 -= 10.0

        return StepResult(obs, r1, r2, done, {"winner": self.game.match.winner})

    def _obs(self) -> dict:
        p1, p2 = self.game.p1, self.game.p2
        return {
            "p1": {"x": p1.pos.x, "y": p1.pos.y, "vx": p1.vel.x, "vy": p1.vel.y, "hp": p1.hp, "state": p1.state.name, "facing": p1.facing},
            "p2": {"x": p2.pos.x, "y": p2.pos.y, "vx": p2.vel.x, "vy": p2.vel.y, "hp": p2.hp, "state": p2.state.name, "facing": p2.facing},
        }
```

### 7.3 Replay（只記錄 input）
Replay 檔只需要：
- seed
- 每 frame 的 `(action_p1, action_p2)`

好處：
- 檔案極小
- 可 100% 重播（只要 deterministic）

---

## 8) 下一步擴充（你最常會加的）

### 8.1 攻擊資料 JSON 化（真 FTG 都會做）
```json
{
  "light": {
    "startup": 6, "active": 4, "recovery": 10, "damage": 10,
    "knockback_x": 320, "hitbox_w": 70, "hitbox_h": 40,
    "hitbox_offset_x": 40, "hitbox_offset_y": -70
  }
}
```

### 8.2 防重複命中 / 多段 hit
- 每次進入 ATTACK：`has_hit_this_attack = False`
- active 期間：命中一次就鎖住

### 8.3 真正 FTG 的 frame data
- block / blockstun
- pushbox（避免角色穿模）
- dash / cancel / juggle / hitstop

### 8.4 AI 進階
- Heuristic → MCTS → RL（自對戰 + Elo）
- headless batch self-play：每秒幾百局

---

## 9) 建議你下一步（如果你要我續寫）
1) 攻擊 JSON 化 + 多招（light/heavy/special）
2) Block + blockstun
3) Replay 錄影/回放
4) Game 變成可 headless 逐 frame（完善 env）
5) Self-play 腳本（輸出勝率 / 平均時間 / Elo）

---
