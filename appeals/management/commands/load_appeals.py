from django.core.management.base import BaseCommand
import pandas as pd
from appeals.models import Appeal

class Command(BaseCommand):
    help = 'Load appeals from CSV'

    def handle(self, *args, **kwargs):
        df = pd.read_csv('final_cleaned_appeals.csv')
        for _, row in df.iterrows():
            Appeal.objects.create(
                title=row['Title'],
                description=row['Description'],
                creation_date=row['StartedAt'],
                completion_date=row['CompletedAt'],
                status=row['Status'],
                process_status=row['ProcessStatus'],
                address=row['Address'],
                coord_x=row['CoordX'],
                coord_y=row['CoordY'],
                kind_of_appeal_id=row['KindOfAppealId'],
                category_id=None if pd.isna(row.get('CategoryId')) else int(row.get('CategoryId')),
                received_from=row.get('ReceivedFrom'),
                appeal_type_en=row.get('AppealType_en'),
                appeal_type_ru=row.get('AppealType_ru'),
                appeal_type_kk=row.get('AppealType_kk'),
                location=row.get('location'),
                hexagon_id=row.get('hexagon_id'),
            )
        self.stdout.write(self.style.SUCCESS("✅ Appeals successfully loaded."))
