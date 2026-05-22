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
    name = models.CharField(max_length=SKILL_NAME_MAX_LENGTH, verbose_name="Навык")

    class Meta:
        ordering = ("name",)
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name="Email")
    name = models.CharField(max_length=USER_NAME_MAX_LENGTH, verbose_name="Имя")
    surname = models.CharField(max_length=USER_NAME_MAX_LENGTH, verbose_name="Фамилия")
    avatar = models.ImageField(upload_to="avatars/", verbose_name="Аватар", blank=True, null=True)
    phone = models.CharField(max_length=USER_PHONE_MAX_LENGTH, verbose_name="Телефон", blank=True)
    github_url = models.URLField(blank=True, verbose_name="Ссылка на GitHub")
    about = models.TextField(max_length=USER_ABOUT_MAX_LENGTH, blank=True, verbose_name="О себе")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    skills = models.ManyToManyField(Skill, related_name="users", blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("name", "surname")

    class Meta:
        ordering = ("-date_joined",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.name} {self.surname}"