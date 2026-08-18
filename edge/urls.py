from django.urls import path

from edge.views import EdgeSyncUsersView, EdgeUserListView, EdgeVerifyView

urlpatterns = [
    path("users/", EdgeUserListView.as_view(), name="edge-users-sync"),
    path("verify/", EdgeVerifyView.as_view(), name="edge-verify"),
    path("edge/users/", EdgeSyncUsersView.as_view(), name="edge-sync-users"),
]
