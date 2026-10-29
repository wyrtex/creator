# Creator — автоматический контент по играм Supercell

Цель: Claude сам делает и публикует видео для YouTube (длинные + Shorts), TikTok и Instagram Reels.
Ниша: Brawl Stars, Clash Royale, Clash of Clans, mo.co.

## Главное правило формата

Видео НЕ требуют живого геймплея. Только то, что можно собрать из графики, текста и озвучки:

- **Новости** — обновления, баланс-патчи, новые бравлеры/карты/юниты, ивенты, слитые сникпики.
- **Тактики и стратегии** — колоды CR, расстановки базы CoC, контрпики в BS, билды в mo.co.
- **Тир-листы и мета** — «топ-5 колод сезона», «кто сломан после патча».
- **Объяснялки** — механики, математика урона/эликсира, гайды для новичков, сравнения.
- **Списки/факты** — «10 вещей, которые ты не знал про …».

Визуал — моушн-графика (HyperFrames/Remotion): карточки, схемы арены/базы, стрелки, цифры, анимированные таблицы.

## Пайплайн (один ролик)

1. **Тема** — свежие новости/патчноуты (WebSearch: официальные блоги Supercell, Reddit, X). Для стратегий — текущая мета.
2. **План/упаковка** — `yt-plan`, `yt-viral`, `yt-package` (заголовок + превью как пара), `yt-seo`.
3. **Сценарий** — длинное: `yt-script`; короткое: `tiktok-script`, `short-form-video-script`, `ig-reel`, `hook-writer`. Хук в первые 1–2 сек.
4. **Озвучка** — русский: `python3 tools/tts.py text.txt out.mp3` (edge-tts, `ru-RU-DmitryNeural`; пишет и тайминги слов `out.json` для субтитров). Kokoro русский не умеет.
5. **Видео** — `hyperframes` (основной движок) или `remotion-*`. Вкус и моушн — `emil-design-eng`, `animate`, `improve-animations`, `design-taste-frontend`, `impeccable`.
   - Длинное: 16:9, 1920×1080, 6–12 мин, главы через `yt-chapters`.
   - Короткое: 9:16, 1080×1920, 20–55 сек; из длинных нарезать через `yt-shorts`, `ig-repurpose`.
6. **Подписи** — `ig-caption`, `yt-seo`, хэштеги под платформу.
7. **Публикация** — `upload-post` (YouTube, TikTok, Instagram одним API). Платформенные нюансы — `tiktok-video-publishing`.
8. **Аналитика** — `yt-retention`, `yt-audit`, `ig-audit`, `tiktok-growth` → корректировать следующие темы.

Пример готового проекта: `videos/cr-elixir-short/` (сцены, `script/gen_trades.py`, `script/gen_captions.py`).
Готовые файлы складывать в `output/<дата>-<slug>/` (video, thumbnail, script.md, meta.json).

## Ассеты и авторские права

- Следовать Supercell Fan Content Policy: не выдавать себя за официальный канал, в описании указать
  «This content is not affiliated with, endorsed, sponsored, or specifically approved by Supercell…».
- Не использовать чужую музыку/трендовые треки без лицензии; SFX — из `media-use/audio/assets`.
- Иконки/арты игр брать из официальных пресс-китов, не воровать чужие монтажи.

## Что нужно от владельца

- `UPLOAD_POST_API_KEY` (upload-post.com) с подключёнными каналами YouTube/TikTok/Instagram —
  положить в секреты окружения, не в репозиторий.
- Язык роликов и название/брендинг канала.
