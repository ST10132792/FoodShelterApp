# Food Inventory Management System

A Flask-based web application for managing food inventory, meal planning, and budgeting.

## Prerequisites

- Python 3.8+
- PostgreSQL database
- SMTP access (Gmail account for email functionality)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following variables:
```plaintext
FLASK_SECRET_KEY=your_secret_key_here
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
MAIL_USERNAME=your_gmail_address
MAIL_PASSWORD=your_gmail_app_password
```

Note: For Gmail, you'll need to use an App Password rather than your regular password. You can generate this in your Google Account settings.

## Database Setup

1. Create a PostgreSQL database
2. Update the DATABASE_URL in your .env file with your database credentials
3. The tables will be automatically created when you run the application

## Running the Application

1. Make sure your virtual environment is activated
2. Run the Flask application:
```bash
python app.py
```

3. Access the application in your web browser at:
```
http://127.0.0.1:5000
```

## Features

- User authentication and registration
- Food inventory management
- Meal planning
- Budget tracking
- Low stock alerts
- Expiration date tracking
- Email notifications

## Development

The application runs in debug mode by default. For production deployment, make sure to:
- Disable debug mode
- Use a production-grade WSGI server
- Set up proper security measures
- Configure proper logging

## Logging

The application logs are stored in `app.log`. You can monitor this file for debugging and tracking application activity.
