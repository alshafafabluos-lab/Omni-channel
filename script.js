// --- إدارة التنقل بين التبويبات (Navigation Logic) ---
function nav(target) {
    const titleMap = {
        'feed': 'تدفق الرسائل الموحد',
        'publish': 'النشر الموحد (Posts)',
        'reels': 'إدارة الـ Reels والمنشورات النشطة'
    };

    // تحديث العنوان
    document.getElementById('tab-title').innerText = titleMap[target];

    // تحديث شكل الأزرار (إزالة النشط من الكل وإضافته للمختار)
    document.querySelectorAll('nav button').forEach(btn => {
        btn.classList.remove('bg-sky-600/10', 'text-sky-400', 'border-sky-500/20');
        btn.classList.add('text-slate-400');
    });
    
    // إضافة الشكل النشط للزر الحالي
    event.currentTarget.classList.add('bg-sky-600/10', 'text-sky-400', 'border-sky-500/20');
    event.currentTarget.classList.remove('text-slate-400');

    // منطق تبديل المحتوى (سيتم توسيعه لاحقاً)
    console.log(`تم الانتقال إلى قسم: ${target}`);
}

// --- وظيفة النشر الموحد (The Publishing Core) ---
async function publishToAll() {
    const content = document.querySelector('textarea').value;
    
    if (!content) {
        alert("يرجى كتابة محتوى أولاً يا هندسة!");
        return;
    }

    // إظهار حالة التحميل للعميل
    const publishBtn = event.currentTarget;
    publishBtn.innerText = "جاري النشر من جهازك...";
    publishBtn.disabled = true;

    try {
        // استدعاء محرك البايثون مباشرة (Python Bridge)
        const result = await pywebview.api.publish_to_meta(content, ['facebook', 'instagram']);
        
        if (result.status === "success") {
            alert("تم النشر بنجاح على جميع المنصات المحددة ✅");
            document.querySelector('textarea').value = "";
        }
    } catch (error) {
        console.error("فشل الاتصال بالمحرك:", error);
        alert("حدث خطأ في الربط مع المحرك المحلي.");
    } finally {
        publishBtn.innerText = "نشر عبر القنوات";
        publishBtn.disabled = false;
    }
}

// --- تحديث حالة الحسابات لحظياً ---
async function updateStatus() {
    try {
        const status = await pywebview.api.get_status();
        // هنا نقوم بتحديث الأيقونات (أونلاين/أوفلاين) في الواجهة
        console.log("حالة الحسابات الحالية:", status);
    } catch (e) {
        // المحرك لم يعمل بعد
    }
}

// تشغيل تحديث الحالة كل 30 ثانية
setInterval(updateStatus, 30000);
