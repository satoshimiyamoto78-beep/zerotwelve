# BIMA — дизайн стены в офисе: промпты для Nano Banana (Google Flow)

## Как работать в Flow

1. **Загрузи фото текущей стены** как reference (image-to-image / edit). Так сохранится геометрия: изогнутая белая ниша с закруглённым верхом, камера, скамейка, банкомат справа.
2. **Загрузи логотип BIMA** (лев + надпись) отдельным референсом, чтобы модель не придумала свой.
3. Вставь **базовый блок** + **один из концептов** ниже. Промпты на английском: Nano Banana так лучше понимает. Тексты на русском оставлены в кавычках.
4. Кириллица у модели иногда ломается. Если надписи кривые: сначала сгенерируй композицию **без текста** (добавь `no text on the panels, leave clean space for text`), а текст наложи потом в Figma/Illustrator. Для презентации клиенту можно оставить текст, сгенерированный моделью.
5. Генерируй 4 варианта, выбирай лучший и уточняй точечно ("make the lion bigger", "reduce icons to 5", "more white space on the left").

---

## Базовый блок (вставлять в начало каждого промпта)

```
Edit the attached photo. Keep the exact room, camera angle, lighting, the curved white wall niche with its rounded top edge, the bench, the ceiling camera and the ATM on the right. Replace ONLY the current yellow hexagon signage on the wall with a new, premium corporate brand wall design for BIMA Insurance (Tajikistan's leading insurance company).
Brand: golden amber #F5A623, deep navy #2D3748, white. Use the attached BIMA logo exactly — geometric golden lion head + wordmark "BIMA INSURANCE". Bold geometric sans-serif typography (Montserrat ExtraBold style), all caps for headlines.
Content to show (6 facts):
1. "67,5 МЛН СОМОНИ" — самая большая выплата в истории страны
2. "ЛИДЕРЫ РЫНКА" — по сборам и выплатам
3. "ЛУЧШАЯ СТРАХОВАЯ ОРГАНИЗАЦИЯ ТАДЖИКИСТАНА" — по версии World Finance
4. "ЛУЧШАЯ ЭКСПЕРТИЗА" — в корпоративном направлении
5. "ЛУЧШЕЕ ДМС" — лучшее добровольное медицинское страхование в Таджикистане
6. "ПРЕДСТАВИТЕЛЬСТВА" — Худжанд, Пенджикент, Бохтар, Куляб, Хорог
Photorealistic interior photography, the design looks physically installed (printed vinyl / acrylic), correct perspective, soft realistic shadows, 16:9, high detail.
```

---

## Концепт 1 — «Геометрическая мозаика» (реф: Mountain View)

Самый сильный и свежий вариант: стена превращается в цельное панно, а не в набор табличек.

```
Design concept: a full-wall geometric mosaic mural that follows the curved shape of the niche, flat vector illustration style. A grid of rectangular and square tiles in golden amber, deep navy, light warm gray and white, with diagonal splits (~20° angle, BIMA signature diagonal), quarter circles and triangles. The big golden geometric lion head is the hero tile in the left-center, built from the same angular facets as the logo. "BIMA INSURANCE" wordmark in navy on a large white tile next to it.
The 6 facts live inside individual tiles: the number "67,5" is huge and bold in navy on a gold tile with "МЛН СОМОНИ" below; other tiles combine one simple thick-line icon (shield with heart, award medal, ribbon badge with star, thumbs up, map of Tajikistan with 5 location pins) and a short caps headline. Remaining tiles are purely decorative: abstract mountains (Pamir), sun, a minimal Dushanbe skyline, dots and stripes — insurance and protection metaphors (umbrella, shield, key).
Balanced, rhythmic, lots of breathing room, max 3 lines of text per tile, consistent icon stroke weight. Matte vinyl print.
```

## Концепт 2 — «Сетка панелей с line-иконками» (реф: ANPS)

Чище и строже, как в банке. Легко производить: печать на композите, панели можно менять.

```
Design concept: the niche is covered by a clean modular grid of square panels (3 rows), printed on matte composite, with thin 8mm gaps between panels. Color rhythm: mostly deep navy and golden amber panels, a few white and soft-gold panels, arranged in a balanced checkerboard-like rhythm. Large white thin-line icons (uniform 4px stroke, rounded caps) on navy panels: shield, heart with plus, medal with star, award ribbon, location pins, trophy.
A large merged panel (2x2) in the center holds the golden lion logo and "BIMA INSURANCE". A wide horizontal panel holds the key number "67,5 МЛН СОМОНИ" with caption "САМАЯ БОЛЬШАЯ ВЫПЛАТА В ИСТОРИИ СТРАНЫ". Fact headlines in white caps on navy and in navy on gold. Some panels have big abstract shapes — half circle, diagonal triangle, large letter "B" crop — for an editorial feel.
Perfect alignment, symmetric margins inside the curved niche, modern Scandinavian corporate look.
```

