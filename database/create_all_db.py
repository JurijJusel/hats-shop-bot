from create_database_user import init_users_database
from create_shop_database import init_database

def main():
    init_database()
    init_users_database()

if __name__ == "__main__":
    main()
