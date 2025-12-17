from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JobTrainingViewSet

router = DefaultRouter()
router.register(r'', JobTrainingViewSet, basename='jobtraining')

urlpatterns = [
    path('', include(router.urls)),
]
