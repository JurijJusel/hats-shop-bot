# 🧢 Hats Shop Telegram Bot

A fully-featured Telegram bot designed for hat e-commerce with comprehensive admin panel.
This bot provides a complete shopping experience allowing users to browse hats,
manage their cart, process payments, and track orders, while administrators have
full control over products, users, and order management.

Built with Python and the `python-telegram-bot` library, this solution offers a modern,
scalable approach to running an online hat store directly through Telegram,
making it perfect for businesses looking to leverage the platform's massive user base and convenient messaging interface.

## 🚀 Features

### For Users
- 🧢 **Hat Catalog** - Browse and select hats
- 🛒 **Shopping Cart** - Add/remove items
- 💳 **Payment** - Order payment processing
- 📦 **Order History** - View your orders
- ❓ **Help** - Bot information

### For Admins
- 👥 **User Management** - Block/unblock users
- 📊 **Order Management** - View and change order status
- 🧢 **Product Management** - Add, edit, remove hats
- 📈 **Statistics** - User and order information

## 📋 Requirements

- Python 3.12+
- Telegram Bot Token
- SQLite database

## 🛠️ Installation

1. **Clone repository**
   ```bash
   git clone <repository-url>
   cd hats-shop-bot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   # or using uv
   uv sync
   ```

4. **Configure .env file**
   ```env
   BOT_TOKEN=your_telegram_bot_token
   ```

5. **Run the bot**
   ```bash
   python bot.py
   ```

## 📁 Structure

```
hats-shop-bot/
├── bot.py              # Main bot file
├── admin/              # Admin functions
├── handlers/           # Handlers
├── users/              # User functions
├── database/           # Database management
├── logging_err/        # Logging configuration
├── constants.py        # Constants
└── .env               # Environment variables
```

## 🎮 Commands

### User Commands
- `/start` - Start working with the bot
- `/help` - Help
- `/klausimai` - FAQ
- `/my_orders` - My orders

### Admin Commands
- `/info` - System information
- `/show_users` - Show users
- `/ban_user <user_id>` - Block user
- `/unban_user <user_id>` - Unblock user
- `/show_hats` - Show hats
- `/show_orders` - Show orders
- `/show_orders_10` - Last 10 orders
- `/show_orders_status` - Order statuses

## 🔧 Configuration

The bot uses SQLite databases:
- `shop.db` - Store data
- `users_info.db` - User information
- `banned_users.db` - Blocked users

## 📝 Logging

The bot has an advanced logging system that saves information to the `logging_err/` directory.

## 🤗 Authors

Created with ❤️ using the `python-telegram-bot` library.

## 📄 License

MIT License
