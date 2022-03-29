from ast import Try
from operator import is_not
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.core.mail import send_mail
import uuid as uuid_lib

class UserManager(UserManager):
    def _create_user(self,email,password,**extra_fields):
        email = self.normalize_email(email)
        user = self.model(email = email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db) #検討がつかない
        return user
    
    def create_user(self,email,password=None,**extra_fields):
        extra_fields.setdefault('is_staff',False)
        extra_fields.setdefault('is_superuser',False)
        return self._create_user(email,password=password,**extra_fields)
    
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        email = self.normalize_email(email=email)
        user = self.model(email=email,**extra_fields)
        user.username=email
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    """ Custom User """
    class Meta:
        verbose_name = 'ユーザー'
        verbose_name_plural = 'ユーザー'

    id = models.UUIDField(default=uuid_lib.uuid4,primary_key=True,editable=False) #管理ID デフォがidで検索できるので、こちらもidでフィールド登録
    username = models.CharField(max_length=30,unique=False) #ユーザー氏名
    email = models.EmailField(unique=True,blank=True,null=True) #メアド (これで認証)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    password_changed = models.BooleanField(default=False)
    password_changed_date = models.DateTimeField(blank=True,null=True)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELD = ''

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self,subject,message,from_email=None,**kwargs):
        send_mail(subject,message,from_email,[self.email],**kwargs)
    
    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.username
    
    def get_short_name(self):
        return self.username