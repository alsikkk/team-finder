from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from projects.forms import ProjectForm
from projects.models import Project
from team_finder.constants import (
    PROJECT_STATUS_CLOSED,
    PROJECT_STATUS_OPEN,
)
from team_finder.pagination import paginate


def project_list_view(request):
    queryset = Project.objects.select_related("owner").prefetch_related("participants")
    page_obj, query_prefix = paginate(request, queryset)
    return render(
        request,
        "projects/project_list.html",
        {
            "page_obj": page_obj,
            "query_prefix": query_prefix,
        },
    )


def project_detail_view(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants"),
        pk=project_id,
    )
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def project_create_view(request):
    form = ProjectForm(request.POST or None)

    if request.method != "POST":
        return render(
            request,
            "projects/create-project.html",
            {"form": form, "is_edit": False},
        )

    if not form.is_valid():
        return render(
            request,
            "projects/create-project.html",
            {"form": form, "is_edit": False},
        )

    project = form.save(commit=False)
    project.owner = request.user
    project.save()
    project.participants.add(request.user)
    return redirect("projects:detail", project_id=project.pk)


@login_required
def project_edit_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id, owner=request.user)
    form = ProjectForm(request.POST or None, instance=project)

    if request.method != "POST":
        return render(
            request,
            "projects/create-project.html",
            {"form": form, "is_edit": True},
        )

    if not form.is_valid():
        return render(
            request,
            "projects/create-project.html",
            {"form": form, "is_edit": True},
        )

    form.save()
    return redirect("projects:detail", project_id=project.pk)


@login_required
@require_POST
def project_complete_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id, owner=request.user)

    if project.status != PROJECT_STATUS_OPEN:
        return JsonResponse({"status": "error"}, status=400)

    project.status = PROJECT_STATUS_CLOSED
    project.save(update_fields=["status"])

    return JsonResponse({"status": "ok", "project_status": PROJECT_STATUS_CLOSED})


@login_required
@require_POST
def toggle_participate_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
      
    if project.owner_id == request.user.pk:
        return JsonResponse({"status": "error"}, status=403)

    if project.participants.filter(pk=request.user.pk).exists():
        project.participants.remove(request.user)
        return JsonResponse({"status": "ok", "participant": False})

    project.participants.add(request.user)
    return JsonResponse({"status": "ok", "participant": True})