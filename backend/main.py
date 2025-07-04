from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.database import get_db
from backend.models import User, SingleGame, MinesGame
import random
import json
import os
from datetime import datetime
from fastapi.responses import FileResponse
import logging


logging.basicConfig(
    level=logging.INFO,  # INFO или DEBUG — для вывода разных уровней подробности
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Загрузка startXMap.json

START_X_MAP_PATH = "backend/startXMap.json"
logger.info(f"Loading startXMap.json from {START_X_MAP_PATH}")
if not os.path.exists(START_X_MAP_PATH):
    raise Exception(f"File {START_X_MAP_PATH} not found")
with open(START_X_MAP_PATH, 'r') as f:
    start_x_map = json.load(f)

# Таблица множителей для Plinko
plinko_multipliers = [0.2, 0.5, 1, 2, 5, 2, 1, 0.5, 0.2]

# Вероятности выбора корзин
plinko_bin_probabilities = {
    0: 0.25,  # 0.2x (левая)
    1: 0.10,  # 0.5x
    2: 0.075, # 1x
    3: 0.05,  # 2x
    4: 0.05,  # 5x
    5: 0.05,  # 2x
    6: 0.075, # 1x
    7: 0.10,  # 0.5x
    8: 0.25   # 0.2x (правая)
}

# Временное хранилище результатов для экспорта
plinko_results = []

# Путь для сохранения JSON-файла
PLINKO_RESULTS_PATH = "backend/plinko_results.json"

# Таблица множителей для Mines (без изменений)
mines_chances = {
    '2': [1.05, 1.15, 1.26, 1.39, 1.53, 1.7, 1.9, 2.14, 2.42, 2.77, 3.2, 3.73, 4.41, 5.29, 6.47, 8.08, 10.39, 13.86, 19.4, 29.1, 48.5, 97, 200],
    '3': [1.08, 1.24, 1.42, 1.63, 1.94, 2.28, 2.69, 3.22, 3.93, 4.85, 6.08, 7.75, 10.10, 13.12, 15.40, 22.03, 29.05, 47.98, 65.98, 93.33, 236.56, 540],
    '4': [1.15, 1.39, 1.68, 2.05, 2.53, 3.17, 4.01, 5.16, 6.74, 8.99, 11, 15, 20, 30, 45, 70, 100, 150, 300, 700, 1000],
    '5': [1.21, 1.53, 1.96, 2.53, 3.32, 4.43, 5.89, 7.65, 9.4, 13.6, 18.54, 34.09, 45.12, 67.09, 93.51, 122.02, 234.29, 545, 5590, 12940],
    '6': [1.25, 1.5, 2, 3, 4, 6, 9, 13, 18, 30, 50, 100, 150, 300, 450, 900, 1500, 3000, 10000],
    '7': [1.35, 1.9, 2.53, 3.01, 5.01, 7.25, 14.65, 23.98, 34.76, 46.46, 67.86, 90.72, 145.74, 1010, 1597, 3450, 4588, 15000],
    '8': [1.43, 2.14, 3.28, 5.16, 8.33, 13.88, 23.98, 40, 50, 100, 250, 350, 1000, 3000, 9000, 14000, 30000],
    '9': [1.51, 2.42, 3.98, 6.74, 11.8, 16.45, 28.76, 56.52, 86.22, 164.94, 190.85, 1300, 3400, 9634, 16790, 34000],
    '10': [1.62, 2.77, 4.9, 8.99, 17.16, 34.32, 72.46, 100, 300, 900, 1500, 3000, 7000, 15000, 48888],
    '11': [1.73, 3.2, 6.13, 12.26, 25.74, 35.2, 79.86, 123.09, 345, 950, 1605, 3405, 7800, 17695],
    '12': [1.86, 3.73, 7.8, 17.16, 40.04, 100.11, 271.72, 815.17, 2770, 1190, 5540, 9940, 18000],
    '13': [2.02, 4.41, 10.14, 24.79, 55.07, 125.92, 331.74, 891, 2980, 12005, 14050, 18950],
    '14': [2, 5, 10, 20, 55.55, 111.20, 166.78, 998.4, 1988.3, 3767.45, 10000],
    '15': [2.42, 6.47, 18.59, 58.43, 135.51, 295.03, 1503, 2503, 3534, 5607],
    '16': [2.69, 8.08, 26.56, 97.38, 409.02, 2050, 12950, 15600, 45000],
    '17': [3.03, 10.39, 39.84, 145.29, 554.29, 3530, 7689, 16670],
    '18': [3.46, 13.86, 63.74, 350.58, 2450, 24540, 35000],
    '19': [4.04, 19.4, 111.55, 818.03, 8590, 14000],
    '20': [4.85, 29.1, 223.1, 2450, 7000],
    '21': [6.06, 48.5, 557.75, 12270],
    '22': [8.08, 97, 2230],
    '23': [12.13, 291],
    '24': [24.25]
}

@app.get("/api/user/{user_id}/balance/")
async def get_user_balance(user_id: int, db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(User).filter(User.user_id == user_id))).scalar_one_or_none()
    if not user:
        logger.info(f"User with id:{user_id} not found, creating new user")
        user = User(user_id=user_id, balance=0.0, reg_date=datetime.utcnow())
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info(f"User with id:{user_id} created successfully")
    return {"user_id": user.user_id, "balance": user.balance, "reg_date": user.reg_date}

