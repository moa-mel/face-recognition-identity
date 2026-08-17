from django.urls import path
from face_recognition.views import FaceEnrollmentView


urlpatterns = [

    path("face/enroll/<uuid:user_id>/", FaceEnrollmentView.as_view(), name="enroll"),
]