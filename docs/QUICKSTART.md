# 🚀 GREITAS STARTAS (5 MINUTĖS)

## 1️⃣ Sukurk Telegram kanalą (2 min)

1. **Atidaryk Telegram** (mobilioje ar desktop)
2. **Spausk**:
   - Mobile: ☰ Menu → New Channel
   - Desktop: ☰ Menu → New Channel
3. **Užpildyk**:
   - **Pavadinimas**: `Svarbiausios Žinios` (arba kažką panašaus)
   - **Aprašymas**: `Tik svarbiausia iš geriausių kanalų. Max 5 postai/dieną.`
4. **Pasirink Public Channel**
5. **Sugalvok username**: pvz. `@svarbiausios_lt` (turi būti laisvas)
6. **✅ NUKOPIJUOK** savo username - reikės vėliau!

---

## 2️⃣ Gauk Telegram API kredencialus (2 min)

1. **Eik į**: https://my.telegram.org/auth
2. **Prisijunk** su savo telefono numeriu
3. **Spausk**: `API development tools`
4. **Užpildyk formą**:
   ```
   App title: News Bot
   Short name: newsbot
   Platform: Desktop
   ```
5. **Spausk**: `Create application`
6. **✅ NUKOPIJUOK**:
   - `api_id` (skaičius, pvz. 12345678)
   - `api_hash` (eilutė, pvz. abc123def456...)

---

## 3️⃣ Įdiegk ir paleisk (1 min)

### Windows:

```powershell
# 1. Įdiegk dependencies
pip install -r requirements.txt

# 2. Sukurk .env failą
copy .env.example .env

# 3. Atidaryk .env su Notepad
notepad .env

# 4. Užpildyk:
#    API_ID=tavo_api_id
#    API_HASH=tavo_api_hash
#    TARGET_CHANNEL=@tavo_username
# Išsaugok ir uždaryk

# 5. Paleisk!
python bot.py
```

### Pirmą kartą paleidus:

```
📱 Įvesk telefono numerį (su kodu): +37060012345
📱 Įvesk gautą kodą iš Telegram: 12345
✅ Prisijungta!
👂 Klausausi naujų žinučių...
```

**SVARBU**: Palikti terminalo langą atvirą - botas veikia!

---

## 🎯 Kaip patikrinti ar veikia?

1. **Pažiūrėk terminalo langą** - turėtų rašyti:
   ```
   ✅ Prisijungta kaip: Tavo Vardas
   ✅ Target kanalas rastas: Svarbiausios Žinios
   ✅ Veikia 5/5 kanalai
   👂 Klausausi naujų žinučių...
   ```

2. **Palaukti 5-10 min** - kai @topor ar kiti kanalai postins ką nors su keywords (pvz. "важно", "AI", "политика") - automatiškai pasirodys tavo kanale!

3. **Pažiūrėk `bot.log` failą** - ten matysis visos žinutės ir kodėl buvo forward'intos ar atmestos

---

## ⚙️ Kaip keisti nustatymus?

Atidaryk `.env` failą ir keisk:

```env
# Pridėti daugiau keywords (atskirti kableliais)
KEYWORDS=важно,срочно,AI,технологии,наука,политика,Литва

# Pakeisti max postų skaičių
MAX_POSTS_PER_DAY=10

# Pridėti daugiau šaltinių
SOURCE_CHANNELS=@topor,@cybers,@Scienceg,@tavo_kanalas
```

Po pakeitimų - sustabdyk botą (Ctrl+C) ir paleisk iš naujo (`python bot.py`)

---

## 🌐 24/7 veikimas (Railway.app)

Kad botas veiktų nuolat (net kai kompiuteris išjungtas):

1. **Sukurk paskyrą**: https://railway.app/
2. **New Project** → **Deploy from GitHub repo**
3. **Prijunk šį projektą**
4. **Pridėk Environment Variables**:
   - `API_ID` = tavo api_id
   - `API_HASH` = tavo api_hash
   - `TARGET_CHANNEL` = @tavo_username
   - (kitus gali palikti default)
5. **Deploy!** Veiks 24/7 nemokamai

**SVARBU**: Pirmą kartą vis tiek reikia paleisti lokaliai (žingsnis 3), nes Railway negali interaktyviai įvesti Telegram kodo.

---

## 🆘 Problemos?

**"Cannot find any entity corresponding to @..."**
→ Patikrink ar username teisingas ir ar esi kanalo adminas

**"FloodWaitError"**
→ Telegram laikinai apribojo - palaukti keletą minučių

**Neforward'ina žinučių**
→ Pažiūrėk `bot.log` - ten matysis kodėl atmesta (pvz. nėra keywords, viršytas limitas)

**Reikia 2FA slaptažodžio**
→ Įvesk savo Telegram slaptažodį kai paprašys

---

**Sėkmės! 🚀**
