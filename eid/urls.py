from django.urls import path
from eid.views import GenerateEIDView


urlpatterns = [
    path(
        "<uuid:user_id>/generate/", GenerateEIDView.as_view(), name="generate-eid"
    ),

]