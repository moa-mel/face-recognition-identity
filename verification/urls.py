from django.urls import path
from verification.views import VerifyIdentityView


urlpatterns = [
    path("verify-identity/", VerifyIdentityView.as_view(), name="verify-identity"),
]