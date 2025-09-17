# Делает удобные импорты и не падает, если каких-то модулей нет.

from . import base, events, errors, heroes  # эти должны быть всегда

# skills может отсутствовать на ранней стадии — подключаем по возможности
try:
    from . import skills
except Exception:
    skills = None

__all__ = ["base", "events", "errors", "skills", "heroes"]
