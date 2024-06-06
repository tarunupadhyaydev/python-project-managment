from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from organizations.models import Organization
from django.conf import settings


# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=30, blank=True, verbose_name="Name")
    last_name = models.CharField(max_length=30, blank=True ,verbose_name="Surname")
    organization = models.ForeignKey(Organization,related_name='organization_assignement',blank=True,null=True, on_delete = models.CASCADE)
    designation = models.CharField(max_length=255,blank=True,)
    job_type = models.CharField(max_length=255,blank=True,)
    telephone = models.CharField(max_length=150,blank=True, verbose_name="Work Telephone")
    mobile = models.CharField(max_length=150,blank=True, verbose_name="Cell phone")
    address = models.CharField(max_length=255,blank=True, verbose_name="Work Street Address")
    postal_address = models.CharField(max_length=255,blank=True, verbose_name="Work Postal Address")
    is_active = models.BooleanField(default=True, verbose_name="Status")
    is_staff = models.BooleanField(default=True)
    is_employee = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True, on_delete=models.CASCADE, related_name='create_by_user_model')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    #USERNAME_FIELD = 'email'
    USERNAME_FIELD = 'username'
    #REQUIRED_FIELDS = ['username']
    REQUIRED_FIELDS = ['email']

    objects = UserManager()


        # defining the custom permissions using the class Meta
    class Meta:
        verbose_name = 'Users'
        verbose_name_plural = 'Users'
        permissions = (("is_employee", "Can user is of type employee"),)


    def __str__(self):
      return self.email

#   class Meta:
#         permissions = (("is_employee", "User is of type employee"),
#         #, ("perm2", "details of permission2"),
#         # You can add other custom permissions as required
#         )
