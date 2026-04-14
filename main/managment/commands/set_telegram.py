from django.core.management.base import BaseCommand
from users.models import CustomUser


class Command(BaseCommand):
    help = 'Set telegram_id for user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)
        parser.add_argument('telegram_id', type=str)

    def handle(self, *args, **options):
        username = options['username']
        telegram_id = options['telegram_id']

        user = CustomUser.objects.get(username=username)
        user.telegram_id = telegram_id
        user.save()

        self.stdout.write(self.style.SUCCESS(f'Telegram ID set for {username}'))