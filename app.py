import webview
import os
import requests
import sqlite3
import json
from datetime import datetime

class OHubAPI:
    def __init__(self):
        # إعدادات الروابط الأساسية
        self.fb_base_url = "https://graph.facebook.com/v19.0"
        
        # بيانات الاعتماد (تبدأ فارغة ويملأها المستخدم)
        self.fb_token = None
        self.fb_page_id = None
        self.wa_token = None
        self.wa_phone_id = None
        
        # تشغيل قاعدة البيانات المحلية فوراً
        self.db_init()

    # --- 1. إدارة قاعدة البيانات (الأرشفة المحلية) ---
    def db_init(self):
        """إنشاء سجل البيانات على جهاز المستخدم لضمان الخصوصية"""
        conn = sqlite3.connect('ohub_local.db')
        c = conn.cursor()
        # جدول المحادثات
        c.execute('''CREATE TABLE IF NOT EXISTS messages 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      platform TEXT, sender TEXT, content TEXT, time TEXT)''')
        conn.commit()
        conn.close()

    def save_to_local_db(self, platform, sender, content):
        """حفظ أي رسالة أو تعليق محلياً"""
        conn = sqlite3.connect('ohub_local.db')
        c = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO messages (platform, sender, content, time) VALUES (?, ?, ?, ?)",
                  (platform, sender, content, now))
        conn.commit()
        conn.close()

    # --- 2. إعدادات الربط (Settings) ---
    def update_credentials(self, fb_token, fb_page_id, wa_token=None, wa_phone_id=None):
        """تحديث مفاتيح الربط من واجهة المستخدم"""
        self.fb_token = fb_token
        self.fb_page_id = fb_page_id
        self.wa_token = wa_token
        self.wa_phone_id = wa_phone_id
        return {"status": "success", "message": "تم تحديث جميع المفاتيح بنجاح"}

    # --- 3. وظائف الفيسبوك وإنستجرام (Meta) ---
    def publish_post(self, message, platforms):
        """النشر الموحد عبر المنصات المحددة"""
        if not self.fb_token or not self.fb_page_id:
            return {"status": "error", "message": "المفاتيح غير مضبوطة"}

        results = []
        if 'facebook' in platforms:
            url = f"{self.fb_base_url}/{self.fb_page_id}/feed"
            try:
                res = requests.post(url, data={'message': message, 'access_token': self.fb_token})
                results.append({"platform": "facebook", "status": res.status_code})
            except Exception as e:
                results.append({"platform": "facebook", "status": "failed", "error": str(e)})
        
        return {"status": "success", "details": results}

    def get_live_feed(self):
        """جلب التعليقات الحية (الشيء الخرافي)"""
        if not self.fb_token: return []
        try:
            url = f"{self.fb_base_url}/{self.fb_page_id}/posts?fields=comments.limit(5),message&access_token={self.fb_token}"
            data = requests.get(url).json()
            feed = []
            if 'data' in data:
                for post in data['data']:
                    if 'comments' in post:
                        comment = post['comments']['data'][0]
                        feed.append({
                            "post": post.get('message', 'Post')[:30],
                            "user": comment['from']['name'] if 'from' in comment else "User",
                            "comment": comment['message']
                        })
                        # أرشفة تلقائية للتعليق الجديد
                        self.save_to_local_db("Facebook", "User", comment['message'])
            return feed
        except:
            return []

    # --- 4. وظائف الواتساب (WhatsApp) ---
    def send_whatsapp(self, receiver_phone, message_text):
        """إرسال رسالة واتساب رسمية (Cloud API)"""
        if not self.wa_token: return {"status": "error", "message": "واتساب غير مربوط"}
        
        url = f"https://graph.facebook.com/v19.0/{self.wa_phone_id}/messages"
        headers = {"Authorization": f"Bearer {self.wa_token}", "Content-Type": "application/json"}
        payload = {
            "messaging_product": "whatsapp",
            "to": receiver_phone,
            "type": "text",
            "text": {"body": message_text}
        }
        res = requests.post(url, headers=headers, json=payload)
        return res.json()

# --- تشغيل البرنامج ---
if __name__ == '__main__':
    api = OHubAPI()
    
    # تحديد مسار ملف الواجهة
    current_path = os.path.dirname(os.path.abspath(__file__))
    html_file = os.path.join(current_path, "index.html")

    # إنشاء النافذة
    window = webview.create_window(
        title='O-Hub Omni | Unified Console',
        url=html_file,
        js_api=api,
        width=1280,
        height=850,
        background_color='#020617'
    )

    webview.start(debug=False)
