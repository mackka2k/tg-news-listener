# 📚 Pavyzdžiai ir FAQ

## Pavyzdiniai keywords scenarijai

### Scenario 1: Tik labai svarbios naujienos
```env
KEYWORDS=важно,срочно,breaking,эксклюзив,расследование
MAX_POSTS_PER_DAY=3
```
Rezultatas: Tik labai svarbios, skubios naujienos - ~2-3 per dieną

### Scenario 2: Tech ir AI fokusas
```env
KEYWORDS=AI,искусственный интеллект,технологии,наука,ChatGPT,нейросети,робот,квантовый
MAX_POSTS_PER_DAY=5
```
Rezultatas: Daugiau tech/AI naujienų - ~4-5 per dieną

### Scenario 3: Geopolitika ir Lietuva
```env
KEYWORDS=Литва,Lithuania,политика,война,Украина,НАТО,NATO,ЕС,EU,Россия,санкции
MAX_POSTS_PER_DAY=7
```
Rezultatas: Fokusas į geopolitiką ir Lietuvą - ~5-7 per dieną

### Scenario 4: Viskas įdomu (platus filtras)
```env
KEYWORDS=важно,новость,AI,технологии,наука,политика,экономика,скандал,расследование,Литва
MAX_POSTS_PER_DAY=10
```
Rezultatas: Platus spektras - ~8-10 per dieną

---

## Dažniausiai užduodami klausimai

### Q: Ar botas veiks su privačiais kanalais?
**A:** Taip, bet tavo Telegram paskyra turi būti prenumeruojanti tuos kanalus. Botas naudoja tavo paskyrą, todėl mato viską ką ir tu matai.

### Q: Ar galiu naudoti ne savo paskyrą?
**A:** Taip, gali sukurti atskirą Telegram paskyrą tik botui. Bet reikės tos paskyros telefono numerio ir prisijungimo kodo.

### Q: Ar Telegram neužblokuos manęs už forward'inimą?
**A:** Ne, jei neviršiji ~20-30 forward'ų per valandą. Mūsų botas limituotas 5 per dieną, tai visiškai saugu. Telegram leidžia forward'inti, tik ne spam'inti.

### Q: Kaip pridėti daugiau kanalų?
**A:** Atidaryk `.env` failą ir pridėk prie `SOURCE_CHANNELS`:
```env
SOURCE_CHANNELS=@topor,@cybers,@Scienceg,@CleverMindRu_Official,@politikaf,@naujas_kanalas
```
Užtikrink, kad tavo paskyra prenumeruoja naują kanalą!

### Q: Ar galiu forward'inti į grupę vietoj kanalo?
**A:** Taip! Vietoj `@channel_username` naudok grupės ID (pvz. `-1001234567890`). Gauk ID per @getidsbot.

### Q: Kaip išjungti botą?
**A:** Tiesiog spausk `Ctrl+C` terminale. Jei deploy'intas Railway - sustabdyk deployment'ą.

### Q: Ar botas ištrins originalias žinutes?
**A:** Ne! Botas tik forward'ina (kopijuoja) žinutes. Originalai lieka savo kanaluose.

### Q: Kaip pakeisti, kad ne forward'intų, o kopijuotų be "Forwarded from"?
**A:** Pakeisk `bot.py` eilutę:
```python
# Vietoj:
await self.client.forward_messages(self.config.TARGET_CHANNEL, event.message)

# Naudok:
await self.client.send_message(self.config.TARGET_CHANNEL, event.message)
```

### Q: Ar galiu pridėti savo tekstą prie kiekvieno posto?
**A:** Taip! Pakeisk `bot.py`:
```python
# Pridėk prieš forward'inimą:
custom_text = f"📰 Šaltinis: {source_name}\n\n{message_text}"
await self.client.send_message(self.config.TARGET_CHANNEL, custom_text)
```

### Q: Kaip matyti statistiką (kiek forward'inta per dieną)?
**A:** Pažiūrėk `bot.log` failą - ten logojama kiekviena operacija. Arba pridėk paprastą counter'į `bot.py`.

