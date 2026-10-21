# BIMA: правка утверждённого стенда (v4)

Загрузить в Flow утверждённую картинку (ряд из 6 скруглённых панелей) и вставить промпт.

## Основной промпт

```
Edit the attached image. Keep EVERYTHING exactly the same — room, camera angle, lighting, logo, all six panel shapes, sizes, positions, gaps, thickness, shadows, icons, fonts and all other text. Make ONLY these three changes:

1. First panel (left, "67,5"): change the panel color from dark navy to light gray #F6F6F6 (glossy acrylic, same thickness and shadow, a subtle edge so it stays visible on the white wall). Text becomes deep navy/black: "67,5" very large, "МЛН СОМОНИ", "Самая большая выплата в истории страны". Same layout and font as now.

2. Second panel (medal icon): replace the text. Remove the medal icon. Write "BB-" very large in bold navy (Latin letters B B and a minus sign, same weight and size as "67,5"), below it the caption: "кредитный рейтинг от АКРА с прогнозом «Стабильный»" in the regular caption style, centered, max 3 lines.

3. Third panel (rosette icon): keep the rosette icon. Replace the text: "WORLD FINANCE" large in bold navy caps (2 lines: "WORLD" / "FINANCE"), and below it small caption text: "лучшая страховая организация Таджикистана 2023 года".

Typography for all changed text: the same wide geometric sans-serif as on the other panels (Montserrat / Gilroy style), bold caps for headlines, regular weight sentence case for captions, even margins, correct Cyrillic spelling. Do not change anything else.
```

## Вариант с жёлтыми буквами на первом блоке

Заменить пункт 1 на:

```
1. First panel (left, "67,5"): change the panel color from dark navy to light gray #F6F6F6. "67,5" in golden yellow #F5A623 very large with a thin navy outline for readability; "МЛН СОМОНИ" and "Самая большая выплата в истории страны" in deep navy.
```

## Если модель портит соседние панели

Делать по одной правке за раз: вставлять только нужный пункт (1, 2 или 3) и начинать с `Edit the attached image. Keep everything exactly the same. Change ONLY the ... panel:`.
