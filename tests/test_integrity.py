"""Check that a public copy fails closed on changed inputs and output bytes."""

import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from data.fetch.fetch_inputs import InputError, records
from src.verify_outputs import OutputError, verify_outputs


class IntegrityTests(unittest.TestCase):
    def test_manifest_rejects_parent_directory_input(self):
        with tempfile.TemporaryDirectory() as temporary:
            manifest = Path(temporary) / "manifest.csv"
            fields = ("path", "source_url", "retrieved_at", "sha256", "bytes", "role",
                      "archive_path", "archive_member", "source_ref", "original_sha256")
            with manifest.open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerow({"path": "data/raw/../outside.zip", "role": "file_c_archive",
                                 "source_url": "https://files.usaspending.gov/frozen.zip",
                                 "retrieved_at": "2026-09-28T00:00:00Z",
                                 "sha256": "a" * 64, "bytes": "10"})
            with self.assertRaisesRegex(InputError, "unsafe input path"):
                records(manifest)

    def test_reviewed_output_hash_rejects_changed_csv(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "outputs/chart.csv"
            output.parent.mkdir()
            output.write_bytes(b"id,value\n1,7\n")
            receipts = [f"outputs/{folder}/verification.json"
                        for folder in ("chart_1", "chart_2", "figure_b")]
            for name in receipts:
                receipt = root / name
                receipt.parent.mkdir(parents=True)
                receipt.write_text(json.dumps({"technical_status": "PASS", "output_sha256": {}}))
            checks = root / "checks.json"
            checks.write_text(json.dumps({"schema_version": 2, "files": {
                "outputs/chart.csv": hashlib.sha256(output.read_bytes()).hexdigest()},
                "dynamic_receipts": receipts, "generated_unreleased": [],
                "released_files": ["outputs/chart.csv", *receipts]}))
            self.assertEqual(verify_outputs(root, checks), 1)
            output.write_bytes(b"id,value\n1,8\n")
            with self.assertRaisesRegex(OutputError, "SHA-256 differs"):
                verify_outputs(root, checks)


if __name__ == "__main__":
    unittest.main()
