from django.urls import path, re_path
from . import views


urlpatterns = [
    path('', views.manage_managers, name='manager-manage'),
    path('add/', views.add_manager, name='manager-add'),
    #path('get/', views.get_idTags, name='idtag-get'),
    re_path(r'^edit/*', views.edit_manager, name='manager-edit'),
    re_path(r'^delete/*', views.delete_manager, name='manager-delete'),

]
