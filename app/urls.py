from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('pubilc/', views.pubilc, name='pubilc'),
    path('report/', views.report, name='report'),
    path('report2/', views.report2, name='report2'),
    path('public3/', views.public3, name='public3'),
    path('index/', views.index, name='index'),
    path('myreports/', views.myreports, name='myreports'),
    path('officer/', views.officer, name='officer'),
    path('role/', views.role, name='role'),
    path('report/', views.report, name='report'),
    path("upload/", views.upload_image, name="upload"),
    path("api/reports/", views.get_reports),
    path("login", views.login,name='login'),
    path("reports/pdf/<int:id>/", views.view_pdf, name="view_pdf"),
]