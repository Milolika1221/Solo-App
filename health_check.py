#!/usr/bin/env python3
"""
Health check endpoint для Render
"""
from flask import Flask
from threading import Thread
import asyncio
import logging

app = Flask(__name__)

@app.route("/")
@app.route("/health")
@app.route("/ping")
def health_check():
    """Health check endpoint для UptimeRobot"""
    return "🤖 Bot is alive!", 200

def run_health_check():
    """Запуск health check сервера"""
    app.run(host="0.0.0.0", port=8080, debug=False)

def start_health_check():
    """Запуск health check в отдельном потоке"""
    health_thread = Thread(target=run_health_check, daemon=True)
    health_thread.start()
    logging.info("🌐 Health check запущен на порту 8080")

# Экспортируем для использования в main.py
__all__ = ['start_health_check']
