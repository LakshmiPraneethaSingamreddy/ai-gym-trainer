import cv2
import threading

class Camera:
    def __init__(self, src=0, width=640, height=480):
        self.cap = cv2.VideoCapture(src)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self._frame = None
        self._lock = threading.Lock()
        self._running = True
        # Background thread continuously drains the camera buffer so
        # read() always returns the latest frame, not a stale buffered one.
        self._thread = threading.Thread(target=self._reader, daemon=True)
        self._thread.start()

    def _reader(self):
        while self._running:
            success, frame = self.cap.read()
            if success:
                with self._lock:
                    self._frame = frame

    def read(self):
        with self._lock:
            return self._frame.copy() if self._frame is not None else None

    def release(self):
        self._running = False
        self._thread.join(timeout=1)
        self.cap.release()
