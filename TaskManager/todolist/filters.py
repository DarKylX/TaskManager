""" Фильтры """

import django_filters
from django_filters import rest_framework as filters
from .models import Task, UserBIO


class TaskFilter(filters.FilterSet):
    """Filter"""

    status = django_filters.CharFilter(
        field_name="status", lookup_expr="exact", label="Статус"
    )

    due_date = filters.DateFilter(
        field_name="due_date", lookup_expr="exact", label="Дедлайн"
    )

    due_date_range = filters.DateFromToRangeFilter(
        field_name="due_date", label="Диапазон дедлайнов"
    )

    current_user = filters.BooleanFilter(
        method="filter_by_current_user", label="Поиск по авторизованному человеку"
    )

    class Meta:
        # pylint: disable=too-few-public-methods
        """Meta"""
        model = Task
        fields = [
            "due_date",
        ]

    def filter_by_current_user(self, queryset, _name, value):
        """Фильтрация по текущему пользователю"""
        if value:
            user = self.request.user
            return queryset.filter(assignee=user)
        return queryset


class UserBIOFilter(filters.FilterSet):
    """Filter"""

    class Meta:
        # pylint: disable=too-few-public-methods
        """Meta"""
        model = UserBIO
        fields = ["age", "role", "company"]
