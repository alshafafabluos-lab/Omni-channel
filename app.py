import webview
import os
import requests
import json

class OHubAPI:
    def __init__(self):
        # بيانات الربط (تبدأ فارغة ويملأها العميل من الواجهة)
        self.access_token = None
        self.page_id = None
        self.fb_base_url = "https://graph.facebook.com/v19.0"

    def update_credentials(self, token, page_id):
        """تحديث مفاتيح الربط في ذاكرة البرنامج"""
        try:
            self.access_token = token
            self.page_id = page_id
            print(f"Credentials Updated for Page: {page_id}")
            return {"status": "success", "message": "تم تحديث البيانات بنجاح"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_status(self):
        """التحقق من حالة الاتصال"""
        return {
            "facebook": self.access_token is not None,
            "instagram": self.access_token is not None, # يعتمد على نفس التوكن في الغالب
            "whatsapp": False # سيتم ربطه لاحقاً
        }

    def publish_to_meta(self, message, platforms):
        """منطق النشر الحقيقي على فيسبوك"""
        if not self.access_token or not self.page_id:
            return {"status": "error", "message": "يرجى ضبط الإعدادات أولاً"}

        results = []
        if 'facebook' in platforms:
            url = f"{self.fb_base_url}/{self.page_id}/feed"
            payload = {'message': message, 'access_token': self.access_token}
            try:
                response = requests.post(url, data=payload)
                res_data = response.json()
                if response.status_code == 200:
                    results.append({"platform": "facebook", "status": "success", "id": res_data.get('id')})
                else:
                    results.append({"platform": "facebook", "status": "error", "msg": res_data.get('error', {}).get('message')})
            except Exception as e:
                results.append({"platform": "facebook", "status": "error", "msg": str(e)})

        return {"status": "success", "details": results}

    def fetch_live_feed(self):
        """جلب المنشورات التي تحتوي على تعليقات (الشيء الخرافي)"""
        if not self.access_token or not self.page_id:
            return []

        try:
            url = f"{self.fb_base_url}/{self.page_id}/posts?fields=comments.limit(5),message,created_time&access_token={self.access_token}"
            response = requests.get(url).json()
            
            active_feed = []
            if 'data' in response:
                for post in response['data']:
                    if 'comments' in post:
                        active_feed.append({
                            "id": post['id'],
                            "text": post.get('message', 'منشور بدون نص')[:50] + "...",
                            "count": len(post['comments']['data']),
                            "last_comment": post['comments']['data'][0]['message'],
                            "platform": "facebook"
                        })
            return active_feed
        except:
            return []

def start_logic():
    print("O-Hub Omni Production Engine is Live.")

if __name__ == '__main__':
    api_bridge = OHubAPI()
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_dir, "index.html")

    window = webview.create_window(
        title='O-Hub Omni | Enterprise Edition',
        url=html_path,
        js_api=api_bridge,
        width=1280,
        height=850,
        background_color='#020617',
        confirm_close=True
    )

    webview.start(start_logic, debug=False)
