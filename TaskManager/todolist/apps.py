""" Config for creating a new instance of the application
with the given configuration
"""

from django.apps import AppConfig


class TodolistConfig(AppConfig):
    """Config"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "todolist"
