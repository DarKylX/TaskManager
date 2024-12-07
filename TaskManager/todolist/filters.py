import django_filters
from django_filters import rest_framework as filters
from .models import Task, UserBIO
from django.utils import timezone
from datetime import timedelta

class TaskFilter(filters.FilterSet):

    status = django_filters.CharFilter(field_name='status', lookup_expr='exact')

    due_date = filters.DateFilter(field_name='due_date', lookup_expr='exact')

    due_date_range = filters.DateFromToRangeFilter(field_name='due_date')

    current_user = filters.BooleanFilter(method='filter_by_current_user', label="Filter by current user")


    class Meta:
        model = Task
        fields = ['due_date',]

    def filter_by_current_user(self, queryset, name, value):
        if value:
            user = self.request.user
            return queryset.filter(assignee=user)
        return queryset


class UserBIOFilter(filters.FilterSet):
    class Meta:
        model = UserBIO
        fields = ['age', 'role', 'company']

