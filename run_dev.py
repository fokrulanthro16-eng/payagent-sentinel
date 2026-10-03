"""Unified development orchestrator: starts FastAPI (:8000) and Vite React (:5173)."""
import os
import subprocess
import sys
import time
import signal

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")


def main():
    print("=" * 70)
    print(" PayAgent-Sentinel: Dual-Server Orchestrator")
    print(" Track: Agentic Commerce & PayPal + AI (2026)")
    print("=" * 70)
    print(f"[1/2] Launching FastAPI Backend on http://localhost:8000 ...")
    backend_cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
    backend_proc = subprocess.Popen(backend_cmd, cwd=BACKEND_DIR)

    print(f"[2/2] Launching Vite Frontend Cockpit on http://localhost:5173 ...")
    # On Windows npm is npm.cmd
    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
    frontend_proc = subprocess.Popen([npm_cmd, "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"], cwd=FRONTEND_DIR)

    print("\n>>> System operational:")
    print("    - REST API Docs:    http://localhost:8000/docs")
    print("    - SSE Telemetry:    http://localhost:8000/api/v1/telemetry/stream")
    print("    - Mission Cockpit:  http://localhost:5173")
    print("\nPress Ctrl+C to terminate both servers.\n")

    try:
        while True:
            time.sleep(1)
            if backend_proc.poll() is not None:
                print("Backend terminated unexpectedly.")
                break
            if frontend_proc.poll() is not None:
                print("Frontend terminated unexpectedly.")
                break
    except KeyboardInterrupt:
        print("\nShutting down PayAgent-Sentinel services...")
    finally:
        backend_proc.terminate()
        frontend_proc.terminate()
        print("Done.")


if __name__ == "__main__":
    main()
