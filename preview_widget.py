"""Local web viewer for prepared R6 model data"""

import json
import mimetypes
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QColor
from PySide6.QtWebEngineWidgets import QWebEngineView

from app_runtime import resource_directory

class PreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.viewer_root = resource_directory() / "viewer"
        self.model_root = None
        self.manifest = None
        self.token = uuid.uuid4().hex

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel("Select an operator and click Load Preview.")
        self.view = QWebEngineView()
        self.view.page().setBackgroundColor(QColor("#24282d"))
        self.view.setStyleSheet("background-color: #24282d;")
        self.view.setHtml("<html><body style='margin: 0; background: #24282d;'></body></html>")
        layout.addWidget(self.label)
        layout.addWidget(self.view, 1)

        owner = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                path = unquote(urlsplit(self.path).path)
                prefix = f"/{owner.token}/"
                if not path.startswith(prefix):
                    self.send_error(404)
                    return

                relative = path[len(prefix):]
                try:
                    if relative == "manifest.json":
                        if owner.manifest is None:
                            self.send_error(404)
                            return
                        payload = json.dumps(owner.manifest).encode("utf-8")
                        content_type = "application/json"
                    else:
                        category, separator, filename = relative.partition("/")
                        roots = {
                            "viewer": owner.viewer_root,
                            "model": owner.model_root
                        }
                        root = roots.get(category)
                        if not separator or root is None:
                            self.send_error(404)
                            return

                        root = root.resolve()
                        target = (root / filename).resolve()
                        if not target.is_relative_to(root) or not target.is_file():
                            self.send_error(404)
                            return

                        payload = target.read_bytes()
                        content_type = "text/javascript" if target.suffix == ".js" else mimetypes.guess_type(target.name)[0] or "application/octet-stream"

                    self.send_response(200)
                    self.send_header("Content-Type", content_type)
                    self.send_header("Content-Length", str(len(payload)))
                    self.send_header("Cache-Control", "no-store")
                    self.end_headers()
                    self.wfile.write(payload)
                except OSError:
                    self.send_error(404)
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def setText(self, text):
        self.label.setText(text)
        self.view.setHtml("<body style='background: #24282d'></body>")

    def load_manifest(self, path):
        path = Path(path).resolve()
        document = json.loads(path.read_text(encoding="utf-8"))
        root = path.parent

        models = []
        for relative in document["models"]:
            model = (root / relative).resolve()
            if not model.is_relative_to(root) or not model.is_file():
                raise ValueError(f"Invalid preview model: {relative}")
            models.append(f"/{self.token}/model/{quote(relative, safe='/')}")

        if not models:
            raise ValueError("Preview contains no models")

        self.model_root = root
        self.manifest = {
            "name": document["operator_name"],
            "models": models
        }
        self.label.setText(f"{document['operator_name']} - basic glTF material preview")
        port = self.server.server_address[1]
        self.view.load(QUrl(f"http://127.0.0.1:{port}/{self.token}/viewer/index.html"))

    def shutdown(self):
        self.server.shutdown()
        self.server.server_close()