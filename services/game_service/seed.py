import asyncio
import csv
from pathlib import Path

from sqlalchemy import select, func

from services.game_service.app.infrastructure.db.models import Catastrophe, BunkerElement, Attribute, ActionCard
from services.game_service.app.infrastructure.db.session import async_session_maker


SEED_CONFIG = {
    Catastrophe: 'data/catastrophes.csv',
    BunkerElement: 'data/bunker_elements.csv',
    Attribute: 'data/attributes.csv',
    ActionCard: 'data/action_cards.csv',
}

async def seed_model(session, model_class, csv_path: str):
    result = await session.execute(select(func.count()).select_from(model_class))
    existing_count = result.scalar()
    
    if existing_count > 0:
        print(f"⚠ {model_class.__name__}: уже есть {existing_count} записей, пропускаем")
        return 0
    
    file_path = Path(csv_path)
    if not file_path.exists():
        print(f"⚠ Файл {csv_path} не найден, пропускаем")
        return 0
    
    with open(file_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        
        records = []
        for row in csv_reader:
            record = model_class(**row)
            records.append(record)
        
        if records:
            session.add_all(records)
            await session.commit()
        
        return len(records)

async def seed_data():
    async with async_session_maker() as session:
        try:
            total_records = 0
            
            for model_class, csv_path in SEED_CONFIG.items():
                model_name = model_class.__name__
                print(f"Загружаем {model_name}...")
                
                count = await seed_model(session, model_class, csv_path)
                total_records += count
                
                print(f"✓ {model_name}: загружено {count} записей")
            
            print(f"\n✓ Всего загружено {total_records} записей")
        
        except Exception as e:
            await session.rollback()
            print(f"✗ Ошибка при загрузке данных: {e}")
            raise

if __name__ == "__main__":
    print("Начинаем загрузку данных...")
    asyncio.run(seed_data())
    print("\nГотово!")