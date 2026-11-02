"""HTTP regression tests for the shared artifact server."""

from functools import partial
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".chezmoitemplates" / "agent-static"))
from server import ArtifactHandler


class ArtifactServerTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "artifacts"
        self.root.mkdir()
        branch = self.root / "feature-preview"
        branch.mkdir()
        (branch / "index.html").write_text("<h1>Preview</h1>")
        (self.root / "index.html").write_text("Root index must not hide folders")
        handler = partial(ArtifactHandler, directory=str(self.root))
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self.thread = Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop_server)

    def stop_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def request(self, path, method="GET"):
        connection = HTTPConnection(*self.server.server_address, timeout=5)
        try:
            connection.request(method, path)
            response = connection.getresponse()
            return response.status, response.read(), dict(response.getheaders())
        finally:
            connection.close()

    def test_root_lists_folders_even_with_index(self):
        status, body, headers = self.request("/")
        self.assertEqual(status, 200)
        self.assertIn(b'href="feature-preview/"', body)
        self.assertNotIn(b"Root index must not hide folders", body)
        self.assertEqual(headers["Cache-Control"], "no-store")
        (self.root / "new-branch").mkdir()
        self.assertIn(b'new-branch/', self.request("/?refresh=1")[1])

    def test_branch_index_and_head(self):
        self.assertEqual(self.request("/feature-preview/")[:2], (200, b"<h1>Preview</h1>"))
        self.assertEqual(self.request("/", "HEAD")[:2], (200, b""))

    def test_directory_without_index_is_browsable(self):
        (self.root / "reports").mkdir()
        (self.root / "reports" / "report.txt").write_text("report")
        self.assertIn(b'href="report.txt"', self.request("/reports/")[1])

    def test_missing_file(self):
        self.assertEqual(self.request("/missing")[0], 404)

    def test_external_symlinks_are_not_served(self):
        outside = Path(self.temp.name) / "private.txt"
        outside.write_text("private")
        (self.root / "link.txt").symlink_to(outside)
        self.assertEqual(self.request("/link.txt")[0], 403)
        (self.root / "linked-index").mkdir()
        (self.root / "linked-index" / "index.html").symlink_to(outside)
        self.assertEqual(self.request("/linked-index/")[0], 403)


if __name__ == "__main__":
    unittest.main()
