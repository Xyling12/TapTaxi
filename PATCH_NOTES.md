# TapTaxi 3.28.0 — Полный Patch Notes

**APK:** `TapTaxi. Водитель_3.28.0.apk`  
**Декомпилировано в:** `taptaxi_328_decompiled/`  
**Keystore:** `D:\tools\taptaxi_test.keystore` / pass: `android` / alias: `taptaxi`

---

## Команды сборки

```bash
# Сборка
java -jar D:\tools\apktool.jar b D:\Antigravity\TapTaxi\taptaxi_328_decompiled -o D:\Antigravity\TapTaxi\taptaxi_328_p9.apk

# Подпись
jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 -keystore D:\tools\taptaxi_test.keystore -storepass android -keypass android D:\Antigravity\TapTaxi\taptaxi_328_p9.apk taptaxi
```

---

## ИТОГ: Что сделано и где (финальная версия p9)

| # | Что | Файл | Метод/Место | Статус |
|---|-----|------|-------------|--------|
| 1 | Fake GPS — игнор mock-провайдера | `smali_classes3/h2/qfzjddwuyn.smali` | `extxjewlhp(Location)Z` | ✅ |
| 2 | Fake GPS — флаг в конструкторе | `smali_classes3/com/soft373/taxi/services/NetworkService.smali` | метод `B()V` ~стр.263 | ✅ |
| 3 | Интервал заказа 4500ms | `smali_classes3/com/soft373/taxi/services/NewOrdersServiceBase.smali` | конструктор + onStartCommand (3 места) | ✅ |
| 4 | Интервал сервера 4500ms | `smali_classes3/com/soft373/taxi/services/NetworkService.smali` | поля `oqddtttpsr`, `nnzwevhkoa` | ✅ |
| 5 | BRIDGE без диалога | `smali_classes3/com/soft373/taxi/services/NewOrdersServiceBase.smali` | метод `vlnjtcdbbq(Intent)V` | ✅ |
| 6 | Координаты в адресе (DetailedOrder UI) | `smali_classes3/com/soft373/taxi/data/DetailedOrder$Address.smali` | `getBuilding()` | ✅ p8 |
| 7 | Координаты в Bridge-адресах (Откуда/Куда) | `smali_classes3/com/soft373/taxi/bridge/data/BridgeAddress.smali` | новый метод `getLongCityStreetHouseGeo()` | ✅ p9 |
| 8 | Bridge UI вызывает getLongCityStreetHouseGeo() | `smali_classes3/com/soft373/taxi/activities/OrderActivity.smali` | 4 вызова (FROM/TO × full/short) | ✅ p9 |
| 9 | Bridge интервал заказа 4500ms | `smali_classes3/com/soft373/taxi/bridge/services/BridgeAbstractService.smali` | `bdweufyeak()J` строка 328 | ✅ p9 |

---

## Сессия p9 — Bridge координаты + интервал (текущая)

**Задача:** применить к v3.28 те же патчи что уже работают в v3.26:
- Координаты в Bridge-адресах заказа
- Уменьшить интервал опроса BridgeAbstractService с 20000ms до 4500ms

### Архитектура Bridge-адресов в v3.28

В v3.28 Bridge-адреса хранятся в `BridgeAddress` (не `DetailedOrder$Address`).
Координаты в `BridgeAddress` хранятся **не как lat:D/lon:D**, а как `coord:GeoPoint`.

GeoPoint имеет методы:
- `isZero()Z` — проверка что координаты ненулевые
- `getLatitude()D` — широта
- `getLongitude()D` — долгота

### Патч 7 — новый метод `getLongCityStreetHouseGeo()`

**Файл:** `BridgeAddress.smali`  
**Добавлено после:** `getLongCityStreetHouseComment()` (строка 703)

Логика:
1. Вызывает `getLongCityStreetHouse()` → базовая строка `Город, Улица, Дом`
2. Берёт `coord:GeoPoint`; если null или isZero() → возвращает базовую строку
3. Иначе: StringBuilder + базовая строка + " (lat; lon)"
4. Использует `Double.valueOf(D).toString()` вместо `append(D)` — безопасно для всех ART-устройств

