from import_export import resources
from .models import SessionConfig


class ExportData(resources.ModelResource):
    class Meta:
        model = SessionConfig
