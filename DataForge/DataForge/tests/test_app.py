import io
import unittest
import pandas as pd
from app import app

class DataForgeTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_health(self):
        r = self.client.get("/api/health")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json["success"])

    def test_sample_and_profile(self):
        r = self.client.get("/api/samples/students")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json["data"]["rows"], 120)
        p = self.client.get("/api/dataset/profile")
        self.assertEqual(p.status_code, 200)
        self.assertGreater(p.json["data"]["columns"], 0)

    def test_upload_validation(self):
        r = self.client.post("/api/upload", data={"file": (io.BytesIO(b"a,b\\n1,2\\n3,4\\n"), "tiny.csv")}, content_type="multipart/form-data")
        self.assertEqual(r.status_code, 200)
        bad = self.client.post("/api/upload", data={"file": (io.BytesIO(b"no"), "bad.txt")}, content_type="multipart/form-data")
        self.assertEqual(bad.status_code, 400)

    def test_generation_evaluation_privacy_and_download(self):
        self.client.get("/api/samples/customers")
        r = self.client.post("/api/generate", json={"rows": 30, "method": "statistical", "constraints": {"age": {"min": 18, "max": 65}}})
        self.assertEqual(r.status_code, 200, r.json)
        self.assertEqual(r.json["data"]["profile"]["rows"], 30)
        self.assertTrue((pd.DataFrame(r.json["data"]["preview"])["age"] >= 18).all())
        self.assertEqual(self.client.post("/api/evaluate", json={}).status_code, 200)
        self.assertEqual(self.client.post("/api/privacy/check", json={}).status_code, 200)
        self.assertEqual(self.client.get("/api/download/csv").status_code, 200)
        self.assertEqual(self.client.get("/api/reports/passport").status_code, 200)

    def test_iteration(self):
        self.client.get("/api/samples/students")
        self.client.post("/api/generate", json={"rows": 25, "method": "statistical"})
        r = self.client.post("/api/iterate", json={"rows": 25, "noise": .2})
        self.assertEqual(r.status_code, 200, r.json)
        self.assertEqual(r.json["data"]["generation"]["method"], "perturbed")

if __name__ == "__main__":
    unittest.main()