```smali
.method public getLongCityStreetHouseGeo()Ljava/lang/String;
    .locals 6
    # v0=base, v1=GeoPoint, v2=StringBuilder, v3=temp, v4/v5=wide pair
    invoke-virtual {p0}, ...->getLongCityStreetHouse()...
    iget-object v1, p0, ...->coord:GeoPoint
    if-eqz v1, :cond_no_coord
    invoke-virtual {v1}, GeoPoint;->isZero()Z
    if-nez v2, :cond_no_coord
    # StringBuilder: base + " (" + lat + "; " + lon + ")"
    ...Double.valueOf chain...
    :cond_no_coord
    return-object v0
.end method
```

### Патч 8 — OrderActivity: 4 вызова

**Файл:** `OrderActivity.smali`

| Строка | Было | Стало |
|--------|------|-------|
| 978 | `getLongCityStreetHouseComment()` (FROM полный) | `getLongCityStreetHouseGeo()` |
| 989 | `getLongCityStreet()` (FROM краткий) | `getLongCityStreetHouseGeo()` |
| 1088 | `getLongCityStreetHouseComment()` (TO полный) | `getLongCityStreetHouseGeo()` |
| 1099 | `getLongCityStreet()` (TO краткий) | `getLongCityStreetHouseGeo()` |

### Патч 9 — BridgeAbstractService: интервал

**Файл:** `BridgeAbstractService.smali`, метод `bdweufyeak()J`, строка 328

```diff
- const-wide/16 v1, 0x4e20   # 20000ms
+ const-wide/16 v1, 0x1194   # 4500ms
```

Этот метод возвращает интервал для опроса сервера в Bridge-режиме.
При отсутствии активного заказа или NO_AUTHORIZATION/no-connection → возвращает `0xea60` (60000ms, штатный fallback).
При активном заказе или ожидании → `0x1194` (4500ms).

---


---

## ИТОГ: Что сделано и где

| # | Что | Файл | Метод/Место | Статус |
|---|-----|------|-------------|--------|
| 1 | Fake GPS — игнор mock-провайдера | `h2/qfzjddwuyn.smali` | `extxjewlhp(Location)Z` | ✅ |
| 2 | Fake GPS — флаг в конструкторе | `services/NetworkService.smali` | метод `B()V` ~стр.263 | ✅ |
| 3 | Интервал заказа 5000ms (3 места) | `services/NewOrdersServiceBase.smali` | конструктор + onStartCommand | ✅ |
| 4 | Интервал сервера 5000ms | `services/NetworkService.smali` | поля `oqddtttpsr`, `nnzwevhkoa` | ✅ |
| 5 | BRIDGE без диалога | `services/NewOrdersServiceBase.smali` | метод `vlnjtcdbbq(Intent)V` | ✅ |
| 6 | Координаты в адресе (UI) | `data/DetailedOrder$Address.smali` | `getBuilding()` | ✅ p8 |
| 7a | Координаты в toString (лог) | `data/DetailedOrder$Address.smali` | `toString()` | ✅ (лог) |
| 8 | Версия на сплэше | `res/layout/activity_splash.xml` | `android:text` | ✅ p8 |

---

## Хронология сессий и итераций

### Сессия 1 — Первые цели (c042b5f1)

**Задача:** убрать BRIDGE-диалог, установить refresh 4500ms, включить Fake GPS.

Проанализированы файлы по аналогии с уже известной версией 3.14.5. Имена обфусцированы — нашли соответствия вручную.

**Что пробовали:**
1. Искали BRIDGE-флаг по паттерну из 3.14.5 (`smgpnjexwe:Z`) → в 3.28.0 это `rvqpxuketw:Z`
2. Искали `epwdywcysm:I` (таймаут) → нашли `kqhmbgiocc:I`
3. GPS: в 3.14.5 был класс `q0/qfzjddwuyn` → в 3.28.0 это `h2/qfzjddwuyn`

**Результат p1:** BRIDGE и интервал — ok, GPS — ошиблись классом (`ibzphkbtmt$feyxvdiekx` вместо `h2/qfzjddwuyn`)

---

### Сессия 2 — Исправление GPS (1a7f70fc)

**Задача:** GPS не работал после p1 — заказы не показывались ("No GPS - no orders").

**Что пробовали и как нашли:**
1. Искали `isFromMockProvider` по всему smali → нашли в `h2/qfzjddwuyn.smali`, метод `extxjewlhp(Location)Z`
2. Сделали патч — всегда возвращает `false`
3. Проверили конструктор: `NetworkService.B()` передаёт флаг `disableMockLocation=true (0x1)` при создании `h2/qfzjddwuyn`. Даже с патчем на isFromMockProvider — флаг блокировал обновления ещё до вызова метода.
4. Поменяли `0x1 → 0x0` в конструкторе.

