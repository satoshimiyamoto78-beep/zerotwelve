# BIMA: стена в офисе, v3 (исправленные тексты и стильная типографика)

## Что поменялось

**Тексты (точно, как утверждено):**
- ДМС: «ЛУЧШЕЕ ДОБРОВОЛЬНОЕ МЕДИЦИНСКОЕ СТРАХОВОЕ ПРЕДЛОЖЕНИЕ»
- World Finance: «ЛУЧШАЯ СТРАХОВАЯ ОРГАНИЗАЦИЯ ТАДЖИКИСТАНА» / «по версии WORLDFINANCE.COM»

**Шрифт:** сейчас модель ставит стандартный узкий шрифт вроде Roboto/DIN, он выглядит дёшево. Новое правило: заголовки набираются тем же типом шрифта, что и слово «BIMA» в логотипе. Это широкий геометрический гротеск (Gilroy / TT Norms / Montserrat), жирный, с плотной разрядкой. Пояснения тонкие (Light), строчными, с воздухом между буквами. Цифры крупные и жирные. Узких (condensed) шрифтов нет вообще.

---

## Блок типографики (уже вшит в промпты ниже, можно дописывать к любому)

```
Typography (very important): premium, stylish, consistent. Headlines use the SAME typeface as the "BIMA" wordmark in the logo — a wide geometric sans-serif (Gilroy / TT Norms Pro / Montserrat style), ExtraBold, ALL CAPS, slightly tight letter-spacing, generous line-height. Captions in the same family, Light weight, sentence case, wider letter-spacing (+5%), smaller size — clear contrast between headline and caption. Numbers: Black weight, very large, tight kerning, the comma well-spaced. NO condensed or narrow fonts, NO Roboto/Arial/DIN look, no mixed fonts. Text optically centered with even margins inside each panel, max 4 lines per block, correct Cyrillic spelling.
```

---

## A. Правка уже сгенерированных картинок (быстрый путь)

Загрузи свою картинку в Flow и вставь промпт. Модель поменяет только тексты и шрифт.

### A1. Для варианта «Лента фактов» (ряд квадратов под логотипом)

```
Edit the attached image. Keep everything exactly the same — room, logo, panel shapes, colors, positions, icons, lighting. Change ONLY the text on the panels and the typography.
Panel 3 (rosette icon) text, 4 lines: "ЛУЧШАЯ / СТРАХОВАЯ ОРГАНИЗАЦИЯ / ТАДЖИКИСТАНА" in bold caps, caption "по версии WORLDFINANCE.COM" in light weight.
Panel 4 (heart icon) text, 4 lines: "ЛУЧШЕЕ / ДОБРОВОЛЬНОЕ / МЕДИЦИНСКОЕ СТРАХОВОЕ / ПРЕДЛОЖЕНИЕ" in bold caps (slightly smaller size so it fits comfortably).
Other panels keep their content: "67,5 / МЛН СОМОНИ / самая большая выплата в истории страны", "ЛИДЕРЫ РЫНКА / по сборам и выплатам", "ЛУЧШАЯ ЭКСПЕРТИЗА / в корпоративном направлении", "ПРЕДСТАВИТЕЛЬСТВА / Худжанд, Пенджикент, Бохтар, Куляб, Хорог".
Typography (very important): premium, stylish, consistent. Headlines use the SAME typeface as the "BIMA" wordmark in the logo — a wide geometric sans-serif (Gilroy / TT Norms Pro / Montserrat style), ExtraBold, ALL CAPS, slightly tight letter-spacing. Captions in the same family, Light weight, sentence case, wider letter-spacing, smaller size. Numbers Black weight, very large. NO condensed or narrow fonts, no Roboto/Arial look. Same text size system on all panels, even margins, correct Cyrillic spelling.
```

### A2. Для варианта «Грани льва» (скошенные панели по бокам логотипа)

