# pyright: reportMissingImports=false
from __future__ import annotations

from pathlib import Path
from typing import Optional

try:
    import cv2
except ImportError:  # pragma: no cover
    cv2 = None


class CameraService:
    def __init__(self, fallback_image: Optional[Path] = None, camera_index: int = 0):
        self.fallback_image = fallback_image
        self.camera_index = camera_index
        self._cap: Optional[cv2.VideoCapture] = None
        self._is_opened = False

    def _ensure_camera_opened(self):
        """Ouvre la caméra si elle n'est pas déjà ouverte (optimisation performance)"""
        if cv2 is None:
            raise RuntimeError("OpenCV n'est pas disponible sur cette machine.")
        
        if self._cap is None or not self._cap.isOpened():
            self._cap = cv2.VideoCapture(self.camera_index)
            if not self._cap.isOpened():
                self._cap = None
                self._is_opened = False
                return False
            self._is_opened = True
            # Laisser la caméra se stabiliser (lire quelques frames)
            for _ in range(5):
                self._cap.read()
        return True

    def capture_frame(self, camera_index: int = 0, delay_ms: int = 0):
        """
        Capture une frame depuis la caméra (maintenant instantané!)
        
        Args:
            camera_index: Index de la caméra (ignoré si déjà ouverte)
            delay_ms: Délai supplémentaire avant capture (rarement nécessaire maintenant)
        """
        if cv2 is None:
            raise RuntimeError("OpenCV n'est pas disponible sur cette machine.")
        
        # Utiliser camera_index si différent de celui par défaut
        if camera_index != self.camera_index:
            self.release()
            self.camera_index = camera_index
        
        if not self._ensure_camera_opened():
            return self._read_fallback()
        
        if delay_ms > 0:
            cv2.waitKey(delay_ms)
        
        success, frame = self._cap.read()
        if success:
            return frame
        return self._read_fallback()

    def get_video_capture(self) -> cv2.VideoCapture:
        """
        Retourne l'objet VideoCapture pour un accès direct (flux continu)
        Utile pour les vues qui veulent gérer le flux elles-mêmes
        """
        if not self._ensure_camera_opened():
            raise RuntimeError("Impossible d'ouvrir la caméra")
        return self._cap

    def release(self):
        """Ferme explicitement la caméra"""
        if self._cap is not None:
            self._cap.release()
            self._cap = None
            self._is_opened = False

    def _read_fallback(self):
        if self.fallback_image and self.fallback_image.exists():
            return cv2.imread(str(self.fallback_image))
        raise RuntimeError("Impossible d'accéder à la caméra et pas d'image de secours fournie.")

    @staticmethod
    def save_frame(frame, destination: Path):
        if cv2 is None:
            raise RuntimeError("OpenCV requis pour sauvegarder une capture.")
        cv2.imwrite(str(destination), frame)
    
    def __del__(self):
        """Cleanup automatique lors de la destruction de l'objet"""
        self.release()
