from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def test_cli_creates_output_files(tmp_path: Path) -> None:
    report_path = tmp_path / "report.csv"
    tx_path = tmp_path / "transactions.csv"

    cmd = [
        sys.executable,
        "-m",
        "sales_analysis.cli",
        "--report-path",
        str(report_path),
        "--transactions-path",
        str(tx_path),
    ]

    env = os.environ.copy()
    src_path = str((Path(__file__).resolve().parents[1] / "src"))
    env["PYTHONPATH"] = src_path + os.pathsep + env.get("PYTHONPATH", "")

    result = subprocess.run(cmd, capture_output=True, text=True, check=False, env=env)

    assert result.returncode == 0, result.stderr
    assert report_path.exists()
    assert tx_path.exists()
    assert "Sales Summary" in result.stdout
