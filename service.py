from connection import *

async def create_user(username, full_name, telegram_id):
    try:
        conn = await connection_db()
        await conn.execute("""
        insert into users(username, full_name, telegram_id) Values
        ($1, $2, $3) 
                     """, username, full_name,str(telegram_id))
    except Exception as Error:
        print(f"Create user Error: {Error}")
    finally:
        await conn.close()
        
        
async def get_user_by_id(telegram_id):
    try:
        conn = await connection_db()
        user = await conn.fetchrow("""
        select * from users where telegram_id = $1
                     """, str(telegram_id))
        return user
    except Exception as Error:
        print(f"Get user by id Error: {Error}")
    finally:
        await conn.close()
        
        
async def create_product(name_product: str, quantity: int, low_stock_threshold: int):
    conn = None
    try:
        conn = await connection_db()
        product = await conn.execute("""
        insert into product( name_product, quantity, low_stock_threshold)values ($1, $2, $3)
                    """, name_product, quantity, low_stock_threshold)
        return product
    except Exception as Error:
        print(f"Create product Error: {Error}")
    finally:
        if conn is not None:
            await conn.close()


async def get_product_by_id(product_id: int):
    conn = None
    try:
        conn = await connection_db()
        product = await conn.fetchrow("""
        select * from product where product_id = $1
                    """, product_id)
        return product
    except Exception as Error:
        print(f"Get product by id Error: {Error}")
    finally:
        if conn is not None: 
            await conn.close()


async def get_all_products():
    conn = None
    try:
        conn = await connection_db()
        products = await conn.fetch("""
            SELECT * FROM product
        """)
        return products
    except Exception as Error:
        print(f"Get all products Error: {Error}")
    finally:
        if conn is not None:
            await conn.close()



async def restock_product(product_id: int, quantity: int):
    conn = None
    try:
        conn = await connection_db()

        product = await conn.fetchrow("""
            SELECT * FROM product WHERE product_id = $1
        """, product_id)
        if product is None:
            return "not_found"
        await conn.execute("""
            UPDATE product
            SET quantity = quantity + $1 WHERE product_id = $2
        """, quantity, product_id)
        await conn.execute("""
            INSERT INTO stock_movements(product_id, change, reason)VALUES ($1, $2, $3)
        """, product_id, quantity, "restock")
        return "success"
    except Exception as Error:
        print(f"Restock product Error: {Error}")
        return "error"
    finally:
        if conn is not None:
            await conn.close()


async def sell_product(product_id: int, quantity: int):
    conn = None
    try:
        conn = await connection_db()
        product = await conn.fetchrow("""
            SELECT * FROM product WHERE product_id = $1
        """, product_id)
        if product is None:
            return "not_found"
        if product["quantity"] < quantity:
            return "not_enough"
        result = await conn.execute("""
            UPDATE product
            SET quantity = quantity - $1 WHERE product_id = $2 AND quantity >= $1
        """, quantity, product_id)
        if result == "UPDATE 0":
            return "not_enough"
        await conn.execute("""
            INSERT INTO stock_movements(product_id, change, reason)VALUES ($1, $2, $3)
        """, product_id, -quantity, "sell")
        return "success"
    except Exception as Error:
        print(f"Sell product Error: {Error}")
        return "error"
    finally:
        if conn is not None:
            await conn.close()


async def get_low_stock():
    conn = None
    try:
        conn = await connection_db()
        products = await conn.fetch("""
            SELECT * FROM product WHERE quantity < low_stock_threshold
        """)
        return products
    except Exception as Error:
        print(f"Get low stock Error: {Error}")
    finally:
        if conn is not None:
            await conn.close()

