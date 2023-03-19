from django_filters import rest_framework as filters

class AuctionListFilter(filters.FilterSet):
    username = filters.CharFilter(field_name="user__username", lookup_expr="exact")
    name = filters.CharFilter(field_name="name", lookup_expr="contains")
    # mode = filters.
    category = filters.CharFilter(field_name="category__name", lookup_expr="exact")
    tags = filters.CharFilter(field_name="tags", lookup_expr="in")
    # finished = fil
    limit = filters.NumberFilter(field_name="limit", lookup_expr="gte")
    # int(limit)