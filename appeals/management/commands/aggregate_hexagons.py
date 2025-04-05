from django.db.models.functions import ExtractYear, ExtractMonth
from django.db.models import Count
from django.core.management.base import BaseCommand
from appeals.models import Appeal, HexagonAggregate

def update_aggregates(aggregates, key, boundary_coords, appeal_type, count):
    if key not in aggregates:
        aggregates[key] = {
            'count': 0,
            'types': {},
            'boundary_coords': boundary_coords,
        }
    aggregates[key]['count'] += count
    aggregates[key]['types'][appeal_type] = aggregates[key]['types'].get(appeal_type, 0) + count

class Command(BaseCommand):
    help = 'Aggregates appeals into hexagon-based summaries'

    def handle(self, *args, **options):
        appeals = Appeal.objects.exclude(hexagon_id=None).exclude(boundary_coords=None)

        # 1. year + month
        grouped = appeals.annotate(
            year=ExtractYear('creation_date'),
            month=ExtractMonth('creation_date')
        ).values('hexagon_id', 'year', 'month', 'boundary_coords', 'appeal_type_ru').annotate(total=Count('id'))

        aggregates = {}

        for entry in grouped:
            key = (entry['hexagon_id'], entry['year'], entry['month'])
            if key not in aggregates:
                aggregates[key] = {
                    'count': 0,
                    'types': {},
                    'boundary_coords': entry['boundary_coords']
                }

            aggregates[key]['count'] += entry['total']
            appeal_type = entry['appeal_type_ru']
            aggregates[key]['types'][appeal_type] = aggregates[key]['types'].get(appeal_type, 0) + entry['total']

        # 2. year only (month=None)
        grouped_year = appeals.annotate(
            year=ExtractYear('creation_date')
        ).values('hexagon_id', 'year', 'boundary_coords', 'appeal_type_ru').annotate(total=Count('id'))

        for entry in grouped_year:
            key = (entry['hexagon_id'], entry['year'], None)
            if key not in aggregates:
                aggregates[key] = {
                    'count': 0,
                    'types': {},
                    'boundary_coords': entry['boundary_coords']
                }

            aggregates[key]['count'] += entry['total']
            appeal_type = entry['appeal_type_ru']
            aggregates[key]['types'][appeal_type] = aggregates[key]['types'].get(appeal_type, 0) + entry['total']

        # ✅ 3. all years & months (None, None)
        grouped_all = appeals.values('hexagon_id', 'boundary_coords', 'appeal_type_ru').annotate(total=Count('id'))

        for entry in grouped_all:
            key = (entry['hexagon_id'], None, None)
            if key not in aggregates:
                aggregates[key] = {
                    'count': 0,
                    'types': {},
                    'boundary_coords': entry['boundary_coords']
                }

            aggregates[key]['count'] += entry['total']
            appeal_type = entry['appeal_type_ru']
            aggregates[key]['types'][appeal_type] = aggregates[key]['types'].get(appeal_type, 0) + entry['total']

        # Save all
        for (hex_id, year, month), data in aggregates.items():
            HexagonAggregate.objects.update_or_create(
                hexagon_id=hex_id,
                year=year,
                month=month,
                defaults={
                    'count': data['count'],
                    'types': data['types'],
                    'boundary_coords': data['boundary_coords'],
                }
            )

        self.stdout.write(self.style.SUCCESS(f"✅ Aggregated {len(aggregates)} hexagons"))
