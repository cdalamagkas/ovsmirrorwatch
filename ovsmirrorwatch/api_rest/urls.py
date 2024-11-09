from django.urls import path
from manager.views import ManagerApiView, ManagerDetailApiView
from bridge.views import BridgeApiView, BridgeDetailApiView
from port.views import PortApiView, PortDetailApiView
from mirror.views import MirrorApiView, MirrorDetailApiView

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


urlpatterns = [
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('redoc/', SpectacularRedocView.as_view(), name='redoc'),

    path('manager/', ManagerApiView.as_view()),
    path('manager/<str:name>/', ManagerDetailApiView.as_view()),
    path('bridge/', BridgeApiView.as_view()),
    path('bridge/<str:name>/', BridgeDetailApiView.as_view()),
    path('port/', PortApiView.as_view()),
    path('port/<str:name>/', PortDetailApiView.as_view()),
    path('mirror/', MirrorApiView.as_view()),
    path('mirror/<str:name>/', MirrorDetailApiView.as_view()),
]