from django.core.paginator import Paginator

from team_finder.constants import PAGE_SIZE


def paginate(request, queryset, per_page=PAGE_SIZE):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)
    query_params = request.GET.copy()
    query_params.pop("page", None)
    query_prefix = f"{query_params.urlencode()}&" if query_params else ""
    return page_obj, query_prefix
