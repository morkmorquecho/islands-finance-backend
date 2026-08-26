from django.db import models
from core.models import BaseModel 
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractUser
import uuid

class User(AbstractUser):
    email = models.EmailField(unique=True) 
    REQUIRED_FIELDS = ['email']
