from django.urls import path
from eid.views import GenerateEIDView, VerifyEIDView


urlpatterns = [
    path(
        "<uuid:user_id>/generate/", GenerateEIDView.as_view(), name="generate-eid"
    ),
    path(
        "eid/verify/<str:qr_token>/", VerifyEIDView.as_view(), name="verify-eid"
    ),


]