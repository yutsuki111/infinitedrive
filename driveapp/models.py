from django.db import models


# ==========================================
# 01_アカウント (accounts)
# ==========================================
class Account(models.Model):
    account_id = models.AutoField(primary_key=True, verbose_name="アカウントID")
    user_id = models.CharField(max_length=100, unique=True, verbose_name="ユーザーID")
    password_hash = models.CharField(max_length=255, verbose_name="パスワードハッシュ")
    display_name = models.CharField(max_length=20, verbose_name="表示名")
    is_admin = models.BooleanField(default=False, verbose_name="管理者フラグ")
    status = models.CharField(max_length=20, default="active", verbose_name="利用状態")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="登録日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        db_table = "accounts"
        verbose_name = "アカウント"
        verbose_name_plural = "アカウント"

    def __str__(self):
        return f"{self.display_name} ({self.user_id})"


# ==========================================
# 02_ゲストセッション (guest_sessions)
# ==========================================
class GuestSession(models.Model):
    guest_id = models.AutoField(primary_key=True, verbose_name="ゲストID")
    session_token_hash = models.CharField(max_length=255, unique=True, verbose_name="セッショントークンハッシュ")
    display_name = models.CharField(max_length=20, default="ゲスト", verbose_name="ゲスト表示名")
    status = models.CharField(max_length=20, default="active", verbose_name="セッション状態")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    expires_at = models.DateTimeField(verbose_name="有効期限")

    class Meta:
        db_table = "guest_sessions"
        verbose_name = "ゲストセッション"
        verbose_name_plural = "ゲストセッション"

    def __str__(self):
        return f"{self.display_name} (Guest: {self.guest_id})"


# ==========================================
# 03_部屋 (rooms)
# ※部屋解散時に物理削除（紐づく参加情報・ドライブ・投稿もCASCADE削除）
# ==========================================
class Room(models.Model):
    room_id = models.AutoField(primary_key=True, verbose_name="部屋ID")
    room_code = models.CharField(max_length=4, unique=True, verbose_name="部屋番号")
    room_name = models.CharField(max_length=50, verbose_name="部屋名")
    passphrase_hash = models.CharField(max_length=255, verbose_name="合言葉ハッシュ")
    status = models.CharField(max_length=20, default="waiting", verbose_name="部屋状態")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")

    class Meta:
        db_table = "rooms"
        verbose_name = "部屋"
        verbose_name_plural = "部屋"

    def __str__(self):
        return f"{self.room_name} ({self.room_code})"


# ==========================================
# 04_部屋参加情報 (room_participations)
# ==========================================
class RoomParticipation(models.Model):
    room_participation_id = models.AutoField(primary_key=True, verbose_name="部屋参加情報ID")
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        db_column="room_id",
        related_name="participations",
        verbose_name="部屋ID",
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column="account_id",
        related_name="room_participations",
        verbose_name="会員ID",
    )
    guest = models.ForeignKey(
        GuestSession,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column="guest_id",
        related_name="room_participations",
        verbose_name="ゲストID",
    )
    nickname = models.CharField(max_length=20, verbose_name="参加ニックネーム")
    role = models.CharField(max_length=20, default="member", verbose_name="部屋権限役割")
    drive_role = models.CharField(max_length=20, null=True, blank=True, verbose_name="運転役割")
    safety_agreed = models.BooleanField(default=False, verbose_name="安全運転同意フラグ")
    drive_status = models.CharField(max_length=20, default="ready", verbose_name="進行状態")
    status = models.CharField(max_length=20, default="joined", verbose_name="参加状態")
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="参加日時")
    left_at = models.DateTimeField(null=True, blank=True, verbose_name="退出日時")

    class Meta:
        db_table = "room_participations"
        verbose_name = "部屋参加情報"
        verbose_name_plural = "部屋参加情報"

    def __str__(self):
        return f"{self.nickname} ({self.role})"


# ==========================================
# 08_目的地 (destinations)
# ※05_ドライブから参照されるため先に定義
# ==========================================
class Destination(models.Model):
    destination_id = models.AutoField(primary_key=True, verbose_name="目的地ID")
    name = models.CharField(max_length=100, verbose_name="目的地名")
    address = models.CharField(max_length=255, null=True, blank=True, verbose_name="住所")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="緯度")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="経度")
    companion_tag = models.CharField(max_length=50, verbose_name="同行者条件タグ")
    mood_tag = models.CharField(max_length=50, verbose_name="気分条件タグ")
    status = models.CharField(max_length=20, default="active", verbose_name="有効状態")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="登録日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        db_table = "destinations"
        verbose_name = "目的地"
        verbose_name_plural = "目的地"

    def __str__(self):
        return self.name


