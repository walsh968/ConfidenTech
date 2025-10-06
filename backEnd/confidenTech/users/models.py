from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import EmailValidator
import uuid
from datetime import datetime
from mongoengine import connect, Document, StringField, EmailField, BooleanField, DateTimeField, UUIDField
from django.conf import settings

# MongoDB Connection
try:
    connect(
        db=settings.MONGODB_SETTINGS['db'],
        host=settings.MONGODB_SETTINGS['host']
    )
except Exception as e:
    print(f"MongoDB connection error: {e}")


class MongoUser(Document):
    """
    MongoDB User model for data storage
    """
    user_id = UUIDField(primary_key=True)
    email = EmailField(required=True, unique=True)
    first_name = StringField(max_length=100)
    last_name = StringField(max_length=100)
    is_active = BooleanField(default=True)
    is_verified = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    last_login = DateTimeField()
    
    meta = {
        'collection': 'users',
        'indexes': ['email']
    }
    
    def __str__(self):
        return self.email


class MongoUserProfile(Document):
    """
    MongoDB User Profile model
    """
    user_id = UUIDField(required=True)
    phone_number = StringField(max_length=20)
    bio = StringField()
    avatar = StringField()
    preferences = StringField()
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    
    meta = {
        'collection': 'user_profiles',
        'indexes': ['user_id']
    }


class MongoLoginAttempt(Document):
    """
    MongoDB Login Attempt model
    """
    user_id = UUIDField(required=True)
    email = EmailField(required=True)
    ip_address = StringField(required=True)
    user_agent = StringField()
    success = BooleanField(default=False)
    attempted_at = DateTimeField(default=datetime.now)
    
    meta = {
        'collection': 'login_attempts',
        'indexes': ['user_id', 'email', 'attempted_at']
    }


class UserManager(BaseUserManager):
    """
    Custom user manager for email-based authentication
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        # Sync to MongoDB
        self._sync_to_mongodb(user)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)
    
    def _sync_to_mongodb(self, user):
        """Sync Django user to MongoDB"""
        try:
            # Check if MongoDB user exists
            existing_user = MongoUser.objects(user_id=user.id).first()
            
            if existing_user:
                # Update existing MongoDB user
                existing_user.email = user.email
                existing_user.first_name = user.first_name or ''
                existing_user.last_name = user.last_name or ''
                existing_user.is_active = user.is_active
                existing_user.updated_at = datetime.now()
                existing_user.save()
            else:
                # Create new MongoDB user
                mongo_user = MongoUser(
                    user_id=user.id,
                    email=user.email,
                    first_name=user.first_name or '',
                    last_name=user.last_name or '',
                    is_active=user.is_active,
                    is_verified=getattr(user, 'is_verified', False),
                    created_at=user.date_joined,
                    updated_at=datetime.now(),
                )
                mongo_user.save()
                
        except Exception as e:
            print(f"Error syncing user to MongoDB: {e}")


class User(AbstractUser):
    """
    Custom User model for MongoDB integration
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Remove username field since we're using email
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    # Use custom manager
    objects = UserManager()
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        return self.first_name or self.email.split('@')[0]
    
    def save(self, *args, **kwargs):
        """Override save to sync with MongoDB"""
        super().save(*args, **kwargs)
        # Sync to MongoDB after saving
        try:
            self._sync_to_mongodb()
        except Exception as e:
            print(f"Error syncing user to MongoDB: {e}")
    
    def _sync_to_mongodb(self):
        """Sync this user instance to MongoDB"""
        try:
            # Check if MongoDB user exists
            existing_user = MongoUser.objects(user_id=self.id).first()
            
            if existing_user:
                # Update existing MongoDB user
                existing_user.email = self.email
                existing_user.first_name = self.first_name or ''
                existing_user.last_name = self.last_name or ''
                existing_user.is_active = self.is_active
                existing_user.updated_at = datetime.now()
                existing_user.save()
            else:
                # Create new MongoDB user
                mongo_user = MongoUser(
                    user_id=self.id,
                    email=self.email,
                    first_name=self.first_name or '',
                    last_name=self.last_name or '',
                    is_active=self.is_active,
                    is_verified=getattr(self, 'is_verified', False),
                    created_at=self.date_joined,
                    updated_at=datetime.now(),
                )
                mongo_user.save()
                
        except Exception as e:
            print(f"Error syncing user to MongoDB: {e}")


class UserProfile(models.Model):
    """
    Extended user profile information
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    avatar = models.URLField(blank=True, null=True)
    preferences = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"Profile for {self.user.email}"


class LoginAttempt(models.Model):
    """
    Track login attempts for security
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_attempts')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    success = models.BooleanField(default=False)
    attempted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'login_attempts'
        verbose_name = 'Login Attempt'
        verbose_name_plural = 'Login Attempts'
        ordering = ['-attempted_at']
    
    def __str__(self):
        return f"{self.user.email} - {'Success' if self.success else 'Failed'} at {self.attempted_at}"
