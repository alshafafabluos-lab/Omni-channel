class OHubAPI:
    def __init__(self):
        self.fb_base_url = "https://graph.facebook.com/v19.0"
        # هذه المفاتيح يجب أن تُجلب من إعدادات البرنامج التي يدخلها العميل
        self.access_token = None 
        self.page_id = None

    def publish_to_meta(self, message, platforms):
        """نشر بوست موحد على فيسبوك وإنستجرام"""
        results = []
        
        # 1. النشر على فيسبوك
        if 'facebook' in platforms:
            fb_url = f"{self.fb_base_url}/{self.page_id}/feed"
            payload = {'message': message, 'access_token': self.access_token}
            response = requests.post(fb_url, data=payload)
            results.append({"platform": "facebook", "status": response.status_code})

        # 2. النشر على إنستجرام (عبر API ميتا الموحد)
        # ملاحظة: إنستجرام يتطلب خطوات إضافية للصور، هنا نجهز الهيكل
        if 'instagram' in platforms:
            # منطق رفع الميديا لإنستجرام
            pass

        return {"status": "success", "details": results}

    def fetch_comments_logic(self):
        """جلب التعليقات الجديدة من آخر المنشورات"""
        if not self.access_token: return []
        
        url = f"{self.fb_base_url}/{self.page_id}/posts?fields=comments.limit(5),message,created_time&access_token={self.access_token}"
        response = requests.get(url).json()
        
        active_posts = []
        if 'data' in response:
            for post in response['data']:
                if 'comments' in post:
                    active_posts.append({
                        "id": post['id'],
                        "message": post.get('message', 'منشور بدون نص'),
                        "comments_count": len(post['comments']['data']),
                        "latest_comment": post['comments']['data'][0]['message']
                    })
        return active_posts
