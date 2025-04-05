from django.db import models
from django.contrib.gis.db import models as gis_models

class Appeal(models.Model):
    STATUS_CHOICES = (
        (1, 'Новое'),
        (2, 'В работе'),
        (3, 'Завершено'),
    )

    PROCESS_STATUS_CHOICES = (
        (1, 'Принято'),
        (2, 'Обрабатывается'),
        (3, 'Отклонено'),
    )

    title = models.CharField(max_length=1024)
    description = models.TextField()
    creation_date = models.DateTimeField(null=True)
    completion_date = models.DateTimeField(null=True)
    status = models.IntegerField(choices=STATUS_CHOICES)
    process_status = models.IntegerField(choices=PROCESS_STATUS_CHOICES)
    address = models.CharField(max_length=1024)
    coord_x = models.FloatField()
    coord_y = models.FloatField()
    kind_of_appeal_id = models.IntegerField()
    category_id = models.IntegerField(null=True)
    received_from = models.CharField(max_length=255, null=True)
    appeal_type_en = models.CharField(max_length=255, null=True)
    appeal_type_ru = models.CharField(max_length=255, null=True)
    appeal_type_kk = models.CharField(max_length=255, null=True)
    location = models.TextField(null=True, blank=True)
    hexagon_id = models.TextField(null=True, blank=True)
    boundary_coords = models.JSONField(null=True, blank=True)
    district_name = models.CharField(max_length=100, null=True, blank=True)
    district_boundary = gis_models.PolygonField(null=True, blank=True, srid=4326)

    def __str__(self):
        return self.title

class Meta:
    indexes = [
        models.Index(fields=['creation_date']),
        models.Index(fields=['status']),
        models.Index(fields=['appeal_type_ru']),
        models.Index(fields=['district_name']),
        models.Index(fields=['received_from']),
    ]

class HexagonAggregate(models.Model):
    hexagon_id = models.CharField(max_length=255)
    year = models.IntegerField(null=True, blank=True)
    month = models.IntegerField(null=True, blank=True)
    count = models.IntegerField()
    types = models.JSONField()
    boundary_coords = models.JSONField()

    class Meta:
        indexes = [
            models.Index(fields=['year', 'month']),
            models.Index(fields=['hexagon_id']),
        ]
