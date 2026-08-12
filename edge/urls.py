from django.urls import path

from edge.views import EdgeUserListView, EdgeVerifyView

urlpatterns = [
    path("users/", EdgeUserListView.as_view(), name="edge-users-sync"),
    path("verify/", EdgeVerifyView.as_view(), name="edge-verify"),
]
