# Fencing FTG (Épée)

> Please select your language / 請選擇語言

<details>
<summary><strong>🇺🇸 English Version (Click to Expand)</strong></summary>

A distance-based Fighting Game (FTG) focused on **Épée Fencing**, integrated with a Gym environment to support Reinforcement Learning (RL).

## 📁 Project Architecture

This project uses **MVCS (Model-View-Controller-Service)** architecture and **WebSocket** for real-time communication.

```text
fencing-ftg/
├── app/
│   ├── main.py          # FastAPI Entry Point
│   ├── ws.py            # WebSocket Endpoint & Router
│   └── game/
│       ├── engine.py    # Game Engine (FSM, Hit Detection, Physics)
│       ├── models.py    # Pydantic Models & Enums (State, Config)
│       ├── service.py   # Game Service (Loop, AI Integration)
│       └── ai.py        # Simple Rule-based AI
├── static/
│   └── index.html       # Frontend Client (Canvas, UI)
├── docker/              # Docker Configuration
└── requirements.txt
```

## 🎮 How to Play

The goal is to score **5 points** first to win.
This is not a combo-based fighting game, but a game about **Spacing** and **Timing**.

### Controls

| Action | Player 1 (Left) | Player 2 (Right) |
| :--- | :--- | :--- |
| **Forward** | `→` (Right Arrow) | `←` (Left Arrow) **Note: Inverted** |
| **Backward** | `←` (Left Arrow) | `→` (Right Arrow) |
| **Thrust** | `Z` | `Z` |
| **Lunge** | `X` | `X` |

> ⚠️ **Important (PvP 2P Controls)**:
> In PvP mode, Player 2's "Forward" (facing opponent) is moving to the **Left**, so the key is **Left Arrow (`←`)**.
> Pressing **Right Arrow (`→`)** will make Player 2 move Backward.

### Game Modes

1.  **PvP (Player vs Player)**:
    *   Two-player mode.
    *   Open two browser tabs/windows to control P1 and P2 respectively.
    *   Input controls are independent.
2.  **vs AI (Player vs Environment)**:
    *   Single-player mode.
    *   Player 2 is controlled by a simple AI.
    *   AI automatically maintains distance and attempts attacks.
    *   **Note**: Since Épée Fencing involves linear (1D) movement, the AI trains very effectively and can become a strong opponent quickly.

## ⚔️ Mechanics

*   **Distance Model**:
    *   **Optimal Range**: ~2.0m to 2.5m. Highest hit probability.
    *   **Too Far**: Attacks will miss.
    *   **Too Close**: (Pushing not implemented yet) Hits connect but you are vulnerable to counter-hits.
*   **Hit Detection**:
    *   A hit is registered when a fencer is in `ATTACK_ACTIVE` state (Thrust/Lunge active frames) and the opponent is within range.
    *   **Freeze Frame**: On hit, the game freezes for 1 second to confirm the score, then positions are reset.
*   **Double Touch**:
    *   If both fencers hit each other within a very short window, both score a point.

## 🚀 Run

### Direct Run
```bash
# Activate environment
activate env

# Start server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Docker Run
```bash
docker-compose up --build
```

Open browser to: `http://localhost:8000/`

</details>

<details open>
<summary><strong>🇹🇼 中文版 (點擊收合)</strong></summary>

一個以 **西洋劍（重劍 Épée）** 為核心的距離壓制型格鬥遊戲 (FTG)，整合了 Gym 環境以支援強化學習 (RL) 訓練。

## 📁 專案架構 (Project Architecture)

本專案採用 **MVCS (Model-View-Controller-Service)** 架構與 **WebSocket** 進行實時通訊。

```text
fencing-ftg/
├── app/
│   ├── main.py          # FastAPI Entry Point
│   ├── ws.py            # WebSocket Endpoint & Router
│   └── game/
│       ├── engine.py    # Game Engine (FSM, Hit Detection, Physics)
│       ├── models.py    # Pydantic Models & Enums (State, Config)
│       ├── service.py   # Game Service (Loop, AI Integration)
│       └── ai.py        # Simple Rule-based AI
├── static/
│   └── index.html       # Frontend Client (Canvas, UI)
├── docker/              # Docker Configuration
└── requirements.txt
```

## 🎮 玩法說明 (How to Play)

遊戲目標是先獲得 **5分** 即可獲勝。
這不是傳統的連招格鬥，而是關於 **距離控制 (Spacing)** 與 **時機 (Timing)** 的遊戲。

### 操作方式 (Controls)

| 動作 | Player 1 (左側) | Player 2 (右側) |
| :--- | :--- | :--- |
| **前進 (Forward)** | `→` (Right Arrow) | `←` (Left Arrow) **注意：方向相反** |
| **後退 (Backward)** | `←` (Left Arrow) | `→` (Right Arrow) |
| **刺擊 (Thrust)** | `Z` | `Z` |
| **弓步 (Lunge)** | `X` | `X` |

> ⚠️ **特別注意 (PvP 2P Controls)**：
> 在 PvP 模式下，Player 2 的前進方向（面向對手）是向 **左** 移動，因此對應的按鍵是 **左方向鍵 (`←`)**。
> 按下 **右方向鍵 (`→`)** 會使 Player 2 後退。

### 遊戲模式 (Game Modes)

1.  **PvP (Player vs Player)**：
    *   雙人對戰模式。
    *   開啟兩個瀏覽器分頁，分別控制 P1 與 P2。
    *   雙方按鍵操作獨立。
2.  **vs AI (Player vs Environment)**：
    *   單人模式。
    *   Player 2 由電腦 AI 自動控制。
    *   AI 會根據距離自動前後移動並嘗試攻擊。
    *   **備註**：由於西洋劍是直線（1D）運動，AI 訓練效率極高，能夠很快學會強大的距離控制與攻擊決策。

## ⚔️ 判定機制 (Mechanics)

*   **距離模型**：
    *   **最佳距離 (Optimal Range)**：約 2.0m ~ 2.5m，最容易命中。
    *   **過遠**：攻擊無法觸及。
    *   **過近**：(尚未實裝推擠) 目前仍可命中，但通常會先被對方擊中。
*   **擊中判定 (Hit Detection)**：
    *   當角色處於 `ATTACK_ACTIVE` 狀態（刺擊或弓步的攻擊幀）且對手在攻擊範圍內時，判定為命中。
    *   **定格 (Freeze Frame)**：命中時遊戲畫面會短暫定格 1 秒，以呈現打擊感與確認得分，隨後重置位置。
*   **雙殺 (Double Touch)**：
    *   若雙方在極短時間內同時擊中對方，則同時得分。

## 🚀 執行方式 (Run)

### 一般執行
```bash
# 進入虛擬環境
activate env

# 啟動伺服器
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Docker 執行
```bash
docker-compose up --build
```

開啟瀏覽器前往：`http://localhost:8000/`

</details>
