# Recap Studio MM — တပ်ဆင်နည်း (မြန်မာ)

ဒီ project မှာ Website UI နဲ့ Flask backend ပါပါတယ်။ ဗီဒီယိုကို Google Gemini File API သို့ upload လုပ်ပြီး Gemini Interactions API ကို အသုံးပြု၍ မြန်မာ Full Recap script တောင်းဆိုပါတယ်။ Script output အတွက်သာ ဖြစ်ပြီး MP3/MP4 ထုတ်လုပ်မှု မပါသေးပါ။

## ဖုန်းကနေ online တင်ဖို့
1. ZIP ကို download လုပ်ပြီး unzip လုပ်ပါ။
2. GitHub အကောင့်ဝင်ပြီး repository အသစ်ဖန်တီးပါ။ ဖိုင်အားလုံးကို repository root ထဲ upload လုပ်ပါ (app.py, requirements.txt, render.yaml, templates/index.html).
3. Render.com ဝင်ပါ → New → Web Service → GitHub repository ကို connect လုပ်ပါ.
4. Build command: `pip install -r requirements.txt`
5. Start command: `gunicorn app:app --timeout 1800`
6. Environment variables ထဲမှာ `GEMINI_API_KEY` ကို ထည့်ပါ။ API key ကို HTML/code ထဲ မထည့်ပါနဲ့။ `GEMINI_MODEL` မသတ်မှတ်လျှင် `gemini-3.8-flash` ကို သုံးပါ။
7. Deploy ပြီး `https://...onrender.com` လင့်ခ်ကို ဖွင့်ပါ။

## Gemini API key
Google AI Studio မှ API key ဖန်တီးပါ: https://aistudio.google.com/app/apikey
Quota/နိုင်ငံအလိုက် ရရှိမှုနှင့် model availability ကွာနိုင်သည်။ API key ကို အခြားသူအား မပေးပါနှင့်။ API usage free tier ရှိမရှိနှင့် သင့်အကောင့် quota ကို Google AI Studio တွင်စစ်ပါ။

## ကန့်သတ်ချက်
- Render free service သည် အိပ်ပျော်သွားခြင်း၊ request/processing အချိန်ကန့်သတ်ချက်များ ရှိနိုင်သည်။ ရုပ်ရှင်အရှည်ကြီးများကို free hosting မှာ အလုပ်လုပ်မည်ဟု အာမမခံနိုင်ပါ။
- Google Gemini File API သည် free tier တွင် file size 2GB အထိကို documentation မှာ ဖော်ပြထားသော်လည်း quota, model, region နှင့် service limit များအပေါ် မူတည်သည်။
- API/SDK/model behavior ပြောင်းလဲနိုင်သည်။ Deploy ပြီး စမ်းသပ်ရန်လိုသည်။
- ဒီဗားရှင်းက script generation ကိုသာ လုပ်သည်။ Burmese TTS နဲ့ MP4 export မပါသေးပါ။
- ကိုယ်ပိုင် သို့မဟုတ် အသုံးပြုခွင့်ရှိသော ဗီဒီယိုများကိုသာ upload လုပ်ပါ။
