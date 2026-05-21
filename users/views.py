import json

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from team_finder.pagination import paginate
from users.forms import (
    CustomPasswordChangeForm,
    LoginForm,
    ProfileEditForm,
    RegistrationForm,
)
from users.models import Skill, User


def _parse_json_body(request):
    if request.content_type == "application/json":
        try:
            return json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return {}
    return request.POST


def _skill_json(skill, created=False, added=False):
    return {
        "skill_id": skill.id,
        "id": skill.id,
        "name": skill.name,
        "created": created,
        "added": added,
    }


def register_view(request):
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        phone_suffix = 1000000000 + User.objects.count()
        User.objects.create_user(
            email=data["email"],
            password=data["password"],
            name=data["name"],
            surname=data["surname"],
            phone=f"+7{phone_suffix}"[-12:],
        )
        return redirect("users:login")
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("projects:list")
    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.cleaned_data["user"])
        return redirect("projects:list")
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("projects:list")


def user_detail_view(request, user_id):
    profile_user = get_object_or_404(User, pk=user_id)
    return render(request, "users/user-details.html", {"user": profile_user})


def user_list_view(request):
    queryset = User.objects.all().order_by("-date_joined")
    active_skill = request.GET.get("skill", "").strip()
    if active_skill:
        queryset = queryset.filter(skills__name=active_skill)
    page_obj, query_prefix = paginate(request, queryset.distinct())
    all_skills = list(
        Skill.objects.order_by("name").values_list("name", flat=True).distinct()
    )
    return render(
        request,
        "users/participants.html",
        {
            "page_obj": page_obj,
            "query_prefix": query_prefix,
            "all_skills": all_skills,
            "active_skill": active_skill,
        },
    )


@login_required
def edit_profile_view(request):
    form = ProfileEditForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user,
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("users:detail", user_id=request.user.pk)
    return render(
        request,
        "users/edit_profile.html",
        {"form": form, "user": request.user},
    )


@login_required
def change_password_view(request):
    form = CustomPasswordChangeForm(request.user, request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("users:detail", user_id=request.user.pk)
    return render(request, "users/change_password.html", {"form": form})


@require_GET
def skills_autocomplete_view(request):
    query = request.GET.get("q", "").strip()
    skills = Skill.objects.filter(name__istartswith=query).order_by("name")[:10]
    payload = [{"id": skill.id, "name": skill.name} for skill in skills]
    return JsonResponse(payload, safe=False)


@login_required
@require_POST
def add_user_skill_view(request, user_id):
    profile_user = get_object_or_404(User, pk=user_id)
    if profile_user.pk != request.user.pk:
        return JsonResponse({"error": "forbidden"}, status=403)

    payload = _parse_json_body(request)
    skill = None
    created = False
    added = False

    if payload.get("skill_id"):
        skill = get_object_or_404(Skill, pk=payload["skill_id"])
    elif payload.get("name"):
        name = payload["name"].strip()
        if not name:
            return JsonResponse({"error": "empty name"}, status=400)
        skill, created = Skill.objects.get_or_create(name=name)
    else:
        return JsonResponse({"error": "invalid payload"}, status=400)

    if not profile_user.skills.filter(pk=skill.pk).exists():
        profile_user.skills.add(skill)
        added = True

    return JsonResponse(_skill_json(skill, created=created, added=added))


@login_required
@require_POST
def remove_user_skill_view(request, user_id, skill_id):
    profile_user = get_object_or_404(User, pk=user_id)
    if profile_user.pk != request.user.pk:
        return JsonResponse({"error": "forbidden"}, status=403)

    skill = get_object_or_404(Skill, pk=skill_id)
    if profile_user.skills.filter(pk=skill.pk).exists():
        profile_user.skills.remove(skill)
    return JsonResponse({"status": "ok"})
