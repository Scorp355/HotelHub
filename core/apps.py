from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Ядро (Главная страница)'

    def ready(self):
        from django.db.backends.signals import connection_created
        connection_created.connect(_register_unicode_lower)


def _register_unicode_lower(sender, connection, **kwargs):
    if connection.vendor == 'sqlite':
        connection.connection.create_function('LOWER', 1, _py_lower)


def _py_lower(value):
    return value.lower() if isinstance(value, str) else value
