# ⚡ GREITAS PALEIDIMAS

## Problema su interaktyviu prisijungimu

Jei matai klaidą `EOFError` - tai reiškia, kad botas negali interaktyviai prašyti telefono numerio.

## ✅ Sprendimas - Paleisk rankiniu būdu

1. **Atidaryk naują PowerShell/Command Prompt langą**

2. **Eik į projekto direktoriją**:
   ```powershell
   cd C:\Users\Admin\Desktop\news-bot
   ```

3. **Paleisk botą**:
   ```powershell
   python bot.py
   ```

4. **Įvesk telefono numerį** kai paprašys:
   ```
   Please enter your phone (or bot token): +37060012345
   ```

5. **Įvesk gautą kodą** iš Telegram:
   ```
   Please enter the code you received: 12345
   ```

6. **Jei turi 2FA** - įvesk slaptažodį:
   ```
   Please enter your password: tavo_slaptazodis
   ```

7. **Turėtų pasirodyt**:
   ```
   ✅ Prisijungta kaip: Tavo Vardas
   ✅ Target kanalas rastas: Svarbiausios Žinios
   ✅ Veikia 5/5 kanalai
   👂 Klausausi naujų žinučių...
   ```

8. **Palikti langą atvirą** - botas veikia!

---

## 🔧 Alternatyva - Pridėk telefono numerį į .env

Jei nori automatinį prisijungimą, pridėk į `.env`:

```env
PHONE_NUMBER=+37060012345
```

Ir pakeisk `bot.py` eilutę 86:
```python
# Vietoj:
await self.client.start()

# Naudok:
await self.client.start(phone=lambda: os.getenv('PHONE_NUMBER'))
```

Bet **pirmą kartą vis tiek reikia rankiniu būdu**, nes reikia įvesti kodą!

---

## 📱 Svarbu

**Pirmą kartą BŪTINAI paleisk rankiniu būdu** (žingsniai 1-7 aukščiau), kad sukurtų `session.session` failą. Po to galėsi deploy'inti į Railway ir veiks automatiškai!
