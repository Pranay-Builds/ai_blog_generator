from django.db import path
from . import views  

urlpatterns = [
    path('', views.index, name='index'), 
]
