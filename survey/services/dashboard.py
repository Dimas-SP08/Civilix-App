
from ..models import  LevelingData,AIReport,CrossSection,CalculatedResult
from django.db.models import Q


def calculate_data_projects(request,projects):
    # ===> HITUNG STATISTIK <===
    total_projects = projects.count()
    active_count = projects.filter(status='IN_PROGRESS').count()
    completed_count = projects.filter(status='COMPLETED').count()
    total_data_points = LevelingData.objects.filter(project__in=projects)
    ai_insight = AIReport.objects.filter(project__in=projects).order_by('-generated_at').first()  # Ambil insight terbaru
    ai_report = ai_insight.report_text[:350] + '...' if ai_insight and ai_insight.report_text else None    
    # Menghitung ada BERAPA PROYEK yang punya minimal 1 data Cross Section
    total_cs_projects = CrossSection.objects.filter(
        station__project__in=projects
    ).values('station__project').distinct().count()
    total_cut_fill_projects = CalculatedResult.objects.filter(
        project__in=projects
    ).filter(
        Q(cut_volume__gt=0) | Q(fill_volume__gt=0) # Asumsi nilai hitungan > 0
    ).values('project').distinct().count()
    persen_completed = (completed_count / total_projects * 100) if total_projects > 0 else 0
    name = request.user.nama if request.user.nama else 'guest'


    context = {
        'projects': projects,
        'total_projects': total_projects,
        'active_count': active_count,
        'completed_count': completed_count,
        'total_data_points': total_data_points.count(),
        'ai_report': ai_report,
        'total_cut_fill_projects': total_cut_fill_projects,
        'total_cs': total_cs_projects,
        'persen_completed': persen_completed,
        'name': name

    }

    return context
