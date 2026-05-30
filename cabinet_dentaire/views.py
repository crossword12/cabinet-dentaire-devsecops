from django.shortcuts import render

def home(request):
    print("==== HOME VUE APPELÉE ====")
    return render(request, 'home.html')

def handler403(request, exception=None):
    return render(request, "403.html", status=403)