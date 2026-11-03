"""Serve temporary agent artifacts with a browsable root."""

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class ArtifactHandler(SimpleHTTPRequestHandler):
    """Always list the root; serve branch previews normally."""

    def send_head(self):
        root = Path(self.directory).resolve()
        path = Path(self.translate_path(self.path))
        candidates = [path]
        if path.is_dir():
            candidates.extend(path / name for name in ("index.html", "index.htm"))
        try:
            if any(not candidate.resolve().is_relative_to(root) for candidate in candidates):
                self.send_error(403, "Path outside artifact root")
                return None
        except (OSError, RuntimeError):
            self.send_error(403, "Invalid artifact path")
            return None
        if path == root:
            return self.list_directory(str(root))
        return super().send_head()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--directory", default="/tmp/artifacts")
    args = parser.parse_args()
    handler = partial(ArtifactHandler, directory=str(Path(args.directory).resolve()))
    with ThreadingHTTPServer(("0.0.0.0", args.port), handler) as server:
        server.serve_forever()