```
Edit the attached image. Keep everything exactly the same — room, logo, panel shapes, colors, positions, icons, lighting. Change ONLY the text and the typography. You may make the heart panel and the rosette panel slightly larger so the longer text fits with comfortable margins.
Heart panel text: "ЛУЧШЕЕ ДОБРОВОЛЬНОЕ / МЕДИЦИНСКОЕ СТРАХОВОЕ / ПРЕДЛОЖЕНИЕ" in bold caps, 3 lines.
Rosette panel text: "ЛУЧШАЯ СТРАХОВАЯ / ОРГАНИЗАЦИЯ ТАДЖИКИСТАНА" in bold caps, caption "по версии WORLDFINANCE.COM" in light weight.
Other panels keep their content: "ЛУЧШАЯ ЭКСПЕРТИЗА / в корпоративном направлении", "ПРЕДСТАВИТЕЛЬСТВА / Худжанд, Пенджикент, Бохтар, Куляб, Хорог", "67,5 / МЛН СОМОНИ / самая большая выплата в истории страны", "ЛИДЕРЫ РЫНКА / по сборам и выплатам".
Typography (very important): premium, stylish, consistent. Headlines use the SAME typeface as the "BIMA" wordmark in the logo — a wide geometric sans-serif (Gilroy / TT Norms Pro / Montserrat style), ExtraBold, ALL CAPS, slightly tight letter-spacing. Captions in the same family, Light weight, sentence case, wider letter-spacing, smaller size. Numbers Black weight, very large. NO condensed or narrow fonts, no Roboto/Arial look. Same text size system on all panels, even margins, correct Cyrillic spelling.
```

---

## B. Полные промпты с нуля (на фото исходной стены + логотип)

### Промпт 1: «Собранные соты»

```
Edit the attached photo. Keep the exact room, camera angle, lighting, the curved white wall niche with its rounded top edge, the bench, the ceiling camera and the ATM. Redesign ONLY the signage on the wall — an enhancement of the existing design, same materials and style.
Keep the style: glossy golden-yellow acrylic panels (#F5A623) about 10mm thick, mounted on standoffs with soft realistic shadows, deep navy (#2D3748) icons and text, white wall, the 3D golden geometric lion logo and black 3D letters "BIMA INSURANCE" (use the attached logo exactly).
Structure: a tight, perfectly aligned honeycomb cluster — flat-top hexagons with equal 25mm gaps, symmetric, centered in the niche with generous white margins from the curved edges. The center hexagon is the largest, white glossy acrylic with the yellow lion; "BIMA INSURANCE" in black directly beneath the cluster center. Three yellow hexagons on the left, three on the right, mirrored. "67,5" is the hero, directly right of the logo, number very large.
Each hexagon: navy icon on top (uniform thick line style, rounded corners), bold caps headline, light caption, centered:
- thumbs up with stars — "ЛУЧШАЯ ЭКСПЕРТИЗА" / "в корпоративном направлении"
- heart with plus — "ЛУЧШЕЕ ДОБРОВОЛЬНОЕ / МЕДИЦИНСКОЕ СТРАХОВОЕ / ПРЕДЛОЖЕНИЕ"
- location pins — "ПРЕДСТАВИТЕЛЬСТВА" / "Худжанд, Пенджикент, Бохтар, Куляб, Хорог"
- "67,5" / "МЛН СОМОНИ" / "самая большая выплата в истории страны"
- medal with star — "ЛИДЕРЫ РЫНКА" / "по сборам и выплатам"
- award rosette — "ЛУЧШАЯ СТРАХОВАЯ / ОРГАНИЗАЦИЯ ТАДЖИКИСТАНА" / "по версии WORLDFINANCE.COM"
Typography (very important): premium, stylish, consistent. Headlines use the SAME typeface as the "BIMA" wordmark in the logo — a wide geometric sans-serif (Gilroy / TT Norms Pro / Montserrat style), ExtraBold, ALL CAPS, slightly tight letter-spacing. Captions in the same family, Light weight, sentence case, wider letter-spacing, smaller size. Numbers Black weight, very large. NO condensed or narrow fonts, no Roboto/Arial look. Same text size system on all panels, even margins, correct Cyrillic spelling.
Photorealistic interior photo, 16:9, high detail. No clutter, do not change the room.
```

### Промпт 2: «Грани льва»

