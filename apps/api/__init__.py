from django.urls import path, include

api_v1 = [
    path('', include('apps.api.v1'))
]

urlpatterns = [
    path('v1/', include(api_v1))
]
