"""
どの画面のテンプレートでも {{ current_participation }} で「今参加している部屋」が使えるようにする。
（config/settings.py の TEMPLATES → context_processors に登録して使う）

  {% if current_participation %}
    {{ current_participation.room.room_name }}
  {% endif %}
"""

from .utils import get_current_participation


def current_room(request):
    return {'current_participation': get_current_participation(request)}
