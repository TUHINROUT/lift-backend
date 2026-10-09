import asyncio

from sqlalchemy import text

from app.db.database import engine


async def test_connection():
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version();"))
            print(result.scalar())

        print("✅ Database Connected Successfully!")

    except Exception as e:
        print(f"❌ Connection Failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_connection())