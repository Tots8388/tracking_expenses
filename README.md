# Expense Tracker Application

A web-based expense tracking app built with Django and MySQL that helps users manage and analyze their income and expenses.

## Features
- User registration and login
- Add, edit, and delete income/expense transactions
- Categorize expenses (food, rent, transport, etc.)
- Monthly and yearly summaries
- Pie and bar charts for spending visualization
- CSV export

## Tech Stack
- **Backend:** Python, Django, Django REST Framework
- **Database:** MySQL
- **Frontend:** HTML, CSS, JavaScript, Bootstrap 5, Chart.js

## Setup Instructions

### 1. Clone the repository
git clone https://github.com/Tots8388/tracking_expenses.git
cd tracking_expenses

### 2. Install dependencies
pip install -r requirements.txt

### 3. Configure the database
In settings.py, update the DATABASES section with your MySQL credentials.

### 4. Run migrations
python manage.py makemigrations
python manage.py migrate

### 5. Create superuser
python manage.py createsuperuser

### 6. Run the server
python manage.py runserver

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/registration/ | Register a new user |
| POST | /api/auth/login/ | Login |
| GET/POST | /api/transactions/ | List or create transactions |
| GET/PUT/DELETE | /api/transactions/{id}/ | Get, update or delete a transaction |
| GET | /api/summary/ | Get income/expense summary |
| GET/POST | /api/categories/ | List or create categories |

## Author
Joshua Kimutai