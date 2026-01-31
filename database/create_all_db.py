from create_database_user import init_users_database
from create_shop_database import init_database
from create_db_ban_users import init_users_ban_database

def main():
    init_database()
    init_users_database()
    init_users_ban_database()

if __name__ == "__main__":
    main()