**Результат p2:** GPS заработал. Заказы появились.

---

### Сессия 7 — Фикс координат в UI (текущая, 1c32c7d1)

**Задача:** координаты не показывались несмотря на патч p6/p7.

**Диагностика:**
- p7 убрал фильтр `lat==0.0` → координаты всё равно не появились
- Подтверждено: p7 запущен (другой заказ, другое время на скриншоте)
- **Корень проблемы:** `StringBuilder.append(D)` с wide-double регистрами в кастомном smali тихо не работает на устройстве пользователя (возможно ART-специфика)

**Решение p8:** Заменить `append(D)` на цепочку `Double.valueOf(D) → toString() → append(String)`:
```smali
# Вместо: invoke-virtual {v6, v1, v2}, StringBuilder;->append(D)
# Делаем:
invoke-static {v1, v2}, Ljava/lang/Double;->valueOf(D)Ljava/lang/Double;
move-result-object v3
invoke-virtual {v3}, Ljava/lang/Double;->toString()Ljava/lang/String;
move-result-object v3
invoke-virtual {v6, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)
```

**Изменения в p8:**
1. `DetailedOrder$Address.getBuilding()` — полностью переписан (`.locals 5`), без `append(D)`
2. `utils/khjnvckbwi.extxjewlhp()` — координатный блок, `append(D)` → Double.valueOf chain
3. `utils/khjnvckbwi.ibzphkbtmt()` — координатный блок, `append(D)` → Double.valueOf chain
4. Сплэш: `p6 → p8`
5. Также убраны фильтры `if lat==0.0` — координаты показываются всегда (даже 0.0; 0.0 если сервер шлёт нули)

**Урок:** `invoke-virtual {obj, vN, vN+1}` для `append(D)` может не работать в ART на некоторых устройствах. Безопаснее боксировать через `Double.valueOf(D)` и передавать как Object/String.

**Задача:** добавить координаты в адрес заказа, установить интервал 5000ms.

#### Интервал
- `NewOrdersServiceBase.smali`: нашли 3 вхождения `0x1194` → заменили на `0x1388`
- `NetworkService.smali`: поля `oqddtttpsr:I` и `nnzwevhkoa:I` (~стр.263) тоже `0x1194` → `0x1388`

#### Координаты — первая попытка (ПРОВАЛ)
**Где пытались:** `DetailedOrder$Address.smali`, метод `toString()`  
**Что сделали:** Добавили `iget-wide` latitude/longitude и `StringBuilder.append(D)` перед возвратом  
**Ошибка:** Использовали `const-wide/16 v1` — это wide-тип, занимает **два** регистра (v1 И v2). Регистры v1/v2 уже хранили String-объекты → Dalvik Verifier бросил `VerifyError` при загрузке класса → **весь GPS перестал работать** (класс Address не загружался).  
**Урок:** wide-типы (double, long) занимают пару регистров подряд. Нужно увеличивать `.locals` и использовать свободные старшие регистры.

#### Координаты — вторая попытка (частичный успех)
**Что исправили:** `.locals 4 → .locals 7`, использовали `v4/v5` для double (не пересекаются с v0-v3)  
**Результат:** `toString()` работает без краша, координаты видны **в некоторых местах** (логи, список заказов), но **не в карточке заказа**.  
**Причина:** UI карточки вызывает не `toString()`, а `getCity()`, `getStreet()`, `getBuilding()` по отдельности.

**Результат p3:** работает, но координаты в основной карточке не видны.

---

### Сессия 4 — GPS пропал снова (bbba1edc)

**Задача:** после последней сборки "No GPS – no orders" вернулось.

**Что исследовали:**
- `FreeOrdersActivity` — проверяет GPS перед показом заказов
- `h2/qfzjddwuyn` — GPS-менеджер, смотрели логику обновлений
- Проверяли, не сломала ли ошибка в `toString()` загрузку класса `DetailedOrder$Address`

Диагностика прервалась из-за переполнения контекста (>200k токенов).

---

### Сессия 5 — Координаты в реальном UI (текущая, bfff51b3)

**Задача:** координаты не показываются в карточке заказа.

**Как нашли нужное место:**

1. Искали `getBuilding`/`getCity`/`getStreet` в activities — **ничего** (обфусцированы)
2. Искали `DetailedOrder$Address` в activities — ничего
3. Прочитали `OrderActivity.smali` — нашли вызов:
   ```
   invoke-static {v9}, Lcom/soft373/taxi/utils/khjnvckbwi;->extxjewlhp(DetailedOrder)String
   ```
