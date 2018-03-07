from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('api/', views.api, name='api'),
    path('store_password/', views.store_password, name='store_password'),
    path('delete_password/', views.delete_password, name='delete_password'),
]
