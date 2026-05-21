from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from team_finder.constants import (
    SKILL_NAME_MAX_LENGTH,
    USER_ABOUT_MAX_LENGTH,
    USER_NAME_MAX_LENGTH,
    USER_PHONE_MAX_LENGTH,
)
from users.managers import UserManager


class Skill(models.Model):
    name = models.CharField(max_length=SKILL_NAME_MAX_LENGTH)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=USER_NAME_MAX_LENGTH)
    surname = models.CharField(max_length=USER_NAME_MAX_LENGTH)
    avatar = models.ImageField(upload_to="avatars/")
    phone = models.CharField(max_length=USER_PHONE_MAX_LENGTH)
    github_url = models.URLField(blank=True)
    about = models.TextField(max_length=USER_ABOUT_MAX_LENGTH, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    skills = models.ManyToManyField(Skill, related_name="users", blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("name", "surname")

    class Meta:
        ordering = ("-date_joined",)

    def __str__(self):
        return f"{self.name} {self.surname}"
