#!/usr/bin/env python3
"""
Health check server for keeping the bot alive on Render.com
"""

from flask import Flask, jsonify
from threading import Thread
import logging
import os

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)


@app.route("/")
def index():
    """Root endpoint for health check"""
    return """
    <html>
        <head><title>RAID SYSTEM Bot</title></head>
        <body>
            <h1>⚔️ RAID SYSTEM</h1>
            <p>Бот работает нормально!</p>
        </body>
    </html>
    """


@app.route("/health")
def health_check():
    """Health check endpoint for UptimeRobot/Render"""
    return jsonify({"status": "ok", "message": "Bot is running"}), 200


def run_health_check():
    """Run the Flask health check server"""
    port = int(os.environ.get('PORT', 8080))
    app.run(host="0.0.0.0", port=port, debug=False)


def start_health_check():
    """Start health check in a separate thread"""
    health_thread = Thread(target=run_health_check, daemon=True)
    health_thread.start()
    port = int(os.environ.get('PORT', 8080))
    logging.info(f"🌐 Health check запущен на порту {port}")
