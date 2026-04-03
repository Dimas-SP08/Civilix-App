from django.forms import ModelForm
from .models import Project

class ProjectForm(ModelForm):
    """
    Formulir sederhana untuk membuat objek Project baru
    """
    class Meta:
        model = Project
        # Pilih fields yang akan diisi oleh user melalui modal
        fields = ['project_name', 'initial_elevation', 'purpose','survey_type']