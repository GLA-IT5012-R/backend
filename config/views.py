# config/views.py
from django.http import HttpResponse

def home(request):
    return HttpResponse("""
    <html>
        <head>
            <title>Snowcraft Backend</title>
            <style>
                body {
                    font-family: Arial;
                    text-align: center;
                    margin-top: 100px;
                    background: #f5f5f5;
                }
                .card {
                    background: white;
                    padding: 40px;
                    border-radius: 10px;
                    display: inline-block;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
                }
                code {
                    background: #eee;
                    padding: 4px 8px;
                    border-radius: 4px;
                }
            </style>
        </head>
        <body>
            <div class="card">
                <h1>Snowcraft Backend</h1>
                <p>Backend service is running.</p>
                <p>API prefix: <code>/api</code></p>
                <p>Example endpoint:</p>
                <code>/api/hello</code>
            </div>
        </body>
    </html>
    """)