from django.apps import AppConfig


class TranslationConfig(AppConfig):
    # Sets the default primary key field type for models in this app
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'translation'
