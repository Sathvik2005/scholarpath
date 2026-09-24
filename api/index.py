"""
Vercel entry point. Vercel's Python runtime serves the ASGI `app` in this
file as a serverless function; vercel.json routes the API paths here.
The backend lives in ../backend -- this just puts it on the import path.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.main import app  # noqa: E402,F401  (Vercel looks for this `app` symbol)
