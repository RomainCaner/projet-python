from __future__ import annotations

from pathlib import Path
from typing import List

import numpy as np
import cv2


class FaceStore:
    """
    Encodage léger basé uniquement sur OpenCV :
    - Détection via Haar cascade.
    - Encodage = visage gris redimensionné (100x100) aplati/normalisé.
    """

    def __init__(self, images_dir: Path):
        self.images_dir = images_dir
        self.images_dir.mkdir(parents=True, exist_ok=True)
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.detector = cv2.CascadeClassifier(cascade_path)

    def save_image(self, student_id: str, image_bytes: bytes, extension: str = "jpg") -> Path:
        path = self.images_dir / f"{student_id}.{extension}"
        path.write_bytes(image_bytes)
        return path

    def _detect_faces(self, image_gray) -> list[tuple[int, int, int, int]]:
        faces = self.detector.detectMultiScale(image_gray, scaleFactor=1.1, minNeighbors=5)
        return faces.tolist() if hasattr(faces, "tolist") else list(faces)

    def _encode_face_region(self, image_gray, x: int, y: int, w: int, h: int) -> List[float]:
        roi = image_gray[y : y + h, x : x + w]
        resized = cv2.resize(roi, (100, 100))
        norm = resized.astype("float32") / 255.0
        return norm.flatten().tolist()

    def encode_image(self, image_path: Path) -> List[float]:
        image_bgr = cv2.imread(str(image_path))
        if image_bgr is None:
            raise RuntimeError(f"Impossible de lire l'image {image_path}.")
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        faces = self._detect_faces(gray)
        if not faces:
            raise RuntimeError("Aucun visage détecté sur la photo fournie.")
        x, y, w, h = faces[0]
        return self._encode_face_region(gray, x, y, w, h)

    def encode_faces_from_frame(self, frame_bgr, with_boxes: bool = False):
        """Détecte et encode tous les visages présents dans un frame BGR."""
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        faces = self._detect_faces(gray)
        items = []
        for (x, y, w, h) in faces:
            encoding = self._encode_face_region(gray, x, y, w, h)
            if with_boxes:
                items.append((encoding, (x, y, w, h)))
            else:
                items.append(encoding)
        return items

    @staticmethod
    def compute_distance(encoding1: List[float], encoding2: List[float]) -> float:
        """Calcule la distance euclidienne entre deux encodages"""
        vec1 = np.array(encoding1, dtype=np.float32)
        vec2 = np.array(encoding2, dtype=np.float32)
        return float(np.linalg.norm(vec1 - vec2))

    @staticmethod
    def compare(
        known_encodings: List[List[float]], face_to_check: List[float], tolerance: float = 0.6
    ) -> List[bool]:
        """
        Compare par distance euclidienne sur encodage flatten. Plus simple que face_recognition.
        """
        if not known_encodings:
            return []
        known = np.array(known_encodings, dtype=np.float32)
        target = np.array(face_to_check, dtype=np.float32)
        dists = np.linalg.norm(known - target, axis=1)
        return (dists < tolerance).tolist()
