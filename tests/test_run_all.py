"""Exercise the release entrypoint's advisory, strict, and hard-error results."""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO

import run_all


class RunAllModesTests(unittest.TestCase):
    def test_late_failure_restores_previous_output_tree(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            prior = root / "outputs/chart_1/comparison.csv"
            prior.parent.mkdir(parents=True)
            prior.write_text("reviewed\n")

            def change_chart(_):
                prior.write_text("partial\n")
                return {"interpretation_status": "WARN"}

            with (patch.object(run_all, "ROOT", root),
                  patch.object(run_all, "fetch_inputs", return_value={"verified": 51}),
                  patch.object(run_all, "build_chart_1", side_effect=change_chart),
                  patch.object(run_all, "build_chart_2", side_effect=ValueError("late failure")),
                  redirect_stdout(StringIO())):
                with self.assertRaisesRegex(ValueError, "late failure"):
                    run_all.run()
            self.assertEqual(prior.read_text(), "reviewed\n")

    def test_interpretation_warning_is_advisory_or_strict(self):
        warn = {"interpretation_status": "WARN"}
        with (patch.object(run_all, "fetch_inputs", return_value={"verified": 48}),
              patch.object(run_all, "build_chart_1", return_value=warn),
              patch.object(run_all, "build_chart_2", return_value=warn),
              patch.object(run_all, "build_facility_screen", return_value=(warn, {"status": "PASS"})),
              patch.object(run_all, "build_figure_b", return_value=warn),
              patch.object(run_all, "verify_outputs", return_value=26),
              redirect_stdout(StringIO())):
            self.assertEqual(run_all.run(), 0)
            self.assertEqual(run_all.run(strict_warnings=True), 1)

    def test_input_mismatch_is_a_hard_error(self):
        with (patch.object(run_all, "verify_inputs", side_effect=ValueError("frozen hash differs")),
              patch.object(sys, "argv", ["run_all.py", "--offline"]),
              redirect_stderr(StringIO())):
            self.assertEqual(run_all.main(), 2)


if __name__ == "__main__":
    unittest.main()
