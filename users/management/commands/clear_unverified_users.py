from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import EmailVerificationToken

class Command(BaseCommand):
    help = 'Удаляет пользователей с просроченными токенами'

    def handle(self, *args, **kwargs):
        expired_tokens = EmailVerificationToken.objects.filter(
            expires_at__lt=timezone.now()
        )

        for token in expired_tokens:
            user = token.user
            token.delete()
            user.delete()

        self.stdout.write("Удалены пользователи с просроченной верификацией")