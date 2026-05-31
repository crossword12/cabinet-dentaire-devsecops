from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

def home(request):
    print("==== HOME VUE APPELÉE ====")
    return render(request, 'home.html')

def handler403(request, exception=None):
    return render(request, "403.html", status=403)

def health_check(request):
    return JsonResponse({"status": "ok"})
def health_page(request):
    html = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>État du service</title>
        <style>
            body {
                margin: 0;
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #e8f3ff, #ffffff);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .card {
                background: white;
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.12);
                text-align: center;
                width: 420px;
            }
            .icon {
                width: 80px;
                height: 80px;
                margin: 0 auto 20px;
                border-radius: 50%;
                background: #e7f8ef;
                color: #16a34a;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 42px;
                font-weight: bold;
            }
            h1 {
                color: #1f2937;
                margin-bottom: 10px;
            }
            p {
                color: #4b5563;
                font-size: 16px;
            }
            .status {
                margin-top: 25px;
                display: inline-block;
                padding: 10px 18px;
                border-radius: 999px;
                background: #dcfce7;
                color: #166534;
                font-weight: bold;
            }
            .footer {
                margin-top: 25px;
                font-size: 13px;
                color: #6b7280;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <div class="icon">✓</div>
            <h1>Service opérationnel</h1>
            <p>L'application Cabinet Dentaire est active et répond correctement.</p>
            <div class="status">STATUS : OK</div>
            <div class="footer">Endpoint de supervision DevSecOps</div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)