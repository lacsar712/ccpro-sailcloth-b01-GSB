from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ClothRollViewSet,
    DipRunViewSet,
    GsmBandSettingsView,
    LoftViewSet,
    dashboard_stats,
)

router = DefaultRouter()
router.register("lofts", LoftViewSet, basename="loft")
router.register("rolls", ClothRollViewSet, basename="roll")
router.register("dips", DipRunViewSet, basename="dip")

urlpatterns = [
    path("dashboard/", dashboard_stats, name="dashboard"),
    path("gsm-bands/", GsmBandSettingsView.as_view(), name="gsm-bands"),
    path("", include(router.urls)),
]
