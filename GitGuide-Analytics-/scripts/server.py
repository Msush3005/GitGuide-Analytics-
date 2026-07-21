"""
GitGuide Analytics - Backend API & Dashboard Server
Provides REST API endpoints for dataset metrics and pipeline execution,
and serves static web frontend assets.

Usage:
    python scripts/server.py [port]
"""

import os
import sys
import json
import subprocess
import pandas as pd
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Resolve paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROCESSED_DATA_PATH = os.path.join(BASE_DIR, "output", "processed.csv")
RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw", "sample.csv")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
WORKFLOW_SCRIPT = os.path.join(BASE_DIR, "scripts", "data_workflow.py")


class AnalyticsAPIHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Serve static files from frontend directory
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def _send_json_response(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self._set_cors_headers()
        self.end_headers()
        response_bytes = json.dumps(data, indent=2).encode("utf-8")
        self.wfile.write(response_bytes)

    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        if path == "/api/data":
            self.handle_get_data()
        elif path == "/api/health":
            self.handle_get_health()
        else:
            # Fallback to static file server
            super().do_GET()

    def do_POST(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        if path == "/api/run-pipeline":
            self.handle_run_pipeline()
        else:
            self._send_json_response({"error": "Endpoint not found"}, 404)

    def handle_get_data(self):
        """Read processed dataset CSV and return JSON response."""
        try:
            if not os.path.exists(PROCESSED_DATA_PATH):
                # Run pipeline to generate initial processed data if missing
                subprocess.run([sys.executable, WORKFLOW_SCRIPT], check=True)

            df = pd.read_csv(PROCESSED_DATA_PATH)
            
            # Fill NaN values for clean JSON serialization
            df_clean = df.fillna("")
            records = df_clean.to_dict(orient="records")

            summary = {
                "total_rows": len(df),
                "total_commits": int(df["commits_count"].sum()) if "commits_count" in df.columns else 0,
                "total_prs": int(df["pull_requests_opened"].sum()) if "pull_requests_opened" in df.columns else 0,
                "total_contributions": int(df["total_contributions"].sum()) if "total_contributions" in df.columns else 0,
                "maintainer_count": int((df["contributor_role"] == "Maintainer").sum()) if "contributor_role" in df.columns else 0,
                "contributor_count": int((df["contributor_role"] == "Contributor").sum()) if "contributor_role" in df.columns else 0,
                "repositories": list(df["repository_name"].unique()) if "repository_name" in df.columns else [],
            }

            response = {
                "status": "success",
                "summary": summary,
                "data": records
            }
            self._send_json_response(response)
        except Exception as e:
            self._send_json_response({"status": "error", "message": str(e)}, 500)

    def handle_get_health(self):
        """Return health status and data file metadata."""
        has_processed = os.path.exists(PROCESSED_DATA_PATH)
        has_raw = os.path.exists(RAW_DATA_PATH)
        
        health_info = {
            "status": "healthy",
            "server": "GitGuide Analytics API",
            "has_processed_data": has_processed,
            "has_raw_data": has_raw,
            "last_modified": os.path.getmtime(PROCESSED_DATA_PATH) if has_processed else None
        }
        self._send_json_response(health_info)

    def handle_run_pipeline(self):
        """Execute data_workflow.py script and return log output."""
        try:
            result = subprocess.run(
                [sys.executable, WORKFLOW_SCRIPT],
                capture_output=True,
                text=True,
                encoding="utf-8"
            )
            
            if result.returncode == 0:
                # Re-read output metrics
                df = pd.read_csv(PROCESSED_DATA_PATH) if os.path.exists(PROCESSED_DATA_PATH) else None
                response = {
                    "status": "success",
                    "message": "✓ Pipeline executed successfully",
                    "output_log": result.stdout,
                    "rows_processed": len(df) if df is not None else 0
                }
                self._send_json_response(response)
            else:
                self._send_json_response({
                    "status": "error",
                    "message": "Pipeline execution failed",
                    "error_log": result.stderr
                }, 500)
        except Exception as e:
            self._send_json_response({"status": "error", "message": str(e)}, 500)


def run_server(port=8000):
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    server_address = ("", port)
    httpd = HTTPServer(server_address, AnalyticsAPIHandler)
    print("==================================================")
    print(f"GitGuide Analytics Dashboard Server Running!")
    print(f"Access UI at: http://localhost:{port}")
    print(f"API Endpoint: http://localhost:{port}/api/data")
    print("==================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()


if __name__ == "__main__":
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    run_server(port)
