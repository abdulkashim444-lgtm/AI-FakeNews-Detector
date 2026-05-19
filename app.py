"""
VeritasAI - Fake News Detection System
Flask Backend API
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

import anthropic
import os
import json
import re
import hashlib
import time
from datetime import datetime

# Load environment variables
load_dotenv()

# Flask App
app = Flask(__name__)

# CORS
CORS(app, resources={
    r"/api/*": {
        "origins": "*"
    }
})

# Rate Limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

limiter.init_app(app)

# API Key
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

print("API KEY LOADED:", ANTHROPIC_API_KEY)

if not ANTHROPIC_API_KEY:
    print("ERROR: ANTHROPIC_API_KEY not found in .env file")

# Anthropic Client
client = anthropic.Anthropic(
    api_key=ANTHROPIC_API_KEY
)

# Cache
_cache = {}
_analysis_history = []


def get_cache_key(text: str) -> str:
    return hashlib.md5(
        text.strip().lower().encode()
    ).hexdigest()


def build_analysis_prompt(text: str) -> str:
    return f"""
You are an expert fake news detector.

Analyze this news/article carefully.

Return ONLY valid JSON.

News:
{text[:3000]}

JSON Format:
{{
  "verdict": "FAKE",
  "confidence": 90,
  "summary": "Short explanation",
  "red_flags": [],
  "positive_indicators": []
}}
"""


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    })


@app.route("/api/analyze", methods=["POST"])
@limiter.limit("20 per minute")
def analyze():

    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "error": "No JSON data received"
            }), 400

        text = data.get("text", "").strip()
        url = data.get("url", "").strip()

        # Handle URL input
        if url and not text:
            text = f"Analyze this article URL: {url}"

        elif url and text:
            text = f"""
URL: {url}

{text}
"""

        if not text:
            return jsonify({
                "error": "No text provided"
            }), 400

        # Cache check
        cache_key = get_cache_key(text)

        if cache_key in _cache:
            cached = _cache[cache_key]
            cached["cached"] = True
            return jsonify(cached)

        print("Sending request to Claude...")

        # Claude API Request
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1000,
            temperature=0.2,
            messages=[
                {
                    "role": "user",
                    "content": build_analysis_prompt(text)
                }
            ]
        )

        print("Claude response received")

        raw_text = response.content[0].text

        print("RAW RESPONSE:")
        print(raw_text)

        # Clean markdown JSON
        clean_text = re.sub(
            r"```json|```",
            "",
            raw_text
        ).strip()

        # Parse JSON
        try:
            result = json.loads(clean_text)

        except Exception:
            result = {
                "verdict": "UNCERTAIN",
                "confidence": 50,
                "summary": clean_text,
                "red_flags": [],
                "positive_indicators": []
            }

        # Extra fields
        result["cached"] = False
        result["analyzed_at"] = datetime.utcnow().isoformat()

        # Save cache
        _cache[cache_key] = result

        # Save history
        _analysis_history.append({
            "verdict": result.get("verdict"),
            "confidence": result.get("confidence"),
            "timestamp": result["analyzed_at"],
            "preview": text[:100]
        })

        return jsonify(result)

    except anthropic.AuthenticationError as e:
        print("AUTH ERROR:", str(e))

        return jsonify({
            "error": "Invalid Anthropic API Key",
            "detail": str(e)
        }), 401

    except anthropic.APIError as e:
        print("ANTHROPIC API ERROR:", str(e))

        return jsonify({
            "error": "Anthropic API Error",
            "detail": str(e)
        }), 500

    except Exception as e:
        print("SERVER ERROR:", str(e))

        return jsonify({
            "error": "Internal Server Error",
            "detail": str(e)
        }), 500


@app.route("/api/history", methods=["GET"])
def history():
    return jsonify({
        "history": _analysis_history[-20:]
    })


@app.route("/api/stats", methods=["GET"])
def stats():

    total = len(_analysis_history)

    fake_count = len([
        x for x in _analysis_history
        if x.get("verdict") == "FAKE"
    ])

    real_count = len([
        x for x in _analysis_history
        if x.get("verdict") == "REAL"
    ])

    return jsonify({
        "total": total,
        "fake": fake_count,
        "real": real_count,
        "cache_size": len(_cache)
    })


@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(429)
def ratelimit(e):
    return jsonify({
        "error": "Too many requests"
    }), 429


if __name__ == "__main__":

    port = int(os.getenv("PORT", 5000))

    print(f"""
==================================
🚀 VERITAS AI BACKEND RUNNING
==================================
URL: http://localhost:{port}
==================================
""")

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )