from django.urls import path, re_path
from . import views


urlpatterns = [
    path('', views.manage_mirrors, name='mirror-manage'),
    path('add/', views.add_mirror, name='mirror-add'),
    #path('get/', views.get_idTags, name='idtag-get'),
    re_path(r'^edit/*', views.edit_mirror, name='mirror-edit'),
    re_path(r'^delete/*', views.delete_mirror, name='mirror-delete'),

]
