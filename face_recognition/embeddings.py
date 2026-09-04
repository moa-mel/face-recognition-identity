import os
import urllib.request

import cv2
import numpy as np

# Lightweight face pipeline using OpenCV's built-in models (no insightface /
# onnxruntime / scipy / scikit-image). Small enough to run in the web process.
#
#   YuNet  - face detection      (~230 KB)
#   SFace  - 128-d face embedding (~37 MB)
#
# Models are fetched on first use if missing, so local dev and Docker both work.

_MODEL_DIR = os.environ.get(
    "FACE_MODEL_DIR",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "models"),
)

_DETECTOR_FILE = "face_detection_yunet_2023mar.onnx"
_RECOGNIZER_FILE = "face_recognition_sface_2021dec.onnx"

_MODEL_URLS = {
    _DETECTOR_FILE: (
        "https://github.com/opencv/opencv_zoo/raw/main/models/"
        "face_detection_yunet/face_detection_yunet_2023mar.onnx"
    ),
    _RECOGNIZER_FILE: (
        "https://github.com/opencv/opencv_zoo/raw/main/models/"
        "face_recognition_sface/face_recognition_sface_2021dec.onnx"
    ),
}

# Downscale anything larger than this (longest side, px) before detection.
_MAX_SIDE = int(os.environ.get("FACE_MAX_IMAGE_SIDE", "1024"))

# YuNet detection confidence.
_DET_SCORE = float(os.environ.get("FACE_DET_SCORE", "0.8"))


def _model_path(filename):
    path = os.path.join(_MODEL_DIR, filename)

    if not os.path.exists(path):
        os.makedirs(_MODEL_DIR, exist_ok=True)
        urllib.request.urlretrieve(_MODEL_URLS[filename], path)

    return path


class FaceEmbeddingService:
    """
    Extract a normalized 128-d face embedding from an image.

    Keeps the ``get_embedding(image_bytes) -> list[float]`` interface the rest
    of the codebase expects.
    """

    def __init__(self):
        self.detector = cv2.FaceDetectorYN.create(
            _model_path(_DETECTOR_FILE),
            "",
            (320, 320),
            score_threshold=_DET_SCORE,
        )
        self.recognizer = cv2.FaceRecognizerSF.create(
            _model_path(_RECOGNIZER_FILE),
            "",
        )

    @staticmethod
    def _downscale(image):
        height, width = image.shape[:2]
        longest = max(height, width)

        if longest <= _MAX_SIDE:
            return image

        scale = _MAX_SIDE / longest

        return cv2.resize(
            image,
            (int(width * scale), int(height * scale)),
            interpolation=cv2.INTER_AREA,
        )

    def get_embedding(self, image_bytes):
        array = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(array, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("Invalid image")

        image = self._downscale(image)

        height, width = image.shape[:2]
        self.detector.setInputSize((width, height))

        _, faces = self.detector.detect(image)

        if faces is None or len(faces) == 0:
            raise ValueError("No face detected")

        if len(faces) > 1:
            raise ValueError("Multiple faces detected")

        aligned = self.recognizer.alignCrop(image, faces[0])
        feature = self.recognizer.feature(aligned).flatten()

        feature = feature / np.linalg.norm(feature)

        return feature.tolist()


_face_service = None


def get_face_service():
    """
    Return a process-wide FaceEmbeddingService, loading the models on first use.
    """
    global _face_service

    if _face_service is None:
        _face_service = FaceEmbeddingService()

    return _face_service
