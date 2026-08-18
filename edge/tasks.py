from celery import shared_task

from .sync import sync_users


@shared_task
def sync_edge_users():
    return sync_users()