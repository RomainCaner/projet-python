# pyright: reportMissingImports=false
from __future__ import annotations

from pathlib import Path
from typing import Optional

try:
    import cv2
except ImportError:  # pragma: no cover
    cv2 = None


class CameraService:
    def __init__(self, fallback_image: Optional[Path] = None):
        self.fallback_image = fallback_image

    def capture_frame(self, camera_index: int = 0, delay_ms: int = 0):
        if cv2 is None:
            raise RuntimeError("OpenCV n'est pas disponible sur cette machine.")
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            cap.release()
            return self._read_fallback()
        if delay_ms > 0:
            # On laisse la caméra "s'éveiller" puis on jette les frames pendant le délai
            cv2.waitKey(delay_ms)
        success, frame = cap.read()
        cap.release()
        if success:
            return frame
        return self._read_fallback()

    def _read_fallback(self):
        if self.fallback_image and self.fallback_image.exists():
            return cv2.imread(str(self.fallback_image))
        raise RuntimeError("Impossible d'accéder à la caméra et pas d'image de secours fournie.")

    @staticmethod
    def save_frame(frame, destination: Path):
        if cv2 is None:
            raise RuntimeError("OpenCV requis pour sauvegarder une capture.")
        cv2.imwrite(str(destination), frame)
