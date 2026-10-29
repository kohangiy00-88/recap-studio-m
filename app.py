import os, time, mimetypes, requests
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_UPLOAD_MB', '1800')) * 1024 * 1024
API_BASE = 'https://generativelanguage.googleapis.com/v1beta'
MODEL = os.getenv('GEMINI_MODEL', 'gemini-3.8-flash')

@app.get('/')
def home():
    return render_template('index.html')

@app.get('/health')
def health():
    return jsonify({'ok': True, 'api_key_configured': bool(os.getenv('GEMINI_API_KEY'))})

def upload_to_gemini(path, filename, mime_type, key):
    size = os.path.getsize(path)
    headers = {
        'X-Goog-Upload-Protocol': 'resumable',
        'X-Goog-Upload-Command': 'start',
        'X-Goog-Upload-Header-Content-Length': str(size),
        'X-Goog-Upload-Header-Content-Type': mime_type,
        'Content-Type': 'application/json',
        'x-goog-api-key': key,
    }
    r = requests.post(f'{API_BASE}/files', headers=headers, json={'file': {'display_name': filename}}, timeout=60)
    r.raise_for_status()
    upload_url = r.headers.get('X-Goog-Upload-URL') or r.headers.get('x-goog-upload-url')
    if not upload_url:
        raise RuntimeError('Google upload URL မရပါ။ API key / quota ကို စစ်ပါ။')
    with open(path, 'rb') as f:
        r = requests.post(upload_url, headers={
            'Content-Length': str(size), 'X-Goog-Upload-Offset': '0',
            'X-Goog-Upload-Command': 'upload, finalize', 'Content-Type': mime_type
        }, data=f, timeout=3600)
    r.raise_for_status()
    return r.json().get('file', r.json())

