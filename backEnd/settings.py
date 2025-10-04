INSTALLED_APPS = [
    # ...
    "rest_framework",
    "rest_framework_simplejwt",
    "users",  # your app
]

# MongoDB via Djongo

DATABASES = {
  "default": {
    "ENGINE": "djongo",
    "NAME": "confidentech",
    "CLIENT": {"host": "mongodb+srv://munavarh:fPF8OVOrnd9JcPmV@main-cluster.hvznv1t.mongodb.net/?retryWrites=true&w=majority&appName=Main-Cluster"}
  }
}


AUTH_USER_MODEL = "users.User"  # custom user below

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}

# Optional but recommended:
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