### Q: Ar veiks su anglų kalbos kanalais?
**A:** Taip! Tiesiog pakeisk keywords į anglų kalbą:
```env
KEYWORDS=breaking,urgent,important,AI,technology,science,politics,exclusive,investigation
```

### Q: Kaip pridėti emoji prie forward'intų postų?
**A:** Pakeisk `bot.py` forward'inimo dalį:
```python
await self.client.send_message(
    self.config.TARGET_CHANNEL, 
    f"🔥 {event.message.text}"
)
```

### Q: Ar galiu filtruoti pagal žinutės ilgį (pvz. tik ilgas)?
**A:** Taip! Pridėk į `should_forward` funkciją:
```python
if len(message_text) < 100:
    return False, "Per trumpa žinutė"
```

### Q: Kaip išvengti dublikatų jei keli kanalai postina tą patį?
**A:** Botas jau saugo `forwarded_messages` set'ą, bet tai veikia tik per session'ą. Jei nori permanent - naudok SQLite database (galiu pridėti jei reikia).

---

## Pavyzdiniai log'ai

### Sėkminga operacija:
```
2026-02-08 14:23:15 - INFO - 📨 Nauja žinutė iš ТОПОР - Горячие новости
2026-02-08 14:23:15 - INFO -    Tekstas: 🚨 ВАЖНО: Новое расследование показало...
2026-02-08 14:23:15 - INFO -    ✅ Keywords: важно, расследование
2026-02-08 14:23:16 - INFO -    ✅ FORWARD'INTA! (3/5 šiandien)
```

### Atmesta žinutė (nėra keywords):
```
2026-02-08 14:25:30 - INFO - 📨 Nauja žinutė iš Cyber Security
2026-02-08 14:25:30 - INFO -    Tekstas: Сегодня хорошая погода...
2026-02-08 14:25:30 - INFO -    Nėra keyword'ų
2026-02-08 14:25:30 - INFO -    ⏭️ Praleista
```

### Atmesta žinutė (spam):
```
2026-02-08 14:27:45 - INFO - 📨 Nauja žinutė iš ТОПОР - Горячие новости
2026-02-08 14:27:45 - INFO -    Tekstas: Купить криптовалюту со скидкой...
2026-02-08 14:27:45 - INFO -    Spam keyword: купить
2026-02-08 14:27:45 - INFO -    ⏭️ Praleista
```

### Viršytas limitas:
```
2026-02-08 20:15:00 - INFO - 📨 Nauja žinutė iš Science
2026-02-08 20:15:00 - INFO -    Tekstas: Важное научное открытие...
2026-02-08 20:15:00 - INFO -    Viršytas dienos limitas (5)
2026-02-08 20:15:00 - INFO -    ⏭️ Praleista
```

---

## Performance tips

### Sumažinti CPU/RAM naudojimą:
```python
# bot.py - pridėk delay tarp tikrinimų
await asyncio.sleep(1)  # Tikrina kas 1 sekundę vietoj realtime
```

### Pagreitinti forward'inimą:
```python
# Pašalinti delay po forward'o (bet gali sukelti FloodWait)
# await asyncio.sleep(2)  # Užkomentuok šią eilutę
```

### Sumažinti log'ų dydį:
```python
# config.py - pakeisk logging level
logging.basicConfig(level=logging.WARNING)  # Vietoj INFO
```

---

## Saugumo patarimai

1. **NIEKADA** nesidalink `.env` failu
2. **NIEKADA** necommit'ink `session.session` failo į GitHub
3. **NIEKADA** nerodyti `API_HASH` viešai
4. Jei kompromituotas - iš karto revoke API key per https://my.telegram.org
5. Naudok atskirą Telegram paskyrą botui (ne savo pagrindinę)

---

## Deployment checklist

Prieš deploy'inant į Railway/Render:

- [ ] Patikrintas lokaliai - veikia
- [ ] `.env` failas užpildytas
- [ ] `session.session` failas sukurtas (po pirmo prisijungimo)
- [ ] `.gitignore` turi `.env` ir `*.session`
- [ ] Railway Environment Variables užpildyti
- [ ] Pirmą kartą prisijungta lokaliai (Railway negali interaktyviai įvesti kodo)

---

**Jei turi daugiau klausimų - rašyk! 😊**
