from django.conf import settings
from django.db import models

from team_finder.constants import (
    PROJECT_NAME_MAX_LENGTH,
    PROJECT_STATUS_CHOICES,
    PROJECT_STATUS_CLOSED,
    PROJECT_STATUS_MAX_LENGTH,
    PROJECT_STATUS_OPEN,
)


class Project(models.Model):
    STATUS_OPEN = PROJECT_STATUS_OPEN
    STATUS_CLOSED = PROJECT_STATUS_CLOSED

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
        max_length=PROJECT_STATUS_MAX_LENGTH,
        choices=PROJECT_STATUS_CHOICES,
        default=PROJECT_STATUS_OPEN,
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
