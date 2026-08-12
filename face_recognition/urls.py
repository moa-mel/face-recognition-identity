from django.urls import path
from face_recognition.views import FaceEnrollmentView


urlpatterns = [

    path("face/enroll/", FaceEnrollmentView.as_view(), name="enroll"),
]