4. Прочитали `utils/khjnvckbwi.smali` целиком — два ключевых метода:
   - `extxjewlhp(DetailedOrder)` — строит строку для **"Куда"** через `getAddressTo()`
   - `ibzphkbtmt(DetailedOrder)` — строит строку для **"Адрес/Откуда"** через `getAddress()`
   - Оба заканчивают на `getBuilding()` без координат

**Первая попытка патча (ошибка):**
- Добавили блок координат в конце, использовали `p1` для вызова `getAddressTo()`
- **Ошибка:** у обоих методов только один параметр `p0`. `p1` не существует.
- Дополнительно: `p0` к концу метода уже **перезаписан** (хранит строку building, не DetailedOrder)

**Исправление:**
- `.locals 4 → .locals 7`
- В **начале** метода (до любых перезаписей p0) сохраняем Address в `v6`:
  ```smali
  invoke-virtual {p0}, ...->getAddressTo()...
  move-result-object v6
  ```
- В блоке координат используем `v6` вместо `p0`/`p1`

**Результат p5:** APK собран, версия отображается — координаты НЕ показались.

---

### Сессия 6 — Разбор рабочего APK v2 (bfff51b3, продолжение)

**Задача:** установить почему p5 не работает.

**Открытие 1:** Установили `tap_taxi_SIGNED_v2_sign.apk` — он показывает координаты (`56,859729; 53,187586` — с запятой, RU Locale).

**Разбор v2 (`taptaxi_v2_decompiled/`):**
- `FreeOrdersActivity.smali` → вызывает утилитный класс `cqwyelzfbm`
- `utils/cqwyelzfbm.smali` — аналог нашего `khjnvckbwi` — **НЕ добавляет координаты сам**
- `data/DetailedOrder$Address.smali` v2 — поля те же: `latitude:D`, `longitude:D`; `toString()` — только лог-формат, без координат

**Вывод:** Координаты приходят **от сервера** в полях `latitude`/`longitude` объекта `Address`, а не строчкой в `building`.

**Открытие 2:** Проблема нашего p5 — `getAddressTo()` возвращает null когда есть `getEndPlace()`. Сохранённый `v6 = null` → координаты не добавляются.

**Правильный подход:** Патчить `getBuilding()` в `DetailedOrder$Address` — он вызывается **всегда** и напрямую читает `latitude`/`longitude` из своего объекта.

**Результат p6:** `getBuilding()` возвращает `"23(56.918; 53.260)"` когда lat != 0.0. ← **текущая версия**

---

## Детали каждого патча (итоговый код)

### Патч 1 — Fake GPS: mock-провайдер
**Файл:** `smali_classes3/h2/qfzjddwuyn.smali`  
**Метод:** `extxjewlhp(Landroid/location/Location;)Z`
```smali
.method private extxjewlhp(Landroid/location/Location;)Z
    .locals 0
    const/4 p1, 0x0   # было: invoke isFromMockProvider + move-result
    return p1
.end method
```

### Патч 2 — Fake GPS: конструктор NetworkService
**Файл:** `smali_classes3/com/soft373/taxi/services/NetworkService.smali`  
**Метод:** `B()V`, ~строка 263
```diff
- const/4 v4, 0x1   # disableMockLocation = true
+ const/4 v4, 0x0
  invoke-direct/range {v0 .. v5}, Lh2/qfzjddwuyn;-><init>(Context;JZLh2/feyxvdiekx;)V
```

### Патч 3 — Интервал заказа 5000ms
**Файл:** `smali_classes3/com/soft373/taxi/services/NewOrdersServiceBase.smali`  
**3 места** (конструктор ~78, onStartCommand ~704, ~728):
```diff
- const/16 v0, 0x1194   # 4500ms
+ const/16 v0, 0x1388   # 5000ms
  iput v0, p0, ...->kqhmbgiocc:I
```

### Патч 4 — Интервал сервера 5000ms
**Файл:** `smali_classes3/com/soft373/taxi/services/NetworkService.smali`  
**Метод:** конструктор, ~строка 263:
```diff
- const/16 v2, 0x1194
+ const/16 v2, 0x1388
  iput v2, p0, ...->oqddtttpsr:I
  iput v2, p0, ...->nnzwevhkoa:I
```

