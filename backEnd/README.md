# ConfidenTech Backend API  

Django REST API with MongoDB integration for user authentication and management.

## Features

- User registration and authentication
- MongoDB integration for data storage
- JWT token-based authentication
- CORS support for frontend integration
- User profile management
- Login attempt tracking
- Security logging and monitoring

## Setup Instructions

### 1. Install Dependencies

```bash
cd backEnd
pip install -r requirements.txt
```

### 2. Install MongoDB using Homebrew


```
brew install mongodb-community
```

### 3. Start MongoDB

```
brew services start mongodb-community
```

### 4. Replace the MongoDB settings in settings.py

```
MONGODB_SETTINGS = {
    'host': 'mongodb://localhost:27017',
    'db': 'confidenTech',
}
```

### 5. Database Setup

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 6. Test MongoDB Connection

```bash
python manage.py test_mongodb
```

### 7. Run Development Server

```bash
python manage.py runserver
```

## API Endpoints

### Authentication

- `POST /api/users/register/` - User registration
- `POST /api/users/login/` - User login
- `POST /api/users/logout/` - User logout

### User Management

- `GET /api/users/profile/` - Get user profile
- `PUT /api/users/update/` - Update user information
- `POST /api/users/change-password/` - Change password

### Utility

- `POST /api/users/check-email/` - Check if email exists
- `GET /api/users/dashboard/` - User dashboard data
- `GET /api/users/login-history/` - Login history

## API Usage Examples

### User Registration

```bash
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "password_confirm": "securepassword123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### User Login

```bash
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### Get User Profile

```bash
curl -X GET http://localhost:8000/api/users/profile/ \
  -H "Authorization: Bearer your-jwt-token"
```

## Models

### User Model
- Custom user model with email as username
- UUID primary key
- Profile relationship
- Security tracking

### UserProfile Model
- Extended user information
- JSON preferences field
- Avatar and bio support

### LoginAttempt Model
- Security logging
- IP address tracking
- Success/failure tracking

## Security Features

- Password validation
- Login attempt tracking
- IP address logging
- Suspicious activity detection
- CORS configuration
- Session management

## MongoDB Integration

The application uses MongoDB for:
- User data storage
- Login attempt logging
- Profile information
- Application data

## Frontend Integration

The API is configured with CORS to work with:
- React frontend (localhost:3000, localhost:5173)
- Vue.js applications
- Any frontend framework

## Development

### Running Tests

```bash
python manage.py test
```

### Database Management

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database
python manage.py flush
```

### Admin Interface

Access the Django admin at `http://localhost:8000/admin/` to manage users and view login attempts.

## Production Deployment

1. Set `DEBUG=False` in settings
2. Configure proper CORS origins
3. Use environment variables for secrets
4. Set up proper MongoDB authentication
5. Configure static file serving
6. Use a production WSGI server (Gunicorn)

## Troubleshooting

### MongoDB Connection Issues
- Verify connection string
- Check network connectivity
- Ensure MongoDB cluster is accessible

### CORS Issues
- Add frontend URL to CORS_ALLOWED_ORIGINS
- Check CORS_ALLOW_CREDENTIALS setting

### Authentication Issues
- Verify JWT token configuration
- Check session settings
- Ensure proper middleware order
