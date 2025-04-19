# Core Payment Processing System

This is the core module for the cashless payment processing system. It handles all backend operations, database management, and payment processing.

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Unix/macOS
# or
.\venv\Scripts\activate  # On Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a .env file in the core directory with the following variables:
```
DEBUG=True
SECRET_KEY=your-secret-key
DB_NAME=payment_system
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## Features

- Secure payment processing
- QR code generation and validation
- User balance management
- Transaction history
- API endpoints for mobile apps
- Admin dashboard integration
- Database backup system 