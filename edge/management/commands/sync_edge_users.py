from django.core.management.base import BaseCommand, CommandError

from edge.sync import sync_users


class Command(BaseCommand):
    help = (
        "Pull the latest users/face embeddings from the central server "
        "(CENTRAL_API_URL) into this edge node's local database. "
        "Intended to be run on a schedule (cron/systemd timer) on-prem."
    )

    def handle(self, *args, **options):
        try:
            count = sync_users()
        except Exception as exc:
            raise CommandError(f"Edge sync failed: {exc}")

        self.stdout.write(
            self.style.SUCCESS(f"Synced {count} user(s) from central server.")
        )
