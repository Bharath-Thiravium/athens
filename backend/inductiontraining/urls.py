from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InductionTrainingViewSet

router = DefaultRouter()
router.register(r'', InductionTrainingViewSet, basename='induction')

urlpatterns = [
    path('', include(router.urls)),
    # The router automatically generates URLs for @action decorators:
    # /induction/initiated_workers/ (from @action(detail=False))
    # /induction/{id}/attendance/ (from @action(detail=True))
    # /induction/users/ (from @action(detail=False))
    # /induction/users_search/ (from @action(detail=False))
]
