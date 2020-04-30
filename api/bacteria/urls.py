from django.urls import path

from . import views

urlpatterns = [
    path('loadculture', views.load_culture),
    path('saveculture', views.save_culture),
    path('savegroup', views.save_group),
    path('updategroup', views.update_group),
    path('addnewgroup', views.new_group),
    path('loadantibioticset', views.load_antibiotic_set),
    path('loadsetelements', views.load_set_elements)
]
