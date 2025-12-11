from __future__ import annotations

import datetime as dt
import time
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional

import cv2
from PIL import Image, ImageTk

from services.camera import CameraService
from services.student_service import StudentService
from services.face_store import FaceStore


class AccessControlView(ttk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        student_service: StudentService,
        camera_service: CameraService,
        face_store: FaceStore,
        on_back: Callable[[], None],
        debit_amount: float = 1.0,
    ):
        super().__init__(master, padding=24)
        self.student_service = student_service
        self.camera_service = camera_service
        self.face_store = face_store
        self.on_back = on_back
        self.debit_amount = debit_amount
        self._after_id: Optional[str] = None
        self._running = True
        self._preview_image = None
        self._current_frame = None
        self._last_detection_time = 0
        self._cooldown_seconds = 3  # Évite de débiter plusieurs fois le même étudiant
        
        # Ouvrir la caméra une seule fois pour flux continu
        self._cap = cv2.VideoCapture(0)
        if not self._cap.isOpened():
            messagebox.showerror("Erreur", "Impossible d'ouvrir la caméra")
            raise RuntimeError("Caméra non disponible")

        # En-tête avec titre et bouton retour
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", pady=(0, 12))
        
        ttk.Label(header_frame, text="Contrôle d'accès - Reconnaissance en continu", font=("Segoe UI", 18)).pack(side="left")
        ttk.Button(header_frame, text="← Retour au menu", command=self._handle_back, width=20).pack(side="right")

        # Canvas de prévisualisation caméra
        self.preview_label = ttk.Label(self, text="Chargement de la caméra...")
        self.preview_label.pack(pady=8)

        # Statut
        self.status_var = tk.StringVar(value="En attente - Positionnez-vous devant la caméra...")
        ttk.Label(self, textvariable=self.status_var, font=("Segoe UI", 12, "bold")).pack(pady=8)

        # Dernier événement
        self.last_event_var = tk.StringVar(value="Aucun passage détecté.")
        ttk.Label(self, textvariable=self.last_event_var, font=("Segoe UI", 10)).pack(pady=4)

        # Lancer la reconnaissance en continu
        self._update_preview_with_recognition()

    def _update_preview_with_recognition(self):
        """Met à jour la prévisualisation avec reconnaissance automatique en temps réel"""
        if not self._running:
            return
            
        try:
            # Lire la frame depuis la caméra ouverte (flux continu)
            ret, frame = self._cap.read()
            if not ret:
                self.status_var.set("Erreur de lecture caméra")
                return
                
            frame_display = frame.copy()
            current_time = time.time()
            
            # Détecter et reconnaître les visages sur chaque frame
            results = self.face_store.encode_faces_from_frame(frame, with_boxes=True)
            
            if results:
                # Analyser chaque visage détecté
                for encoding, (x, y, w, h) in results:
                    student = self.student_service.match_encoding(encoding, tolerance=15)
                    
                    if student:
                        # Visage reconnu - dessiner rectangle vert
                        cv2.rectangle(frame_display, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        cv2.putText(
                            frame_display,
                            student.display_name,
                            (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (0, 255, 0),
                            2,
                        )
                        
                        # Débiter le solde (avec cooldown pour éviter les doublons)
                        if current_time - self._last_detection_time > self._cooldown_seconds:
                            self._last_detection_time = current_time
                            updated = self.student_service.decrement_balance(
                                student.student_id, self.debit_amount
                            )
                            balance = (updated or student).balance
                            
                            if balance > 0:
                                self.status_var.set(
                                    f"✓ Accès autorisé : {student.display_name} | Solde : {balance:.2f} €"
                                )
                            else:
                                self.status_var.set(
                                    f"⚠ Solde insuffisant : {student.display_name} (0.00 €)"
                                )
                            
                            self.last_event_var.set(
                                f"Dernier passage : {student.display_name} à {dt.datetime.now():%H:%M:%S}"
                            )
                        else:
                            # Afficher l'état reconnu sans débiter
                            balance = student.balance
                            self.status_var.set(
                                f"Reconnu : {student.display_name} | Solde : {balance:.2f} €"
                            )
                    else:
                        # Visage non reconnu - dessiner rectangle rouge
                        cv2.rectangle(frame_display, (x, y), (x + w, y + h), (0, 0, 255), 2)
                        cv2.putText(
                            frame_display,
                            "INCONNU",
                            (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (0, 0, 255),
                            2,
                        )
                        if current_time - self._last_detection_time > self._cooldown_seconds:
                            self.status_var.set("✗ Visage non reconnu - Accès refusé")
            else:
                # Aucun visage détecté
                if current_time - self._last_detection_time > 2:
                    self.status_var.set("En attente - Positionnez-vous devant la caméra...")
            
            # Convertir et afficher la frame avec les overlays
            frame_rgb = cv2.cvtColor(frame_display, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (800, 600))  # Taille optimisée pour laisser place aux boutons
            img = Image.fromarray(frame_resized)
            self._preview_image = ImageTk.PhotoImage(image=img)
            self.preview_label.config(image=self._preview_image, text="")
            
        except Exception as exc:
            # Ne pas arrêter le flux pour une erreur temporaire
            print(f"Erreur temporaire : {exc}")
            
        # Rafraîchir toutes les 50ms (20 FPS) - flux continu
        if self._running:
            self._after_id = self.after(50, self._update_preview_with_recognition)

    def _handle_back(self):
        self.teardown()
        self.on_back()

    def teardown(self):
        """Arrête la prévisualisation et ferme la caméra"""
        self._running = False
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None
        if hasattr(self, '_cap') and self._cap is not None:
            self._cap.release()
            self._cap = None