# ==========================================
# 05_ドライブ (drives)
# ==========================================
class Drive(models.Model):
    drive_id = models.AutoField(primary_key=True, verbose_name="ドライブID")
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        db_column="room_id",
        related_name="drives",
        verbose_name="部屋ID",
    )
    destination = models.ForeignKey(
        Destination,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="destination_id",
        related_name="drives",
        verbose_name="目的地ID",
    )
    companion_tag = models.CharField(max_length=20, default="友達", verbose_name="同行者条件")
    mood_tag = models.CharField(max_length=20, default="エモい", verbose_name="気分条件")
    start_latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="出発地緯度"
    )
    start_longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="出発地経度"
    )
    status = models.CharField(max_length=20, default="waiting", verbose_name="ドライブ状態")
    started_at = models.DateTimeField(null=True, blank=True, verbose_name="開始日時")
    ended_at = models.DateTimeField(null=True, blank=True, verbose_name="終了日時")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")

    class Meta:
        db_table = "drives"
        verbose_name = "ドライブ"
        verbose_name_plural = "ドライブ"

    def __str__(self):
        return f"Drive {self.drive_id} (Room: {self.room_id})"


# ==========================================
# 06_ドライブ履歴 (drive_histories)
# ※部屋解散後も削除しない永続テーブル
# ==========================================
class DriveHistory(models.Model):
    drive_history_id = models.AutoField(primary_key=True, verbose_name="ドライブ履歴ID")
    destination_name_snapshot = models.CharField(max_length=100, verbose_name="目的地名スナップショット")
    mission_title_snapshot = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="達成ミッションスナップショット"
    )
    started_at = models.DateTimeField(verbose_name="ドライブ開始日時")
    ended_at = models.DateTimeField(verbose_name="ドライブ終了日時")
    recorded_at = models.DateTimeField(auto_now_add=True, verbose_name="履歴記録日時")

    class Meta:
        db_table = "drive_histories"
        verbose_name = "ドライブ履歴"
        verbose_name_plural = "ドライブ履歴"

    def __str__(self):
        return f"History {self.drive_history_id}: {self.destination_name_snapshot}"


# ==========================================
# 07_ドライブ履歴参加者 (drive_history_participants)
# ==========================================
class DriveHistoryParticipant(models.Model):
    drive_history_participant_id = models.AutoField(primary_key=True, verbose_name="履歴参加者ID")
    drive_history = models.ForeignKey(
        DriveHistory,
        on_delete=models.CASCADE,
        db_column="drive_history_id",
        related_name="participants",
        verbose_name="ドライブ履歴ID",
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="account_id",
        related_name="drive_history_participations",
        verbose_name="会員ID",
    )
    display_name_snapshot = models.CharField(max_length=20, verbose_name="表示名スナップショット")
    star_rating = models.IntegerField(default=5, verbose_name="星評価")
    result = models.CharField(max_length=100, null=True, blank=True, verbose_name="獲得称号結果")
    saved_image_url = models.CharField(max_length=255, null=True, blank=True, verbose_name="保存写真URL")
    recorded_at = models.DateTimeField(auto_now_add=True, verbose_name="記録日時")

    class Meta:
        db_table = "drive_history_participants"
        verbose_name = "ドライブ履歴参加者"
        verbose_name_plural = "ドライブ履歴参加者"

    def __str__(self):
        return f"{self.display_name_snapshot} (History: {self.drive_history_id})"


# ==========================================
# 09_ミッション (missions)
# ==========================================
class Mission(models.Model):
    mission_id = models.AutoField(primary_key=True, verbose_name="ミッションID")
    title = models.CharField(max_length=100, verbose_name="ミッション名")
    description = models.TextField(null=True, blank=True, verbose_name="ミッション説明")
    companion_tag = models.CharField(max_length=50, verbose_name="同行者条件タグ")
    mood_tag = models.CharField(max_length=50, verbose_name="気分条件タグ")
    status = models.CharField(max_length=20, default="active", verbose_name="有効状態")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="登録日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        db_table = "missions"
        verbose_name = "ミッション"
        verbose_name_plural = "ミッション"

    def __str__(self):
        return self.title


# ==========================================
# 10_ドライブミッション (drive_missions)
# ==========================================
class DriveMission(models.Model):
    drive_mission_id = models.AutoField(primary_key=True, verbose_name="ドライブミッションID")
    drive = models.ForeignKey(
        Drive,
        on_delete=models.CASCADE,
        db_column="drive_id",
        related_name="drive_missions",
        verbose_name="ドライブID",
    )
    mission = models.ForeignKey(
        Mission,
        on_delete=models.CASCADE,
        db_column="mission_id",
        related_name="drive_missions",
        verbose_name="ミッションID",
    )
    status = models.CharField(max_length=20, default="active", verbose_name="状態")
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name="割り当て日時")

    class Meta:
        db_table = "drive_missions"
        verbose_name = "ドライブミッション"
        verbose_name_plural = "ドライブミッション"

    def __str__(self):
        return f"DriveMission {self.drive_mission_id} (Drive: {self.drive_id})"


