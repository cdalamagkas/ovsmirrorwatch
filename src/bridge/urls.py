from django.urls import path, re_path
from . import views


urlpatterns = [
    #path('', views.manage_mirrors, name='mirror-manage'),
    path('add/', views.add_bridge, name='bridge-add'),
    #path('get/', views.get_idTags, name='idtag-get'),
    re_path(r'^edit/*', views.edit_bridge, name='bridge-edit'),
    re_path(r'^delete/*', views.delete_bridge, name='bridge-delete'),

]
