from django.conf import settings
from django.db import models

from team_finder.constants import (
    PROJECT_NAME_MAX_LENGTH,
    PROJECT_STATUS_CLOSED,
    PROJECT_STATUS_OPEN,
)


class Project(models.Model):
    class Status(models.TextChoices):
        OPEN = PROJECT_STATUS_OPEN, "Открыт"
        CLOSED = PROJECT_STATUS_CLOSED, "Закрыт"

    name = models.CharField(max_length=PROJECT_NAME_MAX_LENGTH)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    github_url = models.URLField(blank=True)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.OPEN,
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="participated_projects",
        blank=True,
    )

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.name