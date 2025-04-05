from rest_framework import viewsets, filters
from .models import Appeal
from .serializers import AppealSerializer
from django.db.models import Count, Q
from django.db.models.functions import ExtractYear, ExtractMonth
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.core.paginator import Paginator
from .models import HexagonAggregate
import json

# class AppealViewSet(viewsets.ModelViewSet):
#     queryset = Appeal.objects.all()
#     serializer_class = AppealSerializer
#     filter_backends = [filters.SearchFilter, filters.OrderingFilter]
#     search_fields = ['title', 'address', 'appeal_type_ru']
#     ordering_fields = ['creation_date', 'completion_date']

# views.py
@api_view(['GET'])
def appeals_statistics(request):
    year_param = request.query_params.get('year')
    qs = Appeal.objects.all()
    if year_param:
        qs = qs.filter(creation_date__year=year_param)

    total = qs.count()
    resolved = qs.filter(status=3).count()
    in_progress = qs.filter(status=2).count()
    with_budget = qs.filter(received_from__icontains="бюджет").count()

    years_qs = Appeal.objects.values_list(ExtractYear('creation_date'), flat=True).distinct()
    years = sorted(set(int(y) for y in years_qs if y))

    data_by_year = {}
    for year in sorted(years):
        monthly_counts = {m: 0 for m in range(1, 13)}
        results = qs.filter(creation_date__year=year) \
                    .values(month=ExtractMonth('creation_date')) \
                    .annotate(count=Count('id'))
        for entry in results:
            monthly_counts[entry['month']] = entry['count']
        data_by_year[year] = monthly_counts

    return Response({
        "monthly_data": data_by_year,
        "summary": {
            "total": total,
            "resolved": resolved,
            "in_progress": in_progress,
            "with_budget": with_budget
        }
    })

@api_view(['GET'])
def appeal_counts_by_type(request):
    year = request.query_params.get("year")
    month = request.query_params.get("month")

    qs = Appeal.objects.all()

    if year:
        qs = qs.filter(creation_date__year=year)
    if month:
        qs = qs.filter(creation_date__month=month)

    grouped = qs.values("appeal_type_ru").annotate(count=Count("id")).order_by("-count")
    return Response(grouped)

@api_view(['GET'])
def appeal_summary(request):
    year = request.query_params.get("year")
    month = request.query_params.get("month")

    qs = Appeal.objects.all()
    if year:
        qs = qs.filter(creation_date__year=year)
    if month:
        qs = qs.filter(creation_date__month=month)

    return Response({
        "total": qs.count(),
        "resolved": qs.filter(status=3).count(),
        "in_progress": qs.filter(status=2).count(),
    })

class AppealViewSet(ModelViewSet):
    queryset = Appeal.objects.all()
    serializer_class = AppealSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        year = self.request.query_params.get("year")
        month = self.request.query_params.get("month")

        if year:
            try:
                queryset = queryset.filter(creation_date__year=int(year))
            except ValueError:
                pass

        if month:
            try:
                queryset = queryset.filter(creation_date__month=int(month))
            except ValueError:
                pass

        return queryset

@api_view(['GET'])
def hexagons_list(request):
    year = request.query_params.get("year")
    month = request.query_params.get("month")
    queryset = Appeal.objects.exclude(boundary_coords=None)

    if year:
        queryset = queryset.filter(creation_date__year=year)
    if month:
        queryset = queryset.filter(creation_date__month=month)

    data = {}
    for appeal in queryset:
        hex_id = appeal.hexagon_id

        # print("RAW TYPE:", appeal.appeal_type_ru)

        if hex_id not in data:
            data[hex_id] = {
                "hexagon_id": hex_id,
                "boundary_coords": appeal.boundary_coords,
                "count": 0,
                "types": {}
            }

        data[hex_id]["count"] += 1
        appeal_type = appeal.appeal_type_ru
        if appeal_type not in data[hex_id]["types"]:
            data[hex_id]["types"][appeal_type] = 0
        data[hex_id]["types"][appeal_type] += 1

    return Response(list(data.values()))

@api_view(['GET'])
def fast_hexagons(request):
    year = request.query_params.get("year")
    month = request.query_params.get("month")

    qs = HexagonAggregate.objects.all()

    if year and year != "all":
        qs = qs.filter(year=int(year))
    elif year == "all":
        qs = qs.filter(year__isnull=True)

    if month and month != "all":
        qs = qs.filter(month=int(month))
    elif month == "all":
        qs = qs.filter(month__isnull=True)

    data = []
    for item in qs:
        data.append({
            "hexagon_id": item.hexagon_id,
            "count": item.count,
            "types": item.types,
            "boundary_coords": item.boundary_coords,
        })

    return Response(data)


@api_view(['GET'])
def appeals_list(request):
    year = request.query_params.get("year")
    month = request.query_params.get("month")
    appeal_type = request.query_params.get("type")
    district_name = request.query_params.get("district_name")
    page = int(request.query_params.get("page", 1))
    export_all = request.query_params.get("all") == "true"

    queryset = Appeal.objects.all().order_by('-creation_date')

    if year:
        queryset = queryset.filter(creation_date__year=year)
    if month:
        queryset = queryset.filter(creation_date__month=month)
    if appeal_type:
        queryset = queryset.filter(appeal_type_ru=appeal_type)
    if district_name:
        queryset = queryset.filter(district_name=district_name)

    # если экспортируем всё — возвращаем без пагинации
    if export_all:
        return Response({
            "results": AppealSerializer(queryset, many=True).data
        })

    paginator = Paginator(queryset, 20)
    page_obj = paginator.get_page(page)

    return Response({
        "results": AppealSerializer(page_obj, many=True).data,
        "total_pages": paginator.num_pages,
        "current_page": page
    })

@api_view(['GET'])
def districts_polygons(request):
    year = request.query_params.get("year")
    month = request.query_params.get("month")

    qs = Appeal.objects.exclude(district_boundary=None).exclude(district_name=None)

    if year:
        qs = qs.filter(creation_date__year=year)
    if month:
        qs = qs.filter(creation_date__month=month)

    districts = {}

    for appeal in qs:
        name = appeal.district_name
        if name not in districts:
            districts[name] = {
                "name": name,
                "geometry": appeal.district_boundary.geojson,
                "count": 0,
                "types": {}
            }

        districts[name]["count"] += 1
        appeal_type = appeal.appeal_type_ru
        if appeal_type not in districts[name]["types"]:
            districts[name]["types"][appeal_type] = 0
        districts[name]["types"][appeal_type] += 1

    return Response(list(districts.values()))