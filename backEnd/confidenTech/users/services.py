from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction
import logging
from datetime import datetime, timedelta
import hashlib
import secrets

from .models import User, UserProfile, LoginAttempt
from .mongodb_utils import save_user_to_mongodb, get_user_from_mongodb, update_user_in_mongodb

logger = logging.getLogger(__name__)


class UserService:
    """
    Service class for user-related business logic
    """
    
    @staticmethod
    def create_user(email, password, first_name=None, last_name=None):
        """
        Create a new user with validation
        """
        try:
            # Validate password
            validate_password(password)
            
            # Check if user already exists
            if User.objects.filter(email=email).exists():
                raise ValidationError("User with this email already exists.")
            
            with transaction.atomic():
                # Create user
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                
                # Create user profile
                UserProfile.objects.create(user=user)
                
                # Save to MongoDB
                user_data = {
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_active': user.is_active,
                    'is_verified': user.is_verified,
                    'created_at': user.created_at.isoformat(),
                    'updated_at': user.updated_at.isoformat(),
                    'last_login': user.last_login.isoformat() if user.last_login else None
                }
                save_user_to_mongodb(user_data)
                
                logger.info(f"User created successfully: {email}")
                return user
                
        except Exception as e:
            logger.error(f"Failed to create user {email}: {str(e)}")
            raise
    
    @staticmethod
    def authenticate_user(email, password, request=None):
        """
        Authenticate user with security logging
        """
        try:
            user = authenticate(email=email, password=password)
            
            if user:
                # Log successful login
                if request:
                    UserService._log_login_attempt(user, request, success=True)
                
                # Update last login
                user.last_login = timezone.now()
                user.save(update_fields=['last_login'])
                
                logger.info(f"User authenticated successfully: {email}")
                return user
            else:
                # Log failed login attempt
                if request:
                    try:
                        user = User.objects.get(email=email)
                        UserService._log_login_attempt(user, request, success=False)
                    except User.DoesNotExist:
                        pass
                
                logger.warning(f"Failed authentication attempt for: {email}")
                return None
                
        except Exception as e:
            logger.error(f"Authentication error for {email}: {str(e)}")
            raise
    
    @staticmethod
    def _log_login_attempt(user, request, success):
        """
        Log login attempt for security tracking
        """
        try:
            ip_address = UserService._get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            LoginAttempt.objects.create(
                user=user,
                ip_address=ip_address,
                user_agent=user_agent,
                success=success
            )
        except Exception as e:
            logger.error(f"Failed to log login attempt: {str(e)}")
    
    @staticmethod
    def _get_client_ip(request):
        """
        Get client IP address
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def update_user_profile(user, profile_data):
        """
        Update user profile information
        """
        try:
            with transaction.atomic():
                # Update user fields
                if 'first_name' in profile_data:
                    user.first_name = profile_data['first_name']
                if 'last_name' in profile_data:
                    user.last_name = profile_data['last_name']
                user.save()
                
                # Update profile
                profile, created = UserProfile.objects.get_or_create(user=user)
                for field, value in profile_data.items():
                    if hasattr(profile, field):
                        setattr(profile, field, value)
                profile.save()
                
                # Update MongoDB
                update_data = {
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'updated_at': user.updated_at.isoformat()
                }
                update_user_in_mongodb(user.email, update_data)
                
                logger.info(f"User profile updated: {user.email}")
                return user
                
        except Exception as e:
            logger.error(f"Failed to update user profile {user.email}: {str(e)}")
            raise
    
    @staticmethod
    def change_password(user, old_password, new_password):
        """
        Change user password with validation
        """
        try:
            # Verify old password
            if not user.check_password(old_password):
                raise ValidationError("Old password is incorrect.")
            
            # Validate new password
            validate_password(new_password)
            
            # Update password
            user.set_password(new_password)
            user.save()
            
            logger.info(f"Password changed for user: {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to change password for {user.email}: {str(e)}")
            raise
    
    @staticmethod
    def get_user_login_history(user, page=1, page_size=10):
        """
        Get user login history with pagination
        """
        try:
            start = (page - 1) * page_size
            end = start + page_size
            
            login_attempts = LoginAttempt.objects.filter(user=user).order_by('-attempted_at')[start:end]
            total_count = LoginAttempt.objects.filter(user=user).count()
            
            return {
                'results': login_attempts,
                'total_count': total_count,
                'page': page,
                'page_size': page_size,
                'total_pages': (total_count + page_size - 1) // page_size
            }
            
        except Exception as e:
            logger.error(f"Failed to get login history for {user.email}: {str(e)}")
            raise
    
    @staticmethod
    def get_user_stats(user):
        """
        Get user statistics
        """
        try:
            total_logins = LoginAttempt.objects.filter(user=user, success=True).count()
            failed_attempts = LoginAttempt.objects.filter(user=user, success=False).count()
            recent_logins = LoginAttempt.objects.filter(user=user, success=True).order_by('-attempted_at')[:5]
            
            return {
                'total_logins': total_logins,
                'failed_attempts': failed_attempts,
                'recent_logins': recent_logins
            }
            
        except Exception as e:
            logger.error(f"Failed to get user stats for {user.email}: {str(e)}")
            raise
    
    @staticmethod
    def check_email_exists(email):
        """
        Check if email already exists
        """
        try:
            return User.objects.filter(email=email).exists()
        except Exception as e:
            logger.error(f"Failed to check email existence for {email}: {str(e)}")
            raise


class SecurityService:
    """
    Service class for security-related operations
    """
    
    @staticmethod
    def generate_secure_token():
        """
        Generate a secure random token
        """
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def hash_password(password):
        """
        Hash password using Django's built-in hashing
        """
        from django.contrib.auth.hashers import make_password
        return make_password(password)
    
    @staticmethod
    def verify_password(password, hashed_password):
        """
        Verify password against hash
        """
        from django.contrib.auth.hashers import check_password
        return check_password(password, hashed_password)
    
    @staticmethod
    def get_suspicious_activity(user, hours=24):
        """
        Check for suspicious login activity
        """
        try:
            since = timezone.now() - timedelta(hours=hours)
            failed_attempts = LoginAttempt.objects.filter(
                user=user,
                success=False,
                attempted_at__gte=since
            ).count()
            
            return failed_attempts > 5  # Flag if more than 5 failed attempts in 24 hours
            
        except Exception as e:
            logger.error(f"Failed to check suspicious activity for {user.email}: {str(e)}")
            return False