### Патч 5 — BRIDGE без диалога
**Файл:** `smali_classes3/com/soft373/taxi/services/NewOrdersServiceBase.smali`  
**Метод:** `vlnjtcdbbq(Intent)V`
```diff
- iget-boolean v0, p0, ...->rvqpxuketw:Z
+ const/4 v0, 0x0
  invoke-virtual {p0, v0, p1}, ...->pyxggrwgoy(ZLandroid/content/Intent;)V
```

### Патч 6 — Координаты в UI (финальный, p6) ⭐
**Файл:** `smali_classes3/com/soft373/taxi/data/DetailedOrder$Address.smali`  
**Метод:** `getBuilding()` — всегда вызывается из UI

**Почему именно здесь:**  
- `getAddressTo()` возвращает null при наличии `getEndPlace()` → v6=null → предыдущий патч не работал
- `getBuilding()` напрямую обращается к полям `this.latitude` и `this.longitude` → всегда работает

```smali
.method public getBuilding()Ljava/lang/String;
    .locals 7
    # v0=building, v1/v2=lat, v3/v4=0.0_wide, v5=cmpl+temp, v6=StringBuilder
    iget-object v0, p0, ...->building:Ljava/lang/String;
    iget-wide v1, p0, ...->latitude:D
    const-wide/16 v3, 0x0
    cmpl-double v5, v1, v3        # v5=0 если lat==0.0
    if-eqz v5, :cond_no_coords
    
    new-instance v6, Ljava/lang/StringBuilder;
    invoke-direct {v6}, StringBuilder;-><init>()
    if-eqz v0, :cond_skip_building
    invoke-virtual {v6, v0}, StringBuilder;->append(String)   # добавляем building
    :cond_skip_building
    const-string v5, "("
    invoke-virtual {v6, v5}, StringBuilder;->append(String)
    invoke-virtual {v6, v1, v2}, StringBuilder;->append(D)    # latitude
    const-string v5, "; "
    invoke-virtual {v6, v5}, StringBuilder;->append(String)
    iget-wide v1, p0, ...->longitude:D
    invoke-virtual {v6, v1, v2}, StringBuilder;->append(D)    # longitude
    const-string v5, ")"
    invoke-virtual {v6, v5}, StringBuilder;->append(String)
    invoke-virtual {v6}, StringBuilder;->toString()
    move-result-object v0
    
    :cond_no_coords
    return-object v0
.end method
```

### Патч 7 — Координаты в toString (лог, не UI)
**Файл:** `smali_classes3/com/soft373/taxi/data/DetailedOrder$Address.smali`  
**Метод:** `toString()`  
`.locals 4 → .locals 6`, добавлены `iget-wide v4` latitude и longitude с `append(D)` — **работает только в логах**, в основном UI не используется.

### Патч 8 — Версия на сплэше
**Файл:** `res/layout/activity_splash.xml`
```xml
android:text="v3.28.0-p6 [GPS+COORD+5s+ADDR]"
```

---

## Таблица соответствия полей 3.14.5 → 3.28.0

| Смысл | 3.14.5 | 3.28.0 |
|-------|--------|--------|
| BRIDGE флаг | `smgpnjexwe:Z` | `rvqpxuketw:Z` |
| Таймаут заказа | `epwdywcysm:I` | `kqhmbgiocc:I` |
| GPS класс | `q0/qfzjddwuyn` | `h2/qfzjddwuyn` |
| Интервал сервера | аналог | `oqddtttpsr:I` |
| Геттер интервала | аналог | `qzbvjsuekv()I` |

---

## Ключевые уроки

1. **Wide-типы (double/long) занимают 2 регистра подряд.** Если `.locals 4` и используешь `v3`/`v4` для wide — `v4` будет незареги­стрированным вторым регистром пары. Всегда увеличивай `.locals` и используй `v(N), v(N+1)` где оба свободны.

2. **`p0` перезаписывается в середине метода.** В статических методах с одним параметром `p0` часто переиспользуется как временная переменная. Сохраняй нужные объекты в свободные `vN` **в начале** метода.

3. **`toString()` ≠ UI.** Современные Android-приложения вызывают геттеры (`getCity()`, `getStreet()`) напрямую. Патч на `toString()` влияет только на `Log.d()` и места с явным `String.valueOf(object)`.

4. **Dalvik Verifier** проверяет типы **статически** при загрузке класса. Если register type mismatch — класс не загружается вообще, без исключений в рантайме.
