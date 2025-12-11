from __future__ import annotations

import shutil
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Callable, Optional
from uuid import uuid4

import cv2
from PIL import Image, ImageTk

from services.camera import CameraService
from services.student_service import StudentService
from utils.paths import IMAGES_DIR

IMAGES_DIR.mkdir(parents=True, exist_ok=True)


class AddStudentView(ttk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        student_service: StudentService,
        camera_service: CameraService,
        on_back: Callable[[], None],
    ):
        super().__init__(master, padding=24)
        self.student_service = student_service
        self.camera_service = camera_service
        self.on_back = on_back
        self.selected_image: Optional[Path] = None
        self.preview_photo = None
        self.capture_delay_var = tk.IntVar(value=500)  # délai avant capture en ms

        self.columnconfigure(1, weight=1)

        ttk.Label(self, text="Ajout d'un étudiant", font=("Segoe UI", 18)).grid(
            row=0, column=0, columnspan=2, pady=(0, 24)
        )

        ttk.Label(self, text="Identifiant").grid(row=1, column=0, sticky="w")
        self.student_id_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.student_id_var).grid(
            row=1, column=1, sticky="ew", pady=4
        )

        ttk.Label(self, text="Prénom").grid(row=2, column=0, sticky="w")
        self.first_name_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.first_name_var).grid(
            row=2, column=1, sticky="ew", pady=4
        )

        ttk.Label(self, text="Nom").grid(row=3, column=0, sticky="w")
        self.last_name_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.last_name_var).grid(
            row=3, column=1, sticky="ew", pady=4
        )

        ttk.Label(self, text="Solde initial (€)").grid(row=4, column=0, sticky="w")
        self.balance_var = tk.StringVar(value="5.0")
        ttk.Entry(self, textvariable=self.balance_var).grid(
            row=4, column=1, sticky="ew", pady=4
        )

        ttk.Label(self, text="Photo").grid(row=5, column=0, sticky="w")
        status_frame = ttk.Frame(self)
        status_frame.grid(row=5, column=1, sticky="ew", pady=4)
        status_frame.columnconfigure(0, weight=1)
        self.photo_status = tk.StringVar(value="Aucune photo sélectionnée.")
        ttk.Label(status_frame, textvariable=self.photo_status).grid(
            row=0, column=0, sticky="w"
        )

        ttk.Label(self, text="Délai avant capture (ms)").grid(row=6, column=0, sticky="w")
        ttk.Spinbox(self, from_=0, to=5000, increment=100, textvariable=self.capture_delay_var).grid(
            row=6, column=1, sticky="w", pady=4
        )

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=7, column=0, columnspan=2, pady=(8, 0))
        ttk.Button(btn_frame, text="Capturer via webcam", command=self._capture_image).pack(
            side="left", padx=4
        )
        ttk.Button(btn_frame, text="Choisir un fichier…", command=self._import_image).pack(
            side="left", padx=4
        )
        ttk.Button(
            btn_frame,
            text="Mode prévisualisation continue (touche C)",
            command=self._start_live_preview,
        ).pack(side="left", padx=4)

        action_frame = ttk.Frame(self)
        action_frame.grid(row=8, column=0, columnspan=2, pady=(24, 0))
        ttk.Button(action_frame, text="Enregistrer", command=self._submit).pack(
            side="left", padx=4
        )
        ttk.Button(action_frame, text="Retour", command=self.on_back).pack(
            side="left", padx=4
        )

    def _require_student_id(self) -> str:
        student_id = self.student_id_var.get().strip()
        if not student_id:
            raise ValueError("Veuillez renseigner l'identifiant avant la capture.")
        return student_id

    def _capture_image(self):
        try:
            student_id = self._require_student_id()
        except ValueError as exc:
            messagebox.showwarning("Information", str(exc))
            return
        try:
            delay_ms = max(0, int(self.capture_delay_var.get()))
            frame = self.camera_service.capture_frame(delay_ms=delay_ms)
            self._show_preview(frame, student_id)
        except Exception as exc:  # pragma: no cover - dépend matériel
            messagebox.showerror("Caméra", str(exc))

    def _import_image(self):
        file_path = filedialog.askopenfilename(
            title="Sélectionner une image",
            filetypes=[("Images", "*.jpg;*.jpeg;*.png")],
        )
        if not file_path:
            return
        student_id = self.student_id_var.get().strip() or uuid4().hex[:8]
        destination = IMAGES_DIR / f"{student_id}{Path(file_path).suffix.lower()}"
        try:
            shutil.copy(Path(file_path), destination)
            self.selected_image = destination
            self.photo_status.set(f"Image importée : {destination.name}")
        except OSError as exc:
            messagebox.showerror("Fichier", f"Impossible de copier l'image : {exc}")

    def _submit(self):
        student_id = self.student_id_var.get().strip()
        first_name = self.first_name_var.get().strip()
        last_name = self.last_name_var.get().strip()
        if not all([student_id, first_name, last_name]):
            messagebox.showwarning("Champs manquants", "Merci de renseigner identité complète.")
            return
        if not self.selected_image:
            messagebox.showwarning("Photo manquante", "Veuillez capturer ou importer une photo.")
            return
        try:
            balance = float(self.balance_var.get())
        except ValueError:
            messagebox.showwarning("Solde invalide", "Le solde doit être un nombre.")
            return
        try:
            student = self.student_service.register_student(
                student_id=student_id,
                first_name=first_name,
                last_name=last_name,
                balance=balance,
                image_path=self.selected_image,
            )
        except Exception as exc:
            messagebox.showerror("Erreur", str(exc))
            return
        messagebox.showinfo(
            "Succès", f"{student.display_name} a été enregistré avec succès."
        )
        self._reset_form()

    def _reset_form(self):
        self.student_id_var.set("")
        self.first_name_var.set("")
        self.last_name_var.set("")
        self.balance_var.set("5.0")
        self.selected_image = None
        self.photo_status.set("Aucune photo sélectionnée.")

    def _show_preview(self, frame, student_id: str):
        """Affiche un aperçu et demande validation avant sauvegarde."""
        preview = tk.Toplevel(self)
        preview.title("Prévisualisation")

        # Convertir BGR -> RGB puis PhotoImage
        image_rgb = frame[:, :, ::-1]
        img = Image.fromarray(image_rgb)
        img = img.resize((min(640, img.width), int(img.height * min(640, img.width) / img.width)))
        photo = ImageTk.PhotoImage(img)
        self.preview_photo = photo  # éviter le GC

        label = ttk.Label(preview, image=photo)
        label.pack(padx=8, pady=8)

        def on_confirm():
            destination = IMAGES_DIR / f"{student_id}.jpg"
            try:
                self.camera_service.save_frame(frame, destination)
                self.selected_image = destination
                self.photo_status.set(f"Photo capturée : {destination.name}")
            except Exception as exc:  # pragma: no cover
                messagebox.showerror("Erreur", f"Sauvegarde impossible : {exc}")
            preview.destroy()

        def on_cancel():
            preview.destroy()

        btn_frame = ttk.Frame(preview)
        btn_frame.pack(pady=8)
        ttk.Button(btn_frame, text="Valider", command=on_confirm).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Annuler", command=on_cancel).pack(side="left", padx=4)

    def _start_live_preview(self):
        """Ouvre une fenêtre OpenCV en continu, capture sur la touche 'c'."""
        student_id = self.student_id_var.get().strip()
        if not student_id:
            messagebox.showwarning("Information", "Renseigne l'identifiant avant la capture.")
            return

        def run():
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                messagebox.showerror("Caméra", "Impossible d'ouvrir la caméra.")
                return
            captured_path = None
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                cv2.imshow("Prévisualisation (appuie sur 'c' pour capturer, 'q' pour quitter)", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("c"):
                    destination = IMAGES_DIR / f"{student_id}.jpg"
                    cv2.imwrite(str(destination), frame)
                    captured_path = destination
                    break
                if key == ord("q"):
                    break
            cap.release()
            cv2.destroyAllWindows()
            if captured_path:
                # Mettre à jour l'état dans le thread Tk
                self.after(
                    0,
                    lambda: (
                        setattr(self, "selected_image", captured_path),
                        self.photo_status.set(f"Photo capturée : {captured_path.name}"),
                    ),
                )

        # Lancer dans un thread léger pour ne pas bloquer Tk
        import threading

        threading.Thread(target=run, daemon=True).start()

