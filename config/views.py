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
                    max-width: 500px;
                }
                code {
                    background: #eee;
                    padding: 4px 8px;
                    border-radius: 4px;
                }
                .admin-info {
                    margin-top: 20px;
                    background: #fffae6;
                    padding: 20px;
                    border-radius: 8px;
                    border: 1px solid #ffe58f;
                    color: #663c00;
                    font-weight: bold;
                }
                a {
                    color: #1890ff;
                    text-decoration: none;
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

                <div class="admin-info">
                    🎉 Congratulations on checking this page!<br>
                    The admin account and password are:<br>
                    <code>admin@example.com</code> / <code>password123</code><br>
                    Visit the <a href="https://snowcraft-dtc.vercel.app/adminlogin" target="_blank">Admin Dashboard</a>
                </div>
            </div>
        </body>
    </html>
    """)