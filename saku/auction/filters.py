from django_filters import rest_framework as filters
# from django.db.models import Transform
from distutils.util import strtobool
from datetime import datetime

# TODO:
# should change when mode handling changes in Auction model
# int_choices = [(1, 'Increasing'), (2, 'Decreasing')]
# int_choices = [('1', 1, '2', 2)]

# class StringIntFilter()

class AuctionListFilter(filters.FilterSet):
    username = filters.CharFilter(field_name="user__username", lookup_expr="exact")
    name = filters.CharFilter(field_name="name", lookup_expr="contains")
    mode = filters.NumberFilter(method='mode__exact')
    # mode = filters.TypedChoiceFilter(choices=int_choices, coerce=int)
    category = filters.CharFilter(field_name="category__name", lookup_expr="exact")
    tag = filters.CharFilter(field_name="tags", lookup_expr="in")
    # finished = fil
    # limit = filters.NumberFilter(field_name="limit", lookup_expr="gte")
    limit = filters.NumberFilter(method="limit__gte")
    # int(limit)

    def mode__exact(self, queryset, value, *args, **kwargs):
        try:
            queryset = queryset.filter(mode=int(args)) if args else queryset
        except ValueError:
            pass
        return queryset
    
    def limit__gte(self, queryset, value, *args, **kwargs):
        try:
            queryset = queryset.filter(limit__gte=int(args)) if args else queryset
        except ValueError:
            pass
        return queryset
    
    def finished__tf(self, queryset, value, *args, **kwargs):
        try:
            if args:
                is_finished = strtobool(args)
                if is_finished:
                    queryset = queryset.filter(finished_at__lt=datetime.now())
                else:
                    queryset = queryset.filter(finished_at__gte=datetime.now())
        except ValueError:
            pass
        return queryset