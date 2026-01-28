# StickFTG - Python 2D Fighting Game

[English](#english) | [中文說明 (Chinese)](#中文說明-chinese)

---

<a name="english"></a>
## 🇬🇧 English

A minimal 2D fighting game prototype developed in Python using `pygame`.
The project follows a clean **MVCS (Model-View-Controller-Service)** architecture, designed to be scalable and easy to understand for developers interested in fighting game development or reinforcement learning environments.

### 📂 Project Architecture

The project is structured into distinct layers to separate concerns:

```
stickftg/
├── main.py                 # Entry point
└── game/
    ├── core/               # Core game loop and configuration
    │   ├── game.py         # Main Game class (State Management)
    │   └── config.py       # Game settings
    ├── models/             # Data structures (State)
    │   ├── fighter.py      # Player attributes (HP, Pos, Vel)
    │   └── hitbox.py       # Attack definitions (Frame data)
    ├── views/              # Rendering logic (Pure visual)
    │   └── stickman_drawer.py # Procedural stickman animation
    ├── controllers/        # Input handling
    │   └── input_controller.py # Keyboard -> Fighter State
    ├── services/           # Game Logic (Stateless logic)
    │   ├── combat_service.py   # Hit detection & Damage calculation
    │   └── physics_service.py  # Gravity & Movement physics
    └─ env/                 # RL Interface
        └── ftg_env.py      # Gym-like environment for AI training
```

### ⚔️ Combat Mechanics

StickFTG uses a classic **Frame Data** system found in traditional fighting games:

1.  **Hitboxes**:
    *   Defined in `AttackFrame`.
    *   **Startup**: Frames before the hitbox becomes active.
    *   **Active**: Frames where the hitbox can deal damage.
    *   **Recovery**: Frames where the player is vulnerable and cannot act.
    *   Logic: **AABB (Axis-Aligned Bounding Box)** collision checks overlap between the Attacker's Hitbox and the Defender's Hurtbox (Body).

2.  **State Machine**:
    *   Fighters switch between states: `IDLE`, `MOVE`, `JUMP`, `ATTACK`, `HITSTUN`, `BLOCK`, `BLOCK_STUN`.
    *   Input processing is locked during committed states (like Attack Active/Recovery or Hitstun).

3.  **One-Button Combat**:
    *   Designed for simplicity.
    *   Key `J` (P1) or `Num 1` (P2) triggers a fast Punch.
    *   Current build focuses on neutral game and spacing.

### ⚠️ Current Limitations & Future Work

This is a prototype and has several areas open for contribution:

1.  **Limited Moveset**:
    *   Currently reverted to a **Single Punch** mechanic.
    *   *Goal*: Re-implement a stable Combo System (Punch -> Kick -> Smash) or directional attacks.
2.  **Input Handling**:
    *   No **Input Buffer**: Inputs must be precise. Mash-unfriendly.
    *   *Goal*: Add a 5-10 frame input buffer for smoother controls.
3.  **Physics Polish**:
    *   Gravity and friction are basic.
    *   *Goal*: Implement momentum preservation, aerial drift, and corner pushback.
4.  **Visual Feedback**:
    *   No Hitstop (Pause on hit) or Screen Shake.
    *   *Goal*: Add visual flare (particles, hit sparks) and audio cues (SFX).

### 🚀 Getting Started

1.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run the game**:
    ```bash
    python main.py
    ```
3.  **Controls**:
    *   **P1**: WASD to move, J to Attack, S to Block.
    *   **P2**: Arrow Keys to move, Num 1 to Attack, Down to Block.

---

<a name="中文說明-chinese"></a>
## 🇹🇼 中文說明 (Chinese)

這是一個使用 Python `pygame` 開發的極簡 2D 格鬥遊戲原型。
專案採用清晰的 **MVCS (Model-View-Controller-Service)** 架構，適合對格鬥遊戲開發或強化學習環境 (RL Environments) 感興趣的開發者參考與擴充。

### 📂 專案架構

程式碼結構分層明確，便於維護與理解：

```
stickftg/
├── main.py                 # 遊戲入口點 (Entry Point)
└── game/
    ├── core/               # 核心循環與設定
    │   ├── game.py         # 主遊戲類別 (管理狀態)
    │   └── config.py       # 遊戲參數設定
    ├── models/             # 資料結構 (State)
    │   ├── fighter.py      # 角色屬性 (血量, 位置, 速度)
    │   └── hitbox.py       # 攻擊判定定義 (Frame data)
    ├── views/              # 渲染邏輯 (純視覺)
    │   └── stickman_drawer.py # 火柴人程序化動畫繪製
    ├── controllers/        # 輸入控制
    │   └── input_controller.py # 鍵盤輸入 -> 轉換為角色狀態
    ├── services/           # 遊戲邏輯 (無狀態邏輯)
    │   ├── combat_service.py   # 命中偵測與傷害計算
    │   └── physics_service.py  # 重力與移動物理運算
    └─ env/                 # 強化學習介面
        └── ftg_env.py      # 類似 OpenAI Gym 的訓練環境
```

### ⚔️ 戰鬥機制 (Combat Mechanics)

StickFTG 採用傳統格鬥遊戲的 **幀數表 (Frame Data)** 系統：

1.  **攻擊判定 (Hitboxes)**:
    *   定義於 `AttackFrame` 中。
    *   **發生 (Startup)**: 攻擊判定出現前的準備幀數。
    *   **持續 (Active)**: 攻擊判定存在且可造成傷害的幀數。
    *   **硬直 (Recovery)**: 攻擊結束後的收招動作，此時角色脆弱且無法行動。
    *   **判定邏輯**: 使用 **AABB (Axis-Aligned Bounding Box)** 矩形碰撞，檢測攻擊者的 Hitbox 是否重疊防禦者的 Hurtbox (身體)。

2.  **狀態機 (State Machine)**:
    *   角色狀態切換：`IDLE` (待機), `MOVE` (移動), `JUMP` (跳躍), `ATTACK` (攻擊), `HITSTUN` (受擊硬直), `BLOCK` (防禦), `BLOCK_STUN` (防禦硬直)。
    *   在特定狀態下 (如攻擊中或受擊中)，輸入將被鎖定。

3.  **單鍵戰鬥 (One-Button Combat)**:
    *   設計極簡化，降低上手難度。
    *   P1 按 `J` / P2 按 `Num 1` 即可發動快速刺拳。
    *   目前版本著重於立回 (Spacing) 與抓時間差。

### ⚠️ 目前缺點與待優化項目 (Current Limitations)

這是一個原型專案，仍有許多可改進與擴充的空間，歡迎協作修繕：

1.  **招式單一 (Limited Moveset)**:
    *   目前已回退到單一的「刺拳」機制。
    *   *目標*: 重新實作穩定的連招系統 (拳 -> 踢 -> 重擊) 或加入方向鍵招式 (如前+攻擊)。
2.  **輸入優化 (Input Handling)**:
    *   缺乏 **輸入緩衝 (Input Buffer)**：按鍵必須非常精準，連打容易沒反應 (吃指令)。
    *   *目標*: 加入 5-10 幀的輸入緩衝，讓操作手感更滑順。
3.  **物理手感 (Physics Polish)**:
    *   目前的重力與摩擦力較為基礎。
    *   *目標*: 實作慣性保留 (Momentum)、空中轉向限制、以及角落推擠判定。
4.  **視覺反饋 (Visual Feedback)**:
    *   缺乏 **打擊停頓 (Hitstop)** 與畫面震動，打擊感較弱。
    *   *目標*: 加入打擊特效 (粒子、火花) 與音效 (SFX)。
5.  **AI 智能**:
    *   目前 P2 AI 僅為簡單隨機行動。
    *   *目標*: 實作決策樹 AI 或利用 `game/env` 訓練強化學習模型。

### 🚀 快速開始 (Getting Started)

1.  **安裝依賴**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **執行遊戲**:
    ```bash
    python main.py
    ```
3.  **操作說明**:
    *   **P1 (左側)**: `WASD` 移動, `J` 攻擊, `S` 防禦。
    *   **P2 (右側)**: `方向鍵` 移動, `Num 1` 攻擊, `↓` 防禦。
