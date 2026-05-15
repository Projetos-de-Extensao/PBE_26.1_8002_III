from django.urls import path, include
from . import views

urlpatterns = [
    path('singleobj/', views.singleobj),
    path('multipleobj/', views.multipleobj)
]

