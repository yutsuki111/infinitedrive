from django.contrib import admin
from driveapp.models import Room, RoomParticipation


# 参考リンク：
# https://qiita.com/onishi_820/items/fadcfc9e9dd28f54c32c
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    pass

@admin.register(RoomParticipation)
class RoomParticipationAdmin(admin.ModelAdmin):
    pass
