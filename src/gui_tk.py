# src/gui_tk.py
"""
Tkinter GUI for Smart Attendance (prototype)

Features:
- Live webcam preview
- Start / Stop recognition
- Add student from current frame (saves to data/known_faces/<student_id>/)
- Shows recent recognized names
- Export CSV (calls src.db.export_session_csv if available)

Usage:
    python src/gui_tk.py

Dependencies:
- opencv-python
- Pillow
- face_recognition (optional, best with encodings available)
- PyYAML / dotenv not required for GUI to start
"""

import os
import time
import threading
import queue
import pickle
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np

try:
    import face_recognition

    FACE_RECOGNITION_AVAILABLE = True
except Exception:
    FACE_RECOGNITION_AVAILABLE = False

# Config defaults (will try to load config/config.yaml if present)
DEFAULT_CONFIG = {
    "match_threshold": 0.6,
    "cooldown_seconds": 30,
    "frame_skip": 2,
    "paths": {
        "db": "data/attendance.db",
        "encodings": "data/models/encodings.pkl",
        "unknowns": "data/unknowns/",
        "known_faces": "data/known_faces/",
    },
}

try:
    import yaml

    cfg_path = Path("config/config.yaml")
    if cfg_path.exists():
        with open(cfg_path, "r") as f:
            cfg = yaml.safe_load(f)
            # merge with defaults (only shallow merge needed here)
            DEFAULT_CONFIG.update(cfg or {})
except Exception:
    pass

CONFIG = DEFAULT_CONFIG


# helper: load encodings.pkl if available
def load_encodings(enc_path):
    enc_file = Path(enc_path)
    if not enc_file.exists():
        return None
    try:
        with open(enc_file, "rb") as f:
            encodings = pickle.load(f)
        # Expecting structure: {"student_ids": [...], "names": [...], "encodings": [np.array,...]}
        # Normalize to numpy arrays
        encs = encodings.get("encodings") if isinstance(encodings, dict) else None
        if encs is None:
            # old format - try to load as tuple/list
            return encodings
        encodings["encodings"] = [np.array(e) for e in encodings["encodings"]]
        return encodings
    except Exception as e:
        print("Failed to load encodings:", e)
        return None


def recognize_frame_with_encodings(frame_rgb, encodings, threshold=0.6):
    """
    frame_rgb: RGB image (H,W,3)
    encodings: dict with "encodings", "student_ids", "names"
    returns: list of detections dict: {student_id, name, distance, bbox}
    """
    detections = []
    if not FACE_RECOGNITION_AVAILABLE or encodings is None:
        return detections
    try:
        locations = face_recognition.face_locations(frame_rgb, model="hog")
        face_encs = face_recognition.face_encodings(frame_rgb, locations)
        known_encs = encodings.get("encodings", [])
        ids = encodings.get("student_ids", [])
        names = encodings.get("names", [])
        for loc, fe in zip(locations, face_encs):
            distances = (
                face_recognition.face_distance(known_encs, fe)
                if len(known_encs) > 0
                else []
            )
            if len(distances) > 0:
                min_i = int(np.argmin(distances))
                min_d = float(distances[min_i])
                if min_d <= threshold:
                    detections.append(
                        {
                            "student_id": ids[min_i] if ids else None,
                            "name": names[min_i]
                            if names
                            else (ids[min_i] if ids else "Unknown"),
                            "distance": min_d,
                            "bbox": loc,  # (top, right, bottom, left)
                        }
                    )
                else:
                    detections.append(
                        {
                            "student_id": None,
                            "name": None,
                            "distance": min_d,
                            "bbox": loc,
                        }
                    )
            else:
                detections.append(
                    {"student_id": None, "name": None, "distance": None, "bbox": loc}
                )
    except Exception as e:
        print("Error in recognition:", e)
    return detections


class TkRecognizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Attendance — Tkinter GUI")
        self._build_ui()

        # video capture
        self.cap = None
        self.running = False
        self.thread = None
        self.queue = queue.Queue()
        self.current_frame = None
        self.encodings = None
        self.load_encodings()

        self.recent_names = []  # simple list to show in UI
        self.last_marked = {}  # student_id -> timestamp for cooldown

        # frame skip control
        self.frame_count = 0
        self.frame_skip = CONFIG.get("frame_skip", 2)
        self.match_threshold = CONFIG.get("match_threshold", 0.6)
        self.cooldown_seconds = CONFIG.get("cooldown_seconds", 30)

    def _build_ui(self):
        # left: video
        main = ttk.Frame(self.root, padding=6)
        main.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        video_frame = ttk.LabelFrame(main, text="Live Camera")
        video_frame.grid(row=0, column=0, sticky="nsew")
        video_frame.columnconfigure(0, weight=1)
        video_frame.rowconfigure(0, weight=1)

        self.video_label = ttk.Label(video_frame)
        self.video_label.grid(row=0, column=0)

        # right side: controls
        ctrl_frame = ttk.Frame(main, padding=(8, 0))
        ctrl_frame.grid(row=0, column=1, sticky="ns")

        self.start_btn = ttk.Button(ctrl_frame, text="Start", command=self.start)
        self.start_btn.grid(row=0, column=0, sticky="ew", pady=4)

        self.stop_btn = ttk.Button(
            ctrl_frame, text="Stop", command=self.stop, state="disabled"
        )
        self.stop_btn.grid(row=1, column=0, sticky="ew", pady=4)

        self.add_btn = ttk.Button(
            ctrl_frame, text="Add Student (from frame)", command=self.add_student_dialog
        )
        self.add_btn.grid(row=2, column=0, sticky="ew", pady=4)

        self.export_btn = ttk.Button(
            ctrl_frame, text="Export CSV", command=self.export_csv
        )
        self.export_btn.grid(row=3, column=0, sticky="ew", pady=4)

        # recent recognized list
        recent_label = ttk.Label(ctrl_frame, text="Recent recognized:")
        recent_label.grid(row=4, column=0, sticky="w", pady=(12, 0))
        self.recent_list = tk.Listbox(ctrl_frame, height=12, width=30)
        self.recent_list.grid(row=5, column=0, sticky="nsew", pady=4)

        # status bar
        self.status_var = tk.StringVar(value="Idle")
        status = ttk.Label(
            self.root, textvariable=self.status_var, relief="sunken", anchor="w"
        )
        status.grid(row=1, column=0, columnspan=2, sticky="ew")

    def load_encodings(self):
        enc_path = CONFIG["paths"].get("encodings", "data/models/encodings.pkl")
        self.encodings = load_encodings(enc_path)
        if self.encodings is None:
            self.status_var.set("No encodings found. You can still capture images.")
        else:
            self.status_var.set(
                f"Loaded encodings ({len(self.encodings.get('student_ids', []))} identities)"
            )

    def start(self):
        if self.running:
            return
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Camera error", "Cannot open webcam (index 0).")
            return
        self.running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status_var.set("Recognition running...")
        self.thread = threading.Thread(target=self._video_loop, daemon=True)
        self.thread.start()
        self.root.after(30, self._process_queue)

    def stop(self):
        if not self.running:
            return
        self.running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_var.set("Stopped")
        if self.cap:
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None

    def _video_loop(self):
        while self.running and self.cap:
            ret, frame = self.cap.read()
            if not ret:
                continue
            self.frame_count += 1
            self.current_frame = frame.copy()
            # show frame (convert to ImageTk)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # process recognition every N frames
            if self.frame_count % max(1, self.frame_skip) == 0:
                detections = []
                if FACE_RECOGNITION_AVAILABLE and self.encodings:
                    try:
                        detections = recognize_frame_with_encodings(
                            rgb, self.encodings, threshold=self.match_threshold
                        )
                    except Exception as e:
                        print("Recognition error:", e)
                # annotate frame with boxes and names
                annotated = frame.copy()
                for det in detections:
                    bbox = det.get("bbox")
                    if bbox:
                        top, right, bottom, left = bbox
                        cv2.rectangle(
                            annotated, (left, top), (right, bottom), (0, 255, 0), 2
                        )
                        name = det.get("name") or "Unknown"
                        cv2.putText(
                            annotated,
                            name,
                            (left, top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (0, 255, 0),
                            2,
                        )
                        # if recognized and not in cooldown, add to recent list
                        sid = det.get("student_id")
                        if sid:
                            now = time.time()
                            last = self.last_marked.get(sid, 0)
                            if now - last > self.cooldown_seconds:
                                self.last_marked[sid] = now
                                display = f"{det.get('name')} ({sid}) @ {datetime.now().strftime('%H:%M:%S')}"
                                self._add_recent(display)
                # push annotated to queue for display
                display_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
            else:
                display_rgb = rgb
            # convert to PIL Image
            img = Image.fromarray(display_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            # put PIL ImageTk onto queue for UI thread
            try:
                # keep only latest frame in queue
                while not self.queue.empty():
                    try:
                        self.queue.get_nowait()
                    except Exception:
                        break
                self.queue.put(imgtk)
            except Exception:
                pass
            # sleep a bit
            time.sleep(0.03)

    def _void solve(int n, vector<int> &arr)
    {
        if(n == 1) return;
        solve(n-1,arr);
    }process_queue(self):
        try:
            imgtk = self.queue.get_nowait()
        except queue.Empty:
            imgtk = None
        if imgtk:
            # `image` attribute must be kept referenced or tkinter will GC it
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
        if self.running:
            self.root.after(30, self._process_queue)

    def _add_recent(self, text):
        # add to top of recent list, keep only last 20
        self.recent_names.insert(0, text)
        self.recent_list.insert(0, text)
        if len(self.recent_names) > 20:
            self.recent_names = self.recent_names[:20]
            self.recent_list.delete(20, tk.END)

    def add_student_dialog(self):
        # Save the current frame to data/known_faces/<student_id>/
        if self.current_frame is None:
            messagebox.showwarning("No frame", "No frame available to capture.")
            return
        sid = simpledialog.askstring(
            "Student ID", "Enter student ID (unique):", parent=self.root
        )
        if not sid:
            return
        name = simpledialog.askstring(
            "Name", "Enter student name (optional):", parent=self.root
        )
        # ensure folder
        known_dir = Path(CONFIG["paths"].get("known_faces", "data/known_faces"))
        dest = known_dir / sid
        dest.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = dest / f"{sid}_{ts}.jpg"
        # save current frame (BGR) as jpg
        try:
            cv2.imwrite(str(filename), self.current_frame)
            messagebox.showinfo("Saved", f"Saved {filename}")
            # After capturing, optionally re-run encoding script externally (Coder 2)
            self.status_var.set(
                f"Saved image for {sid}. Run encode_faces.py to update encodings."
            )
        except Exception as e:
            messagebox.showerror("Save failed", f"Could not save image: {e}")

    def export_csv(self):
        # Try to call src.db.export_session_csv if available
        try:
            from src import (
                db as dbmod,
            )  # expects src/db.py to implement export_session_csv

            # ask session id
            session_id = simpledialog.askstring(
                "Export CSV", "Enter session id to export:", parent=self.root
            )
            if not session_id:
                return
            out_path = filedialog.asksaveasfilename(
                defaultextension=".csv", filetypes=[("CSV files", "*.csv")]
            )
            if not out_path:
                return
            dbmod.export_session_csv(
                CONFIG["paths"].get("db", "data/attendance.db"), session_id, out_path
            )
            messagebox.showinfo(
                "Exported", f"Exported session {session_id} to {out_path}"
            )
        except Exception as e:
            messagebox.showwarning(
                "Export unavailable",
                "DB export not available. Ensure src/db.py implements export_session_csv.\n\n"
                + str(e),
            )


def main():
    root = tk.Tk()
    app = TkRecognizerGUI(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.stop(), root.destroy()))
    root.geometry("1000x600")
    root.mainloop()


if __name__ == "__main__":
    main()
