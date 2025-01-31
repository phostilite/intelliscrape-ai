from django.core.management.base import BaseCommand
from profile_finder.models import Source
from django.db import transaction

class Command(BaseCommand):
    help = 'Populates the Source model with predefined sources'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing sources before creating new ones',
        )

    def handle(self, *args, **kwargs):
        sources = [
            {
                'name': 'LinkedIn',
                'domain': 'linkedin.com',
                'priority': 100,
            },
            {
                'name': 'GitHub',
                'domain': 'github.com',
                'priority': 90,
            },
            {
                'name': 'Twitter',
                'domain': 'twitter.com',
                'priority': 80,
            },
            {
                'name': 'Medium',
                'domain': 'medium.com',
                'priority': 70,
            },
            {
                'name': 'Stack Overflow',
                'domain': 'stackoverflow.com',
                'priority': 65,
            },
            {
                'name': 'Dev.to',
                'domain': 'dev.to',
                'priority': 60,
            },
            {
                'name': 'Facebook',
                'domain': 'facebook.com',
                'priority': 50,
            },
            {
                'name': 'Wikipedia',
                'domain': 'wikipedia.org',
                'priority': 45,
            },
            {
                'name': 'YouTube',
                'domain': 'youtube.com',
                'priority': 40,
            },
            {
                'name': 'Research Gate',
                'domain': 'researchgate.net',
                'priority': 35,
            },
            {
                'name': 'Academia.edu',
                'domain': 'academia.edu',
                'priority': 30,
            },
            {
                'name': 'Google Scholar',
                'domain': 'scholar.google.com',
                'priority': 25,
            },
        ]

        try:
            with transaction.atomic():
                if kwargs['reset']:
                    self.stdout.write('Deleting existing sources...')
                    Source.objects.all().delete()

                created_count = 0
                updated_count = 0

                for source_data in sources:
                    source, created = Source.objects.update_or_create(
                        name=source_data['name'],
                        defaults={
                            'domain': source_data['domain'],
                            'priority': source_data['priority'],
                            'is_active': True,
                        }
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully populated sources: {created_count} created, {updated_count} updated'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error populating sources: {str(e)}')
            )
