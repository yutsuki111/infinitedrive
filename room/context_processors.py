from .utils import get_current_participation

#どの画面のテンプレートでも {{ current_participation }} で「今参加している部屋」が使えるようにする
#（config/settings.py の TEMPLATES → context_processors に登録している）
def current_room(request):
    return {"current_participation": get_current_participation(request)}
