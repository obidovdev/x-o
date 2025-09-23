# X-O Bot 🎮

**Telegram X-O (Tic-Tac-Toe) Bot**
Bu bot orqali foydalanuvchilar Telegramda real-time tarzda X va O o‘yinini o‘ynashlari mumkin.

---

## 📌 Asosiy xususiyatlar

* 🎲 Tasodifiy raqib bilan o‘yin boshlash
* ⬜ 3x3 inline tugmalar orqali real-time o‘yin
* ⭕ ❌ belgilar bilan navbat ko‘rsatish
* O‘yin yakunida natijani saqlash (`G‘olib`, `Durrang`)
* Profil va o‘yin statistikasi ko‘rish (`Necha o‘yin, qancha vaqt`)
* Top o‘yinchilar ro‘yxati
* O‘yin tugagach, boardni bosib bo‘lmaydi va alert ko‘rsatiladi

---

## 📦 Texnologiyalar

* Python 3.13+
* [Aiogram 3.7.x](https://docs.aiogram.dev/)
* SQLite3 (o‘yin va statistika ma’lumotlarini saqlash uchun)

---

## ⚡ O‘rnatish

1. Repozitoriyani klonlash:

```bash
git clone https://github.com/axrorback/x-o-bot.git
cd x-o-bot
```

2. Virtual environment yaratish va faollashtirish:

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. Kerakli paketlarni o‘rnatish:

```bash
pip install -r requirements.txt
```

4. `.env` fayl yaratish va token qo‘shish:

```env
TOKEN=BOTNING_TOKENI
```

---

## 🛠️ Ishga tushirish

```bash
python app.py
```

* Bot ishga tushadi va foydalanuvchilar bilan interaktiv o‘yin boshlash mumkin bo‘ladi.
* `/start` orqali boshlang.

---

## 📋 Foydalanish

### Asosiy tugmalar:

* 🎲 **Tasodifiy raqib** – tasodifiy boshqa foydalanuvchi bilan o‘yin boshlash
* 📊 **Profilim** – foydalanuvchi statistikasi (necha o‘yin, qancha vaqt)
* 🏆 **Top o‘yinchilar** – eng faol foydalanuvchilar
* ❌ **O‘yin tugatish** – joriy o‘yinni tugatish

### O‘yin jarayoni:

* Inline board orqali 3x3 kataklarni bosish mumkin
* Navbat kimda ekanligi inline board yuqorisida ko‘rsatiladi (`Navbat: ❌ X` yoki `Navbat: ⭕ O`)
* O‘yin yakunlanganda inline board avtomatik bloklanadi, yangi yurish bo‘lmaydi, alert chiqadi

---

## 📂 Fayl tuzilishi

```
xo_bot/
├─ app.py
├─ config.py
├─ db.py
├─ keyboards.py
├─ requirements.txt
└─ handlers/
|   ├─ __init__.py
|   ├─ start.py
|   ├─ game.py
|   └─ profile.py
└─README.md   
   
```

---

## 🤝 Hissa qo‘shish

* Pull request yuborishingiz mumkin
* Xatolik yoki takliflar bo‘lsa issues oching

---

## ⚖️ Litsenziya

MIT License