@app.post('/api/recap')
def recap():
    key = os.getenv('GEMINI_API_KEY')
    if not key:
        return jsonify({'error': 'Server မှာ GEMINI_API_KEY မသတ်မှတ်ရသေးပါ။ Render → Environment မှာ API key ထည့်ပါ။'}), 503
    f = request.files.get('video')
    if not f or not f.filename:
        return jsonify({'error': 'ရုပ်ရှင်ဗီဒီယိုဖိုင်ကို အရင်ရွေးပါ။'}), 400
    name = secure_filename(f.filename) or 'movie.mp4'
    mime = f.mimetype or mimetypes.guess_type(name)[0] or 'video/mp4'
    if not mime.startswith('video/'):
        return jsonify({'error': 'ဗီဒီယိုဖိုင် (MP4/MOV/WEBM စသည်) ကိုသာ တင်ပါ။'}), 400
    duration = request.form.get('duration', 'အပြည့်အစုံ')
    style = request.form.get('style', 'စိတ်ဝင်စားဖွယ် ဇာတ်လမ်းပြောဟန်')
    focus = request.form.get('focus', 'ဇာတ်လမ်းအဓိက ၈၀% + ခံစားချက် ၂၀%')
    tmp = f'/tmp/{int(time.time())}_{name}'
    try:
        f.save(tmp)
        video = upload_to_gemini(tmp, name, mime, key)
        file_name = video.get('name')
        if not file_name:
            raise RuntimeError('Google က file reference ပြန်မပေးပါ။')
        # Wait for Google video processing to finish.
        for _ in range(180):
            status_r = requests.get(f'{API_BASE}/{file_name}', headers={'x-goog-api-key': key}, timeout=30)
            status_r.raise_for_status()
            current = status_r.json()
            state = current.get('state')
            if state == 'ACTIVE':
                video = current
                break
            if state == 'FAILED':
                raise RuntimeError('Google က ဗီဒီယိုဖိုင်ကို မဖတ်နိုင်ခဲ့ပါ။ အခြား MP4 ဖိုင်နဲ့ စမ်းပါ။')
            time.sleep(5)
        else:
            raise RuntimeError('ဗီဒီယိုပြင်ဆင်ချိန် ကြာလွန်းနေပါတယ်။ ဖိုင်တိုနဲ့ ပြန်စမ်းပါ။')
        prompt = f'''သင်သည် မြန်မာဘာသာဖြင့် ရုပ်ရှင်ဇာတ်ကြောင်းကို အစမှအဆုံး ပြန်လည်ဖော်ပြသည့် narration စာရေးဆရာဖြစ်သည်။
တင်ထားသော ရုပ်ရှင်ကို ရရှိနိုင်သမျှ အစဉ်လိုက် စူးစမ်းပြီး အကျဉ်းချုပ်တိုတစ်ခုသာ မရေးပါနှင့်။ ဇာတ်ကွက်များ၊ ဇာတ်ကောင်တွေ့ဆုံမှု၊ အကြောင်းရင်းနှင့် အကျိုးဆက်၊ အရေးကြီးဆုံးဆုံးဖြတ်ချက်များ၊ climax နှင့် ending တို့ကို အစမှအဆုံး ဇာတ်ကြောင်းဆက်စပ်စွာ ရေးပါ။ မျက်နှာအမူအရာ/ခံစားချက်များကို သက်ဆိုင်ရာနေရာတွင် ထည့်ပါ။ မမြင်ရသောအချက်များကို မတီထွင်ပါနှင့်၊ မသေချာလျှင် သေချာသလို မပြောပါနှင့်။
အရေးအသား: {style}
အာရုံစိုက်မှု: {focus}
ရည်ရွယ်ထားသော narration ကြာချိန်: {duration}
မြန်မာလို သဘာဝကျကျ၊ ဇာတ်ကြောင်းအစဉ်လိုက်၊ အပိုင်းခေါင်းစဉ်နှင့် အချိန်မှတ်သားချက်များပါလျှင် ကောင်းသည်။ အဖြေကို script သာပေးပါ။ ရုပ်ရှင်သည် အလွန်ရှည်လျှင် အရေးကြီးသောအပိုင်းများကို မပျောက်စေဘဲ တတ်နိုင်သမျှ အသေးစိတ်ရေးပြီး မဖုံးလွှမ်းနိုင်သည့်အရာကို မဖုံးလွှမ်းခဲ့သလို မဆိုပါနှင့်။'''
        payload = {'model': MODEL, 'input': [
            {'type': 'video', 'uri': video.get('uri'), 'mime_type': video.get('mimeType') or mime, 'processing': 'agentic'},
            {'type': 'text', 'text': prompt}
        ]}
        rr = requests.post(f'{API_BASE}/interactions', headers={'x-goog-api-key': key, 'Content-Type':'application/json'}, json=payload, timeout=1800)
        if not rr.ok:
            raise RuntimeError(f'Gemini API ပြန်စာ {rr.status_code}: {rr.text[:700]}')
        data = rr.json()
        text = data.get('output_text')
        if not text:
            pieces = []
            for step in data.get('steps', []):
                for c in step.get('content', []):
                    if c.get('type') == 'text' and c.get('text'):
                        pieces.append(c['text'])
            text = '\n\n'.join(pieces)
        if not text:
            raise RuntimeError('AI က စာသားမပြန်ပေးပါ။ API response ကို စစ်ဆေးရန်လိုသည်။')
        return jsonify({'script': text, 'model': MODEL, 'note': 'AI ထုတ်ပေးသော script ဖြစ်သည်။ ရုပ်ရှင်တစ်ကားလုံးကို အပြည့်အဝဖုံးလွှမ်းကြောင်း မအာမခံနိုင်ပါ။'})
    except requests.HTTPError as e:
        detail = ''
        try: detail = e.response.text[:700]
        except Exception: pass
        return jsonify({'error': f'API ဆက်သွယ်မှု မအောင်မြင်ပါ။ API key, quota သို့မဟုတ် model ကို စစ်ပါ။ {detail}'}), 502
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        try:
            if os.path.exists(tmp): os.remove(tmp)
        except Exception: pass

@app.errorhandler(413)
def too_large(_):
    return jsonify({'error': 'ဖိုင်အရွယ်အစားက server limit ထက်ကြီးနေပါတယ်။ MAX_UPLOAD_MB ကို စစ်ပါ။ Hosting ရဲ့ request limit လည်း သက်ရောက်နိုင်ပါတယ်။'}), 413

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '10000')))
