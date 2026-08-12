import cv2
import numpy as np

from insightface.app import FaceAnalysis


class FaceEmbeddingService:
    """
    Service for extracting face embeddings from images.
    """
    def __init__(self):
        self.app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
        self.app.prepare(ctx_id=0, det_size=(640, 640))

    def get_embedding(self, image_bytes):
        image_array = np.frombuffer(image_bytes, np.uint8)

        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("Invalid image")

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