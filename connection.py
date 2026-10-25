from dotenv import load_dotenv
import asyncpg
import os

load_dotenv()
pasw  = os.getenv("PASSWORD_DB")

async def connection_db():
    try:
        conn = await asyncpg.connect(
            host="localhost",
            port=5432,
            user="postgres",
            database="bot5_db",
            password=pasw
        )
        return conn
    except Exception as Error:
        print(f"Connection Error: {Error}")


async def create_table():
    try:
        conn = await connection_db()
        await conn.execute("""
        create table if not exists users(
            user_id serial primary key,
            username varchar(200),
            full_name varchar(200),
            telegram_id varchar(300),
            balance int,
            is_active boolean default true,
            created_at timestamp default now()
        );

        create table if not exists product(
            product_id serial primary key,
            name_product varchar(50),
            quantity int,
            low_stock_threshold int
        );
   
        create table if not exists stock_movements(
            movement_id serial primary key,
            product_id int references product(product_id),
            change int,
            reason varchar(20),
            created_at timestamp default now()
        );        
                     """)
        print("Table created")
    except Exception as Error:
        print(f"Create Error: {Error}")
    finally:
        await conn.close()