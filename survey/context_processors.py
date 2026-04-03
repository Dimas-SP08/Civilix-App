from .models import Project # Pastikan import ini benar relatif terhadap file

def sidebar_context(request):
    if request.user.is_authenticated:
        # Ambil 5 proyek terakhir yang diedit/dibuat milik user tersebut
        recent = Project.objects.filter(user=request.user).order_by('-created_at')
        
        return {'recent_projects': recent}
    return {}