## Концепт 3 — «Типографика-манифест» (реф: Meet. Work. Create.)

Минимализм, максимум уверенности. Факты подаются как крупная типографика.

```
Design concept: a bold typographic wall. Mostly white wall with generous negative space. Giant deep-navy volumetric 3D letters (matte, 30mm thick, slightly raised from the wall with soft shadows) reading:
"НАДЁЖНО." on the first line, "ЧЕСТНО." on the second, "НАВСЕГДА." on the third — each word ends with a golden amber dot.
A thin flowing golden amber line (like a lifeline / heartbeat that turns into a smooth wave) runs across the whole wall, passing through the words and connecting small fact markers.
Along the golden line: 6 small elegant fact labels — big numeral or short caps headline in navy and a one-line caption in gray: "67,5 МЛН СОМОНИ", "№1 ПО СБОРАМ И ВЫПЛАТАМ", "WORLD FINANCE: ЛУЧШАЯ СТРАХОВАЯ", "ЛУЧШЕЕ ДМС", "ЭКСПЕРТИЗА В КОРПОРАТИВНОМ СЕКТОРЕ", "5 ПРЕДСТАВИТЕЛЬСТВ".
The golden geometric lion logo with "BIMA INSURANCE" in the upper right as a 3D acrylic sign. Clean, premium, gallery-like.
```

## Концепт 4 — «Облако слов в объёме» (реф: Teamwork)

Самое дешёвое в производстве (объёмные буквы из ПВХ/акрила), но выглядит богато.

```
Design concept: a 3D typographic word cloud made of laser-cut acrylic letters mounted on the white wall with standoffs, casting soft shadows. Centerpiece: a large golden amber lion logo and big navy word "BIMA" in the middle. Around it, words in different sizes and orientations (horizontal and vertical), mixed colors — navy, golden amber, warm gray: "НАДЁЖНОСТЬ", "ЗАЩИТА", "ДОВЕРИЕ", "ДМС", "КАСКО", "ЭКСПЕРТИЗА", "ВЫПЛАТЫ", "ЛИДЕР", "СПОКОЙСТВИЕ", "ПАРТНЁРСТВО", "ХУДЖАНД", "ХОРОГ", "КУЛЯБ", "БОХТАР", "ПЕНДЖИКЕНТ", "WORLD FINANCE", "67,5 МЛН СОМОНИ" (highlighted biggest after BIMA, in gold).
Tight, balanced composition shaped to fill the curved niche, clear hierarchy, no overlapping letters.
```

## Концепт 5 — «Гибрид: диагональ BIMA + инфографика» (рекомендую для презентации)

Использует фирменную диагональ BIMA и собирает все факты в читаемую историю.

```
Design concept: the wall is split by a bold diagonal (~20°, BIMA signature) — the lower-left part is a solid golden amber field, the upper-right stays white. A thin navy line accents the diagonal edge.
On the gold field (left): the huge golden-on-navy lion logo inside a navy angular shape, "BIMA INSURANCE" in navy below, and the hero number "67,5" in giant navy type with "МЛН СОМОНИ — САМАЯ БОЛЬШАЯ ВЫПЛАТА В ИСТОРИИ СТРАНЫ".
On the white field (right): a clean 2x2 infographic grid of facts, each with a navy line icon in a small gold circle, caps headline in navy, one-line caption in gray: "ЛИДЕРЫ РЫНКА", "ЛУЧШАЯ СТРАХОВАЯ ПО ВЕРСИИ WORLD FINANCE", "ЛУЧШЕЕ ДМС В ТАДЖИКИСТАНЕ", "ЛУЧШАЯ КОРПОРАТИВНАЯ ЭКСПЕРТИЗА".
Bottom-right: a minimal navy outline map of Tajikistan with 5 golden pins labeled Худжанд, Пенджикент, Бохтар, Куляб, Хорог, title "ПРЕДСТАВИТЕЛЬСТВА".
Strict grid, aligned baselines, generous margins, nothing touches the curved edge of the niche. Matte vinyl + raised acrylic logo.
```

---

## Полезные доп. фразы (дописывать при доработке)

- `more white space, fewer elements, calmer composition`: если перегружено
- `all text perfectly legible, correct Cyrillic spelling`: если кривые буквы
- `no text on the panels, leave clean areas for text`: чистая основа под ручную вёрстку
- `same design, front-facing straight-on orthographic view of the wall, no room, print-ready flat layout`: макет для типографии
- `evening lighting with warm LED backlight behind the acrylic logo`: вечерний рендер
- `show a person standing next to the wall for scale`: показать масштаб клиенту

## Чего избегать в промпте (negative)

```
no hexagons, no clutter, no random stock icons, no gradients overload, no drop-shadow text, no misspelled words, no extra logos, do not change the room
```
