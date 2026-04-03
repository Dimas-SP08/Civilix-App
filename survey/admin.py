from django.contrib import admin

# Register your models here.
from .models import Project, LevelingData,AIReport,CalculatedResult,CrossSection
admin.site.register(Project)
admin.site.register(LevelingData)
admin.site.register(CalculatedResult)
admin.site.register(CrossSection)
admin.site.register(AIReport)