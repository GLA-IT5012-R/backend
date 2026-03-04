# 🛠 Backend – Django REST E-commerce System

## 1. Project Overview

This backend is built with **Django** and **Django REST Framework (DRF)**.

It provides RESTful APIs for:

- User authentication and verification
- Product management
- Customisation handling
- Shopping cart logic
- Order processing
- Review system
- Admin analytics

Database: **PostgreSQL**



## 2. Tech Stack

- **Framework:** Django
- **API:** Django REST Framework
- **Database:** PostgreSQL
- **Authentication:** JWT + Email verification
- **Media Storage:** Local media directory
- **Data Serialization:** DRF Serializers

---

## 3. Application Modules

```bash

backend/
├── config/                # Project configuration｜settings
├── m_users/               # User module: profile & authentication
│   └── tests.py           # Unit tests for core module
├── m_products/            # Products, assets, and customization
├── m_shops/               # Orders & cart management
├── m_feedback/            # Reviews & ratings
├── media/                 # Uploaded textures / media files
├── manage.py              # Django management script
└── requirements.txt       # Project dependencies

```

## 4. Running the Backend

```bash 
pip install -r requirements.txt 
python manage.py migrate 
python manage.py runserver
```


