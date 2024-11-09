from django.urls import path
from manager.views import ManagerApiView, ManagerDetailApiView

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


urlpatterns = [
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('redoc/', SpectacularRedocView.as_view(), name='redoc'),

    path('manager/', ManagerApiView.as_view()),
    path('manager/<str:name>/', ManagerDetailApiView.as_view()),
]