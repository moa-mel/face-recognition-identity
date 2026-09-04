import os

import cv2
import numpy as np

from insightface.app import FaceAnalysis

# Smaller detection sizes are dramatically faster on CPU. 640 is the insightface
# default; 320 is roughly 3-4x faster and fine for close-up selfie verification.
_DET_SIZE = int(os.environ.get("FACE_DET_SIZE", "640"))

# Downscale anything larger than this (longest side, px) before running the
# model. A full-res phone photo decodes to ~30-40 MB in memory per copy and
# gives the detector nothing extra over a ~1280px image.
_MAX_SIDE = int(os.environ.get("FACE_MAX_IMAGE_SIDE", "1280"))


class FaceEmbeddingService:
    """
    Service for extracting face embeddings from images.
    """
    def __init__(self):
        self.app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
        # ctx_id < 0 selects CPU (there is no GPU on the deployment target).
        self.app.prepare(ctx_id=-1, det_size=(_DET_SIZE, _DET_SIZE))

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
        image_array = np.frombuffer(image_bytes, np.uint8)

        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("Invalid image")

        image = self._downscale(image)

        faces = self.app.get(image)

        if not faces:
            raise ValueError("No face detected")

        if len(faces) > 1:
            raise ValueError("Multiple faces detected")

        face = faces[0]

        embedding = face.embedding

        embedding = embedding / np.linalg.norm(
            embedding
        )

        return embedding.tolist()


_face_service = None


def get_face_service():
    """
    Return a process-wide FaceEmbeddingService, loading the model on first use.
    """
    global _face_service

    if _face_service is None:
        _face_service = FaceEmbeddingService()

    return _face_service