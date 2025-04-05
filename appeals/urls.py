from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AppealViewSet, appeals_statistics, hexagons_list,
    appeals_list, districts_polygons,
    appeal_counts_by_type, appeal_summary, fast_hexagons,
)
router = DefaultRouter()
router.register(r'appeals', AppealViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('appeals-statistics/', appeals_statistics),
    path('appeals-summary/', appeal_summary),
    path('appeals-by-type/', appeal_counts_by_type),
    path('hexagons/', hexagons_list),
    path('appeals-list/', appeals_list),
    path('districts-polygons/', districts_polygons),
    path('fast-hexagons/', fast_hexagons, name='fast-hexagons'),
]
