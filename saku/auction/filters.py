from datetime import datetime
from distutils.util import strtobool

from auction.models import Auction
from django_filters import rest_framework as filters


class AuctionListFilter(filters.FilterSet):
    username = filters.CharFilter(field_name="user__username", lookup_expr="exact")
    name = filters.CharFilter(field_name="name", lookup_expr="contains")
    mode = filters.NumberFilter(method='mode__exact')
    category = filters.CharFilter(field_name="category__name", lookup_expr="exact")
    tags = filters.CharFilter(method="tags__in")
    limit = filters.NumberFilter(method="limit__gte")
    finished = filters.Filter(method="finished__tf")
    is_online = filters.BooleanFilter(field_name="is_online")
    desc = filters.CharFilter(field_name="description", lookup_expr="contains")

    def mode__exact(self, queryset, value, *args, **kwargs):
        try:
            queryset = queryset.filter(mode=int(args[0])) if args else queryset
        except ValueError:
            pass
        return queryset
    
    def limit__gte(self, queryset, value, *args, **kwargs):
        try:
            queryset = queryset.filter(limit__gte=int(args[0])) if args else queryset
        except ValueError:
            pass
        return queryset
    
    def finished__tf(self, queryset, value, *args, **kwargs):
        try:
            if args:
                is_finished = strtobool(args[0])
                if is_finished:
                    queryset = queryset.filter(finished_at__lt=datetime.now())
                else:
                    queryset = queryset.filter(finished_at__gte=datetime.now())
        except ValueError:
            pass
        return queryset
    
    def tags__in(self, queryset, value, *args, **kwargs):
        try:
            if args:
                tags = args[0].split(',')
                queryset = queryset.filter(tags__in=tags)
        except ValueError:
            pass
        return queryset
    
    class Meta:
        model = Auction
        fields = ['username', 'name', 'mode', 'category', 'tags', 'limit', 'finished', 'is_online', 'desc']