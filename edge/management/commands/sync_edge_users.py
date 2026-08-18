from django.core.management.base import BaseCommand, CommandError

from edge.sync import sync_users


class Command(BaseCommand):
    help = "Sync enrolled users from the central API to the edge database"

    def handle(self, *args, **options):
        try:
            count = sync_users()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully synced {count} users."
                )
            )

        except Exception as exc:
            self.stdout.write(
                self.style.ERROR(
                    f"Edge user sync failed: {exc}"
                )
            )
