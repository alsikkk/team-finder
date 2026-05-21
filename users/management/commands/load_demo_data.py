from django.core.management.base import BaseCommand

from projects.models import Project
from team_finder.constants import PROJECT_STATUS_CLOSED, PROJECT_STATUS_OPEN
from users.models import Skill, User


LEGACY_DEMO_EMAILS = (
    "anna.ivanova@example.com",
    "boris.petrov@example.com",
    "maria.sidorova@example.com",
)

DEMO_USERS = (
    {
        "email": "nikita.orlov@example.com",
        "password": "demo12345",
        "name": "Никита",
        "surname": "Орлов",
        "phone": "+79001110001",
        "about": "Тренер по бегу, собираю команду для марафонов.",
        "skills": ("Бег", "Силовые тренировки", "Растяжка"),
        "project": {
            "name": "Клуб утренних пробежек",
            "description": "Ежедневные групповые забеги в парке и подготовка к 10 км.",
            "status": PROJECT_STATUS_OPEN,
        },
    },
    {
        "email": "darya.kozlova@example.com",
        "password": "demo12345",
        "name": "Дарья",
        "surname": "Козлова",
        "phone": "+79001110002",
        "about": "Инструктор по плаванию и open water.",
        "skills": ("Плавание", "Триатлон", "ОФП"),
        "project": {
            "name": "Бассейн для любителей",
            "description": "Совместные тренировки по технике кроля и брассу.",
            "status": PROJECT_STATUS_OPEN,
        },
    },
    {
        "email": "maksim.belov@example.com",
        "password": "demo12345",
        "name": "Максим",
        "surname": "Белов",
        "phone": "+79001110003",
        "about": "Капитан любительской футбольной команды.",
        "skills": ("Футбол", "Баскетбол", "Волейбол"),
        "project": {
            "name": "Любительская футбольная лига",
            "description": "Ищем игроков для участия в городском турнире выходного дня.",
            "status": PROJECT_STATUS_CLOSED,
        },
    },
)


class Command(BaseCommand):
    help = "Создаёт тестовых пользователей, навыки и проекты для проверки TeamFinder."

    def handle(self, *args, **options):
        removed, _ = User.objects.filter(email__in=LEGACY_DEMO_EMAILS).delete()
        if removed:
            self.stdout.write(
                self.style.WARNING(f"Удалены старые демо-пользователи: {removed} записей.")
            )

        created_users = 0
        created_projects = 0

        for item in DEMO_USERS:
            user, created = User.objects.get_or_create(
                email=item["email"],
                defaults={
                    "name": item["name"],
                    "surname": item["surname"],
                    "phone": item["phone"],
                    "about": item["about"],
                },
            )
            if created:
                user.set_password(item["password"])
                user.save()
                created_users += 1
            else:
                user.name = item["name"]
                user.surname = item["surname"]
                user.about = item["about"]
                user.phone = item["phone"]
                user.save()

            user.skills.clear()
            for skill_name in item["skills"]:
                skill, _ = Skill.objects.get_or_create(name=skill_name)
                user.skills.add(skill)

            project_data = item["project"]
            project, project_created = Project.objects.get_or_create(
                name=project_data["name"],
                owner=user,
                defaults={
                    "description": project_data["description"],
                    "status": project_data["status"],
                },
            )
            if not project_created:
                project.description = project_data["description"]
                project.status = project_data["status"]
                project.save()
            if project_created:
                created_projects += 1
            project.participants.add(user)

        self.stdout.write(
            self.style.SUCCESS(
                f"Готово: пользователей добавлено {created_users}, "
                f"проектов добавлено {created_projects}."
            )
        )
