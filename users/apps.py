from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'


# class AuthConfig(AppConfig):
#     name = 'django.contrib.auth'
#     verbose_name = 'User Management'