# ==========================================
# 11_ミッション達成記録 (mission_results)
# ==========================================
class MissionResult(models.Model):
    mission_result_id = models.AutoField(primary_key=True, verbose_name="達成記録ID")
    drive_mission = models.ForeignKey(
        DriveMission,
        on_delete=models.CASCADE,
        db_column="drive_mission_id",
        related_name="mission_results",
        verbose_name="ドライブミッションID",
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="account_id",
        related_name="mission_results",
        verbose_name="会員ID",
    )
    report_image_url = models.CharField(max_length=255, verbose_name="報告写真URL")
    status = models.CharField(max_length=20, default="achieved", verbose_name="状態")
    achieved_at = models.DateTimeField(auto_now_add=True, verbose_name="達成日時")

    class Meta:
        db_table = "mission_results"
        verbose_name = "ミッション達成記録"
        verbose_name_plural = "ミッション達成記録"

    def __str__(self):
        return f"MissionResult {self.mission_result_id}"


# ==========================================
# 12_実績マスタ (achievements)
# ==========================================
class Achievement(models.Model):
    achievement_id = models.AutoField(primary_key=True, verbose_name="実績ID")
    name = models.CharField(max_length=50, verbose_name="実績名")
    description = models.CharField(max_length=200, verbose_name="実績説明")
    icon_url = models.CharField(max_length=255, null=True, blank=True, verbose_name="アイコン画像URL")
    condition_type = models.CharField(max_length=50, verbose_name="獲得条件種類")
    condition_value = models.IntegerField(default=1, verbose_name="獲得条件基準値")
    status = models.CharField(max_length=20, default="active", verbose_name="有効状態")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="登録日時")

    class Meta:
        db_table = "achievements"
        verbose_name = "実績マスタ"
        verbose_name_plural = "実績マスタ"

    def __str__(self):
        return self.name


# ==========================================
# 13_ユーザー実績 (account_achievements)
# ※account_id と achievement_id の複合ユニーク制約で重複獲得を防止
# ==========================================
class AccountAchievement(models.Model):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        db_column="account_id",
        related_name="account_achievements",
        verbose_name="会員ID",
    )
    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE,
        db_column="achievement_id",
        related_name="account_achievements",
        verbose_name="実績ID",
    )
    acquired_at = models.DateTimeField(auto_now_add=True, verbose_name="獲得日時")

    class Meta:
        db_table = "account_achievements"
        verbose_name = "ユーザー実績"
        verbose_name_plural = "ユーザー実績"
        constraints = [
            models.UniqueConstraint(
                fields=["account", "achievement"], name="unique_account_achievement"
            )
        ]

    def __str__(self):
        return f"Account {self.account_id} - Achievement {self.achievement_id}"


# ==========================================
# 14_タイムライン投稿 (timeline_posts)
# ==========================================
class TimelinePost(models.Model):
    post_id = models.AutoField(primary_key=True, verbose_name="投稿ID")
    drive = models.ForeignKey(
        Drive,
        on_delete=models.CASCADE,
        db_column="drive_id",
        related_name="timeline_posts",
        verbose_name="ドライブID",
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        db_column="room_id",
        related_name="timeline_posts",
        verbose_name="部屋ID",
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="account_id",
        related_name="timeline_posts",
        verbose_name="会員投稿者ID",
    )
    guest = models.ForeignKey(
        GuestSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="guest_id",
        related_name="timeline_posts",
        verbose_name="ゲスト投稿者ID",
    )
    post_type = models.CharField(max_length=20, default="normal", verbose_name="投稿種別")
    content = models.TextField(null=True, blank=True, verbose_name="投稿文")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="投稿日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        db_table = "timeline_posts"
        verbose_name = "タイムライン投稿"
        verbose_name_plural = "タイムライン投稿"

    def __str__(self):
        return f"Post {self.post_id} ({self.post_type})"


# ==========================================
# 15_投稿画像 (post_images)
# ==========================================
class PostImage(models.Model):
    post_image_id = models.AutoField(primary_key=True, verbose_name="投稿画像ID")
    post = models.ForeignKey(
        TimelinePost,
        on_delete=models.CASCADE,
        db_column="post_id",
        related_name="images",
        verbose_name="投稿ID",
    )
    image_url = models.CharField(max_length=255, verbose_name="画像ファイルURL")
    display_order = models.IntegerField(default=1, verbose_name="表示順")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="登録日時")

    class Meta:
        db_table = "post_images"
        verbose_name = "投稿画像"
        verbose_name_plural = "投稿画像"

    def __str__(self):
        return f"Image {self.post_image_id} (Post: {self.post_id})"