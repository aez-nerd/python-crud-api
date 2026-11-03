import unittest
import tempfile
import os
import json
import threading
import urllib.request
import urllib.error
from http.server import ThreadingHTTPServer

temp_dir = tempfile.mkdtemp()
os.environ["DATA_FILE"] = os.path.join(temp_dir, "test_messages.json")

import app


class TestPythonCrudAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), app.APIHandler)
        cls.port = cls.server.server_port
        cls.base_url = f"http://127.0.0.1:{cls.port}"
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        if app.DATA_FILE.exists():
            app.DATA_FILE.unlink()

    def request_json(self, method, path, payload=None):
        url = f"{self.base_url}{path}"
        data = None
        headers = {}
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode("utf-8"))

    def test_01_health_check(self):
        status, body = self.request_json("GET", "/health")
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "active")
        self.assertEqual(body["service"], "Backend API")

    def test_02_post_valid_message(self):
        status, body = self.request_json("POST", "/messages", {"message": "Uji otomatis CI/CD"})
        self.assertEqual(status, 201)
        self.assertEqual(body["status"], "created")
        self.assertEqual(body["message"]["message"], "Uji otomatis CI/CD")
        self.assertIn("created_at", body["message"])

    def test_03_post_empty_message_rejected(self):
        status, body = self.request_json("POST", "/messages", {"message": "   "})
        self.assertEqual(status, 400)
        self.assertEqual(body["error"], "message must not be empty")

    def test_04_post_over_500_chars_rejected(self):
        status, body = self.request_json("POST", "/messages", {"message": "A" * 501})
        self.assertEqual(status, 400)
        self.assertEqual(body["error"], "message must be 500 characters or fewer")

    def test_05_get_by_id_and_query_filter(self):
        self.request_json("POST", "/messages", {"message": "Pesan pertama Jenkins"})
        self.request_json("POST", "/messages", {"message": "Pesan kedua Docker"})

        status, detail = self.request_json("GET", "/messages/1")
        self.assertEqual(status, 200)
        self.assertEqual(detail["index"], 1)
        self.assertEqual(detail["item"]["message"], "Pesan kedua Docker")

        status_404, _ = self.request_json("GET", "/messages/99")
        self.assertEqual(status_404, 404)

        status_f, filtered = self.request_json("GET", "/messages?search=docker")
        self.assertEqual(status_f, 200)
        self.assertEqual(filtered["total"], 1)
        self.assertEqual(filtered["messages"][0]["message"], "Pesan kedua Docker")

    def test_06_delete_message(self):
        self.request_json("POST", "/messages", {"message": "Pesan akan dihapus"})
        status, body = self.request_json("DELETE", "/messages?index=0")
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "deleted")

        status_404, _ = self.request_json("DELETE", "/messages?index=999")
        self.assertEqual(status_404, 404)


if __name__ == "__main__":
    unittest.main(verbosity=2)