@app.post("/api/coin/play/")
async def play_coin_game(request: dict, db: AsyncSession = Depends(get_db)):
    user_id = request.get("user_id")
    amount = float(request.get("amount"))
    choice = request.get("choice")

    if not user_id or not amount or not choice:
        raise HTTPException(status_code=400, detail="Missing required fields")

    if choice not in ["heads", "tails"]:
        raise HTTPException(status_code=400, detail="Invalid choice. Must be 'heads' or 'tails'")

    user = (await db.execute(select(User).filter(User.user_id == user_id))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    # Set weighted probabilities: 45% for user's choice, 55% for the opposite
    options = ["heads", "tails"]
    weights = [0.4 if choice == "heads" else 0.6, 0.6 if choice == "heads" else 0.4]
    result = random.choices(options, weights=weights, k=1)[0]

    game = SingleGame(
        user_id=user_id,
        amount=amount,
        game_type="coin",
        game_value=1 if result == "heads" else 0,
        status="FINISHED",
        message_id=0,
        date=datetime.utcnow()
    )
    db.add(game)
    await db.commit()
    await db.refresh(game)

    if choice == result:
        user.balance += amount
        result_status = "won"
    else:
        user.balance -= amount
        result_status = "lost"

    await db.commit()

    return {
        "status": result_status,
        "result": result,
        "balance": user.balance,
        "amount": amount
    }

@app.post("/api/plinko/start/")
async def start_plinko_game(request: dict, db: AsyncSession = Depends(get_db)):
    user_id = request.get("user_id")
    amount = float(request.get("amount"))
    ball_count = int(request.get("ball_count", 1))
    custom_positions = request.get("custom_positions", None)  # Список заданных позиций X

    if not user_id or not amount:
        raise HTTPException(status_code=400, detail="Missing required fields")

    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")

    if custom_positions is None and ball_count not in [1, 5, 10]:
        raise HTTPException(status_code=400, detail="Ball count must be 1, 5, or 10")

    user = (await db.execute(select(User).filter(User.user_id == user_id))).scalar_one_or_none()
    if not user:
        user = User(user_id=user_id, balance=0.0, reg_date=datetime.utcnow())
        db.add(user)
        await db.commit()
        await db.refresh(user)

    # Если используются custom_positions, ball_count равен их количеству
    if custom_positions is not None:
        ball_count = len(custom_positions)
        # Проверяем, что все позиции в диапазоне 80–160
        for x in custom_positions:
            if not (80 <= float(x) <= 160):
                raise HTTPException(status_code=400, detail="All custom positions must be between 80 and 160")

    total_amount = amount * ball_count
    if user.balance < total_amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    user.balance -= total_amount
    games = []
    start_positions = []

    for i in range(ball_count):
        if custom_positions is not None:
            start_x = float(custom_positions[i])
            # Для custom_positions выбираем ближайшую корзину для game_value
            bin_index = random.randint(0, len(plinko_multipliers) - 1)  # Временный выбор
        else:
            # Выбираем корзину с заданными вероятностями
            bin_index = random.choices(
                list(plinko_bin_probabilities.keys()),
                weights=list(plinko_bin_probabilities.values()),
                k=1
            )[0]
            bin_key = str(bin_index)
            if bin_key not in start_x_map or not start_x_map[bin_key]:
                raise HTTPException(status_code=500, detail=f"No start positions for bin {bin_index}")
            start_x = random.choice(start_x_map[bin_key])

        game = SingleGame(
            user_id=user_id,
            amount=amount,
            game_type="plinko",
            game_value=bin_index,
            status="IN_PROGRESS",
            message_id=0,
            date=datetime.utcnow()
        )
        db.add(game)
        games.append(game)
        start_positions.append(start_x)

    await db.commit()

    # Обновляем игры для получения их ID
    game_ids = []
    for game in games:
        await db.refresh(game)
        game_ids.append(game.id)

    for position in start_positions:
        print(f"Start position: {position}")

    return {
        "status": "started",
        "balance": user.balance,
        "games": [
            {"game_id": game_id, "start_x": start_x}
            for game_id, start_x in zip(game_ids, start_positions)
        ]
    }

@app.post("/api/plinko/result/")
async def plinko_result(request: dict, db: AsyncSession = Depends(get_db)):
    game_id = request.get("game_id")
    bin_index = request.get("bin_index")
    start_x = request.get("start_x")  # Добавляем start_x для записи в результаты
    amount = request.get("amount")

    if not game_id or bin_index is None or start_x is None or amount is None:
        raise HTTPException(status_code=400, detail="Missing required fields")

    game = (await db.execute(
        select(SingleGame).filter(SingleGame.id == game_id, SingleGame.game_type == "plinko", SingleGame.status == "IN_PROGRESS")
    )).scalar_one_or_none()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found or not in progress")

    user = (await db.execute(select(User).filter(User.user_id == game.user_id))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if bin_index < 0 or bin_index >= len(plinko_multipliers):
        raise HTTPException(status_code=400, detail="Invalid bin index")

    multiplier = plinko_multipliers[bin_index]
    prize = game.amount * multiplier

    game.game_value = bin_index
    game.status = "FINISHED"
    user.balance += prize

    # Сохраняем результат для экспорта
    plinko_results.append({
        "start_x": start_x,
        "bin_index": bin_index,
        "multiplier": multiplier,
        "amount": amount,
        "prize": prize
    })

    await db.commit()

    return {
        "status": "finished",
        "multiplier": multiplier,
        "prize": prize,
        "balance": user.balance
    }

@app.get("/api/plinko/export/")
async def export_plinko_results():
    # Сохраняем результаты в JSON-файл
    results_data = {"results": plinko_results}
    with open(PLINKO_RESULTS_PATH, 'w') as f:
        json.dump(results_data, f, indent=2)

    # Возвращаем файл для скачивания
    return FileResponse(
        PLINKO_RESULTS_PATH,
        media_type='application/json',
        filename="plinko_results.json"
    )

@app.post("/api/mines/start/")
async def start_mines_game(request: dict, db: AsyncSession = Depends(get_db)):
    user_id = request.get("user_id")
    amount = float(request.get("amount"))
    mines_count = int(request.get("mines_count"))

    if not user_id or not amount or not mines_count:
        raise HTTPException(status_code=400, detail="Missing required fields")

    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")

    if mines_count < 2 or mines_count > 24:
        raise HTTPException(status_code=400, detail="Mines count must be between 2 and 24")

    user = (await db.execute(select(User).filter(User.user_id == user_id))).scalar_one_or_none()
    if not user:
        user = User(user_id=user_id, balance=0.0, reg_date=datetime.utcnow())
        db.add(user)
        await db.commit()
        await db.refresh(user)

    if user.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    user.balance -= amount
    await db.commit()

    total_cells = 25
    if mines_count >= total_cells:
        raise HTTPException(status_code=400, detail="Mines count must be less than total cells (25)")

    mines_array = random.sample(range(total_cells), mines_count)

    mines_game = MinesGame(
        user_id=user_id,
        amount=amount,
        game_type="mines",
        game_value=0,
        status="IN_PROGRESS",
        message_id=0,
        date=datetime.utcnow(),
        current_prize=amount,
        mines_array=mines_array,
        clicked_array=[]
    )
    db.add(mines_game)
    await db.commit()
    await db.refresh(mines_game)

    return {
        "status": "started",
        "balance": user.balance,
        "game_id": mines_game.id
    }

@app.post("/api/mines/click/")
async def click_mines_cell(request: dict, db: AsyncSession = Depends(get_db)):
    game_id = request.get("game_id")
    cell_index = request.get("cell_index")

    if not game_id or cell_index is None:
        raise HTTPException(status_code=400, detail="Missing required fields")

    mines_game = (await db.execute(
        select(MinesGame).filter(MinesGame.id == game_id, MinesGame.game_type == "mines",
                                 MinesGame.status == "IN_PROGRESS")
    )).scalar_one_or_none()
    if not mines_game:
        raise HTTPException(status_code=404, detail="Game not found or not in progress")

    user = (await db.execute(select(User).filter(User.user_id == mines_game.user_id))).scalar_one_or_none()

    clicked_array = mines_game.clicked_array
    mines_array = mines_game.mines_array

    if cell_index in clicked_array:
        raise HTTPException(status_code=400, detail="Cell already clicked")

    clicked_array = clicked_array + [cell_index]
    mines_game.clicked_array = clicked_array

    if cell_index in mines_array:
        mines_game.status = "FINISHED"
        mines_game.game_value = len(clicked_array) - 1
        mines_game.current_prize = 0
        await db.commit()
        return {
            "status": "lost",
            "hit_mine": True,
            "clicked_array": clicked_array,
            "mines_array": mines_array,
            "current_prize": 0,
            "balance": user.balance
        }

    mines_count = len(mines_array)
    mines_count_str = str(mines_count)
    click_index = len(clicked_array) - 1
    if mines_count_str in mines_chances and click_index < len(mines_chances[mines_count_str]):
        multiplier = mines_chances[mines_count_str][click_index]
    else:
        multiplier = 1.0

    mines_game.current_prize = mines_game.amount * multiplier

    remaining_cells = 25 - len(mines_array)
    if len(clicked_array) == remaining_cells:
        mines_game.status = "FINISHED"
        mines_game.game_value = len(clicked_array)
        user.balance += mines_game.current_prize
        await db.commit()
        return {
            "status": "won",
            "hit_mine": False,
            "clicked_array": clicked_array,
            "current_prize": mines_game.current_prize,
            "balance": user.balance
        }

    await db.commit()
    return {
        "status": "in_progress",
        "hit_mine": False,
        "clicked_array": clicked_array,
        "current_prize": mines_game.current_prize,
        "balance": user.balance
    }

@app.post("/api/mines/cashout/")
async def cashout_mines_game(request: dict, db: AsyncSession = Depends(get_db)):
    game_id = request.get("game_id")

    if not game_id:
        raise HTTPException(status_code=400, detail="Missing required fields")

    mines_game = (await db.execute(
        select(MinesGame).filter(MinesGame.id == game_id, MinesGame.game_type == "mines",
                                 MinesGame.status == "IN_PROGRESS")
    )).scalar_one_or_none()
    if not mines_game:
        raise HTTPException(status_code=404, detail="Game not found or not in progress")

    user = (await db.execute(select(User).filter(User.user_id == mines_game.user_id))).scalar_one_or_none()
    user.balance += mines_game.current_prize

    mines_game.status = "FINISHED"
    mines_game.game_value = len(mines_game.clicked_array)
    await db.commit()

    return {
        "status": "won",
        "current_prize": mines_game.current_prize,
        "balance": user.balance
    }