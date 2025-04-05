from rest_framework import serializers
from .models import Appeal

# 1. Основной сериалайзер для таблиц, экспорта, подробных данных
class AppealSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    process_status_display = serializers.CharField(source='get_process_status_display', read_only=True)

    class Meta:
        model = Appeal
        fields = [
            'id',
            'title',
            'description',
            'creation_date',
            'completion_date',
            'status',
            'process_status',
            'process_status_display',
            'status_display',
            'appeal_type_ru',
            'district_name',
            'coord_x',
            'coord_y',
            'hexagon_id',
        ]

# 2. Для отображения точек или hex-нагрузки на карте
class AppealMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appeal
        fields = [
            'id',
            'appeal_type_ru',
            'status',
            'coord_x',
            'coord_y',
            'hexagon_id',
        ]

class DistrictPolygonSerializer(serializers.Serializer):
    district_name = serializers.CharField()
    district_boundary = serializers.CharField()
    count = serializers.IntegerField()
    types = serializers.DictField(child=serializers.IntegerField())
