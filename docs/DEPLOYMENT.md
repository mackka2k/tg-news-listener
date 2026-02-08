# 🚀 Railway.app Deployment Guide

Kaip deploy'inti botą į Railway.app, kad veiktų 24/7 nemokamai.

---

## ⚠️ SVARBU - Pirmiausia paleisk lokaliai!

**Railway negali interaktyviai įvesti Telegram autentifikacijos kodo**, todėl:

1. **Pirmiausia paleisk lokaliai** (žiūrėk [QUICKSTART.md](QUICKSTART.md))
2. **Prisijunk prie Telegram** - įvesk telefono numerį ir kodą
3. **Bus sukurtas `session.session` failas** - jame saugoma autentifikacija
4. **Tik tada** deploy'ink į Railway

---

## 📋 Deployment žingsniai

### 1️⃣ Sukurk Railway paskyrą

1. Eik į https://railway.app/
2. Spausk **Login** → **Login with GitHub**
3. Authorize Railway

### 2️⃣ Sukurk naują projektą

1. Spausk **New Project**
2. Pasirink **Deploy from GitHub repo**
3. Jei dar neprijungei GitHub:
   - Spausk **Configure GitHub App**
   - Pasirink repozitorijas (arba "All repositories")
4. Pasirink `news-bot` repo

### 3️⃣ Pridėk Environment Variables

Railway automatiškai aptiks `requirements.txt` ir įdiegs dependencies, bet reikia pridėti config:

1. Spausk **Variables** tab
2. Pridėk šias variables:

```
API_ID = tavo_api_id
API_HASH = tavo_api_hash
TARGET_CHANNEL = @tavo_channel
SOURCE_CHANNELS = @topor,@cybers,@Scienceg,@CleverMindRu_Official,@politikaf
MAX_POSTS_PER_DAY = 5
KEYWORDS = важно,срочно,breaking,AI,искусственный интеллект,технологии,наука,политика,Литва,Lithuania,новость,эксклюзив,расследование
SPAM_KEYWORDS = реклама,купить,скидка,промокод,казино,ставки
```

3. Spausk **Add** kiekvienai variable

### 4️⃣ Setup Session File

**CRITICAL**: Session files contain full access to your Telegram account. NEVER commit them to Git!

**Recommended Approach - Railway Volumes:**

1. Railway → **Volumes** → **New Volume**
2. Mount path: `/app`
3. After first local run, upload `session.session` to volume via Railway dashboard

**Alternative - Railway CLI:**

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link project
railway link

# Upload session (use with caution)
railway up session.session
```

**⚠️ SECURITY WARNING**: 
- Session files = full Telegram account access
- Git history preserves deleted files forever
- Even private repos can become public accidentally
- NEVER use "Variantas A" - it's a security risk!
- Use volumes or CLI upload instead

### 5️⃣ Deploy!

1. Railway automatiškai deploy'ins po kiekvieno push'o
2. Arba spausk **Deploy** rankiniu būdu
3. Pažiūrėk **Logs** - turėtų rašyti:
   ```
   ✅ Prisijungta kaip: Tavo Vardas
   ✅ Target kanalas rastas: Svarbiausios Žinios
   ✅ Veikia 5/5 kanalai
   👂 Klausausi naujų žinučių...
   ```

### 6️⃣ Patikrink ar veikia

1. Railway → **Logs** → turėtų būti aktyvus
2. Palaukti 10-30 min kol kažkas papostins su keywords
3. Patikrinti savo Telegram kanalą - turėtų atsirasti naujiena!

---

## 🔧 Troubleshooting

### "Cannot find session file"
→ Upload'ink `session.session` failą (žiūrėk žingsnį 4️⃣)

### "ValueError: API_ID nenustatytas"
→ Patikrink ar Environment Variables teisingai pridėtos (žiūrėk žingsnį 3️⃣)

### "FloodWaitError"
→ Per daug forward'ų - sumažink `MAX_POSTS_PER_DAY` arba palaukti

### Botas nuolat restartinasi
→ Pažiūrėk Logs - gali būti klaida config'e arba session'as pasenęs

### "SessionPasswordNeededError"
→ Turi 2FA - reikia prisijungti lokaliai su slaptažodžiu, tada upload'inti naują session

---

## 💰 Kainos

**Railway Free Tier:**
- 500 execution hours/mėn (pakanka 24/7!)
- $5 credit/mėn
- Unlimited projects

**Šis botas naudoja:**
- ~0.01 CPU
- ~50MB RAM
- Beveik 0 network (tik Telegram API)

**Išvada**: Visiškai telpa į free tier! 🎉

---

## 📊 Monitoring

### Kaip matyti ar veikia:

1. **Railway Logs**:
   - Railway → **Logs** tab
   - Matysis visi bot'o log'ai realiu laiku

2. **Metrics**:
   - Railway → **Metrics** tab
   - CPU/RAM naudojimas

3. **Telegram kanalas**:
   - Tiesiog pažiūrėk ar ateina naujienos!

### Alerts:

Railway gali siųsti email'us jei:
- Deployment fails
- Service crashes
- Viršijamas free tier

---

## 🔄 Kaip update'inti botą

### Jei pakeitei kodą lokaliai:

```bash
git add .
git commit -m "Update bot"
git push
```

Railway automatiškai re-deploy'ins!

### Jei pakeitei tik Environment Variables:

1. Railway → **Variables** → Edit
2. Railway automatiškai restartins botą

---

## 🛑 Kaip sustabdyti

### Laikinai:

Railway → **Settings** → **Pause Deployment**

### Visam laikui:

Railway → **Settings** → **Delete Service**

---

## 🔐 Saugumas

### ⚠️ NIEKADA:

- Nesidalink `session.session` failu
- Necommit'ink session į public GitHub repo
- Nerodyti Environment Variables viešai
- Nesidalink Railway project link'u

### ✅ VISADA:

- Naudok private GitHub repo jei commit'ini session
- Reguliariai tikrink Railway Logs
- Revoke API key jei įtari kompromitavimą (https://my.telegram.org)

---

## 🎯 Alternatyvos Railway

Jei Railway neveikia arba nori kitą platformą:

### Render.com
- Panašus į Railway
- 750h/mėn free tier
- Setup: https://render.com/docs/deploy-python

### Heroku
- Mokamas (nuo $7/mėn)
- Labai patikimas
- Setup: https://devcenter.heroku.com/articles/getting-started-with-python

### VPS (Hetzner, DigitalOcean)
- ~$3-5/mėn
- Pilna kontrolė
- Reikia daugiau setup'o

### Savo kompiuteris
- Nemokamas
- Veikia tik kai kompiuteris įjungtas
- Geras testavimui

---

## ✅ Deployment Checklist

Prieš deploy'inant:

- [ ] Botas veikia lokaliai
- [ ] `session.session` failas sukurtas
- [ ] GitHub repo sukurtas (private jei commit'insi session)
- [ ] Railway paskyra sukurta
- [ ] Environment Variables paruoštos
- [ ] `.gitignore` turi `.env` (bet ne `session.session` jei nori commit'inti)

Po deploy'inimo:

- [ ] Logs rodo "Prisijungta kaip..."
- [ ] Logs rodo "Klausausi naujų žinučių..."
- [ ] Telegram kanale atsiranda naujienos (palaukti 10-30 min)

---

**Sėkmės su deployment'u! 🚀**

Jei kažkas neveikia - pažiūrėk Railway Logs ir šį guide'ą dar kartą.
