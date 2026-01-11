import sqlite3

DB_PATH = "shop.db"


def count_products():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_all_products():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id,
        name,
        description,
        price,
        photo_file_id,
        category,
        available,
        created_date
        FROM products
        """
    )
    products = cursor.fetchall()
    conn.close()
    return products


if __name__ == "__main__":
    print("Iš viso produktų:", count_products())
    print("Visos kepures:", get_all_products())