```
Edit the attached photo. Keep the exact room, camera angle, lighting, the curved white wall niche with its rounded top edge, the bench, the ceiling camera and the ATM. Redesign ONLY the signage on the wall — an evolution of the existing design, same materials and style.
Keep the style: glossy golden-yellow acrylic panels (#F5A623), mounted on standoffs with soft shadows, deep navy (#2D3748) icons and text, white wall, the 3D golden geometric lion logo and black 3D letters "BIMA INSURANCE" (use the attached logo exactly).
Shape: angular chamfered panels inspired by the facets of the lion logo — rectangles with two opposite corners cut at 45°, sharp clean edges.
Structure: symmetric. Logo lock-up large in the center with plenty of white space around it. Three panels in a column on the left, three on the right, equal 30mm gaps, columns slightly fanning along the curve of the niche. Top-right panel is double-height hero: "67,5" very large, "МЛН СОМОНИ", caption "самая большая выплата в истории страны". Panels with longer text are slightly larger so text never feels cramped.
Each panel: navy icon on the left (uniform thick line style), text block on the right, left aligned:
- thumbs up with stars — "ЛУЧШАЯ ЭКСПЕРТИЗА" / "в корпоративном направлении"
- heart with plus — "ЛУЧШЕЕ ДОБРОВОЛЬНОЕ / МЕДИЦИНСКОЕ СТРАХОВОЕ / ПРЕДЛОЖЕНИЕ"
- location pins — "ПРЕДСТАВИТЕЛЬСТВА" / "Худжанд, Пенджикент, Бохтар, Куляб, Хорог"
- medal with star — "ЛИДЕРЫ РЫНКА" / "по сборам и выплатам"
- award rosette — "ЛУЧШАЯ СТРАХОВАЯ / ОРГАНИЗАЦИЯ ТАДЖИКИСТАНА" / "по версии WORLDFINANCE.COM"
Typography (very important): premium, stylish, consistent. Headlines use the SAME typeface as the "BIMA" wordmark in the logo — a wide geometric sans-serif (Gilroy / TT Norms Pro / Montserrat style), ExtraBold, ALL CAPS, slightly tight letter-spacing. Captions in the same family, Light weight, sentence case, wider letter-spacing, smaller size. Numbers Black weight, very large. NO condensed or narrow fonts, no Roboto/Arial look. Same text size system on all panels, even margins, correct Cyrillic spelling.
Photorealistic interior photo, 16:9, high detail. No hexagons, no clutter, do not change the room.
```

### Промпт 3: «Лента фактов»

```
Edit the attached photo. Keep the exact room, camera angle, lighting, the curved white wall niche with its rounded top edge, the bench, the ceiling camera and the ATM. Redesign ONLY the signage on the wall — an enhancement of the existing design, same materials and style.
Keep the style: glossy golden-yellow acrylic panels (#F5A623), mounted on standoffs with soft shadows, deep navy (#2D3748) icons and text, white wall, the 3D golden geometric lion logo and black 3D letters "BIMA INSURANCE" (use the attached logo exactly).
Structure: logo lock-up in the upper center of the niche, large, horizontal (lion left, "BIMA INSURANCE" right), comfortable margin from the curved top. Below it, one horizontal row of six equal rounded-square panels (large corner radius) with equal 30mm gaps, centered.
Panel 1 is inverted — deep navy with yellow text: "67,5" very large, "МЛН СОМОНИ", "самая большая выплата в истории страны". The other five are yellow with navy content, icon at the top, text centered:
- medal with star — "ЛИДЕРЫ РЫНКА" / "по сборам и выплатам"
- award rosette — "ЛУЧШАЯ / СТРАХОВАЯ ОРГАНИЗАЦИЯ / ТАДЖИКИСТАНА" / "по версии WORLDFINANCE.COM"
- heart with plus — "ЛУЧШЕЕ / ДОБРОВОЛЬНОЕ / МЕДИЦИНСКОЕ СТРАХОВОЕ / ПРЕДЛОЖЕНИЕ"
- thumbs up with stars — "ЛУЧШАЯ ЭКСПЕРТИЗА" / "в корпоративном направлении"
- location pins — "ПРЕДСТАВИТЕЛЬСТВА" / "Худжанд, Пенджикент, Бохтар, Куляб, Хорог"
Typography (very important): premium, stylish, consistent. Headlines use the SAME typeface as the "BIMA" wordmark in the logo — a wide geometric sans-serif (Gilroy / TT Norms Pro / Montserrat style), ExtraBold, ALL CAPS, slightly tight letter-spacing. Captions in the same family, Light weight, sentence case, wider letter-spacing, smaller size. Numbers Black weight, very large. NO condensed or narrow fonts, no Roboto/Arial look. Same text size system on all panels, even margins, correct Cyrillic spelling.
Photorealistic interior photo, 16:9, high detail. No hexagons, no clutter, do not change the room.
```

---

## Если модель снова путает длинный текст

- Генерируй без текста (`keep icons only, no text on the panels`), а надписи наложи в Figma шрифтом Gilroy или Montserrat: так результат гарантированно точный.
- Или правь по одной панели за раз: `change only the text on the heart panel to ...`.
