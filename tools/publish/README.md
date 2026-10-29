# Публикация: бесплатные официальные API

Все ключи кладутся в **секреты окружения** Claude Code (не в репозиторий).

## Голос — Google AI Studio (Gemini TTS)
1. aistudio.google.com → Get API key → Create.
2. Секрет: `GEMINI_API_KEY`.
Бесплатный тариф: голосовые модели Gemini 3.8 бесплатны до 31.12.2026. На бесплатном тарифе Google может использовать запросы для обучения.

## YouTube — Data API v3
1. console.cloud.google.com → новый проект → APIs & Services → включить **YouTube Data API v3**.
2. OAuth consent screen: External, добавить себя в Test users, затем **Publish app → In production**
   (иначе refresh-токен умирает через 7 дней; предупреждение «приложение не проверено» для себя — нормально).
3. Credentials → Create OAuth client ID → тип **TVs and Limited Input devices** → `YT_CLIENT_ID`, `YT_CLIENT_SECRET`.
4. Здесь, в сессии: `python3 tools/publish/auth_youtube.py` → открыть ссылку, ввести код, войти в аккаунт канала → `YT_REFRESH_TOKEN`.
5. **Важно:** у непроверенных API-проектов загруженные видео остаются *private*. Подать бесплатную заявку
   «YouTube API Services – Audit and Quota Extension Form»; до одобрения ролики загружаются приватными
   (их можно открыть вручную в Studio).
Квота 10 000 единиц/сутки ≈ 6 загрузок в день — нам хватает.

## Instagram Reels — Graph API
1. Instagram → профессиональный аккаунт (Автор/Бизнес), привязать к странице Facebook.
2. developers.facebook.com → Create app (Business) → продукт **Instagram** (Facebook Login for Business).
3. Права: `instagram_basic`, `instagram_content_publish`, `pages_show_list`, `pages_read_engagement`.
4. Токен: Business Settings → System users → создать → Generate token (не истекает) → `IG_ACCESS_TOKEN`.
5. `IG_USER_ID`: Graph API Explorer → `GET /me/accounts?fields=instagram_business_account` → id.
Для своего аккаунта App Review не нужен (режим разработки работает для админов приложения).

## TikTok — Content Posting API
1. developers.tiktok.com → Manage apps → Create → продукты **Login Kit** + **Content Posting API**
   (включить Direct Post), scopes `video.publish`, `video.upload`.
2. Redirect URI — любой ваш https-адрес (страница может отдавать 404) → `TIKTOK_REDIRECT_URI`.
3. `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET` из приложения.
4. `python3 tools/publish/auth_tiktok.py url` → открыть, разрешить, скопировать адрес, на который перекинуло →
   `python3 tools/publish/auth_tiktok.py code '<адрес>'` → `TIKTOK_REFRESH_TOKEN` (живёт 365 дней).
5. **Ограничение до аудита:** пока приложение не прошло бесплатный аудит TikTok, прямые посты только приватные
   (SELF_ONLY). Варианты до аудита: `--mode inbox` — видео прилетает черновиком во «Входящие» TikTok,
   опубликовать одним нажатием в телефоне. После аудита — `"tiktok_mode": "direct"` в `channel/config.json`.
