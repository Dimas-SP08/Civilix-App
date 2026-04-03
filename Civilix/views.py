from django.shortcuts import render,redirect

def index(request):
    if request.user.is_authenticated:
        return redirect('survey:index')
    else:   
        return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def features(request):
    return render(request, 'features.html')

def docs(request):
    return render(request, 'docs.html')

def contact(request):
    return render(request, 'contact.html')

