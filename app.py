from datetime import datetime, date
from dateutil import parser
import re
import math
import random
import sqlite3

app = Flask(__name__)
app.secret_key = "numero-annand-ai-secure-key"

# =========================================================
# DATABASE INITIALIZATION (To prevent fraud and save addresses)
# =========================================================
def init_db():
    conn = sqlite3.connect('/tem/orders.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            utr_number TEXT UNIQUE,
            name TEXT,
            dob TEXT,
            mobile TEXT,
            lang TEXT,
            order_type TEXT,
            address TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# =========================================================
# CONFIG
# =========================================================
WHATSAPP_CONSULT_LINK = "https://wa.me/917099805039"
WHATSAPP_GROUP_LINK = "https://chat.whatsapp.com/C5g8MVpA0SYASAyrZfsrtJ?mode=gi_t"

MASTER_NUMBERS = {11, 22, 33}

# =========================================================
# CHALDEAN MAP
# =========================================================
CHALDEAN_MAP = {
    'A':1,'I':1,'J':1,'Q':1,'Y':1,
    'B':2,'K':2,'R':2,
    'C':3,'G':3,'L':3,'S':3,
    'D':4,'M':4,'T':4,
    'E':5,'H':5,'N':5,'X':5,
    'U':6,'V':6,'W':6,
    'O':7,'Z':7,
    'F':8,'P':8
}

# =========================================================
# RELATIONSHIPS
# =========================================================
NUM_RELATIONS = {
    1:{'friends':[1,2,3,5,7,9],'neutral':[4,8],'enemy':[6]},
    2:{'friends':[1,2,3,5],'neutral':[4,7,8,9],'enemy':[6]},
    3:{'friends':[1,2,3,5,7,9],'neutral':[6,8],'enemy':[4]},
    4:{'friends':[1,5,6,7],'neutral':[2,8,9],'enemy':[3]},
    5:{'friends':[1,2,3,5,6,8],'neutral':[4,7,9],'enemy':[]},
    6:{'friends':[5,6,7,8],'neutral':[3,4,9],'enemy':[1,2]},
    7:{'friends':[1,3,4,5,6],'neutral':[2,8,9],'enemy':[]},
    8:{'friends':[4,5,6,7],'neutral':[1,2,3],'enemy':[8,9]},
    9:{'friends':[1,2,3,5,7],'neutral':[4,6],'enemy':[8,9]}
}

# =========================================================
# MULTI-LANGUAGE TRANSLATION DICTIONARIES
# =========================================================
TRANSLATIONS = {
    'en': {
        'workspace_menu': 'Workspace Menu',
        'name_label': 'Name For Analysis',
        'dob_label': 'Date Of Birth',
        'mobile_label': 'Mobile Number (Optional)',
        'lang_label': 'Select Analysis Language',
        'btn_analyze': 'Analyze Now',
        'consult_folder': 'Consultation Folder',
        'strategist': 'Primary Strategist:',
        'contact': 'Contact:',
        'chat_wa': '💬 Chat on WhatsApp',
        'premium_services': 'Premium Personal Services:',
        'btn_consult': 'Consult with Annand Sarma',
        'wa_group_folder': 'WhatsApp Group Folder',
        'btn_open_wa': 'Open WhatsApp Group',
        'p1_title': '📘 PAGE 1 — CORE NUMEROLOGY PROFILE',
        'p2_title': '📗 PAGE 2 — FULL LO SHU GRID ANALYSIS',
        'p3_title': '📙 PAGE 3 — ADVANCED PSYCHOLOGICAL & SPIRITUAL ANALYSIS',
        'p4_title': '📕 PAGE 4 — NAME CORRECTION & LIFE GUIDANCE',
        'p5_title': '📒 PAGE 5 — DEEP AI PROFESSIONAL REPORT',
        'freq_title': '📊 COMPLETE FREQUENCY ANALYSIS',
        'missing_title': '🔍 Missing Numbers',
        'repeated_title': '🔥 Repeated Numbers',
        'missing_desc': 'These absent frequencies indicate karmic lessons and developmental areas requiring conscious improvement.',
        'repeated_desc': 'Repeated vibrations increase energetic intensity and amplify specific personality dimensions.',
        'mental_title': '🧠 Mental Plane Analysis',
        'mental_desc': 'The Mental Plane reflects intellectual clarity, planning ability, memory structure, and analytical vision. Strong mental numbers indicate strategic intelligence and powerful visualization capability.',
        'emotional_title': '❤️ Emotional Plane Analysis',
        'emotional_desc': 'The Emotional Plane represents empathy, emotional reactions, intuition, compassion, and relationship sensitivity. Balanced emotional numbers improve harmony, emotional maturity, and communication quality.',
        'practical_title': '💼 Practical Plane Analysis',
        'practical_desc': 'The Practical Plane governs execution ability, discipline, financial stability, consistency, and career implementation. Strong practical numbers create structured progress and material success potential.',
        'arrow_title': '🧿 Arrow Analysis',
        'arrow_desc': 'Your Lo Shu Grid reveals hidden energetic pathways influencing determination, willpower, emotional control, spirituality, discipline, and communication style. Strong arrows improve internal alignment while broken arrows reveal karmic learning zones.',
        'raj_title': '👑 Raj Yog Potential',
        'raj_desc': 'The interaction between your Driver Number, Destiny vibration, and Lo Shu structure suggests strong potential for recognition, authority, leadership, and long-term influence. Consistent discipline and emotionally balanced decision-making can significantly improve manifestation power.',
        'psych_title': '🧠 Psychological Traits',
        'psych_desc': 'Your chart suggests a deeply layered psychological structure influenced by both conscious ambition and subconscious karmic memory patterns. You may naturally seek meaning, stability, emotional security, and purposeful growth rather than temporary achievements.',
        'spiritual_title': '🪷 Spiritual Traits',
        'spiritual_desc': 'Spiritual development becomes important when your inner vibration begins searching for emotional clarity, energetic balance, and deeper life purpose. Meditation, self-awareness, disciplined routine, and positive environments improve spiritual stability.',
        'career_title': '💼 Career Guidance',
        'career_desc': 'Your numerological structure supports fields connected to communication, guidance, teaching, management, spirituality, consulting, analytics, business development, and public interaction. Long-term success improves when emotional balance and disciplined routines are maintained consistently.',
        'rel_title': '❤️ Relationship Guidance',
        'rel_desc': 'Relationship harmony improves through patience, emotional openness, balanced communication, and mutual understanding. Your emotional vibration seeks sincerity, respect, loyalty, and psychological depth within relationships.',
        'fin_title': '💰 Financial Guidance',
        'fin_desc': 'Financial stability increases through strategic planning, long-term discipline, and practical money management. Avoid impulsive financial decisions during emotionally unstable periods.',
        'lucky_title': '🍀 Lucky Indicators',
        'deep_title': '🧠 Human-Style Deep Interpretation',
        'deep_desc': 'Your complete numerological blueprint reveals a personality carrying both intellectual sensitivity and long-term growth potential. The interaction between your Driver vibration, Destiny path, and Name frequency creates a life pattern focused on self-development, responsibility, emotional evolution, and gradual manifestation. Periods of internal confusion generally appear when emotional pressure overrides logical structure. However, your chart also shows strong recovery potential, resilience, and adaptability.',
        'forecast_title': '📈 Yearly Forecast',
        'forecast_desc': 'The upcoming energetic cycle favors structured decision-making, strategic planning, financial awareness, and emotional maturity. New opportunities may emerge through communication, networking, guidance roles, or knowledge-sharing activities.',
        'roadmap_title': '🪷 Spiritual Roadmap',
        'roadmap_desc': 'Meditation, focused routine, spiritual reading, gratitude practice, and balanced environments help stabilize your energetic field. Avoid negative surroundings, emotional overthinking, and inconsistent routines.',
        'remedies_title': '🧿 Remedies',
        'success_title': '🚀 Success Strategy',
        'success_desc': 'Long-term success emerges when emotional intelligence, discipline, communication skills, and spiritual balance operate together. Your chart rewards patience, structured planning, consistency, and positive social contribution more than short-term shortcuts.',
        'premium_box_title': '📥 Get Your Complete Premium Offline Report',
        'premium_box_desc': 'Unlock your fully personalized, beautifully formatted extensive master blueprint edition.',
        'scan_pay': 'Scan via PhonePe / Any UPI App to Pay:',
        'important_note': '⚠️ Important: After finishing your payment, click the button below to instantly notify me via Email with your confirmation screenshot.',
        'btn_paid': 'I Have Paid - Notify via Email'
    },
    'hi': {
        'workspace_menu': 'कार्यक्षेत्र मेनू',
        'name_label': 'विश्लेषण के लिए नाम',
        'dob_label': 'जन्म तिथि',
        'mobile_label': 'मोबाइल नंबर (वैकल्पिक)',
        'lang_label': 'विश्लेषण भाषा चुनें',
        'btn_analyze': 'अभी विश्लेषण करें',
        'consult_folder': 'परामर्श फ़ोल्डर',
        'strategist': 'मुख्य रणनीतिककार:',
        'contact': 'संपर्क:',
        'chat_wa': '💬 व्हाट्सएप पर चैट करें',
        'premium_services': 'प्रीमियम व्यक्तिगत सेवाएं:',
        'btn_consult': 'आनंद शर्मा से परामर्श करें',
        'wa_group_folder': 'व्हाट्सएप ग्रुप फ़ोल्डर',
        'btn_open_wa': 'व्हाट्सएप ग्रुप खोलें',
        'p1_title': '📘 पेज 1 — मुख्य अंकज्योतिष प्रोफाइल',
        'p2_title': '📗 पेज 2 — पूर्ण लो शू ग्रिड विश्लेषण',
        'p3_title': '📙 पेज 3 — उन्नत मनोवैज्ञानिक और आध्यात्मिक विश्लेषण',
        'p4_title': '📕 पेज 4 — नाम सुधार और जीवन मार्गदर्शन',
        'p5_title': '📒 पेज 5 — गहन एआई प्रोफेशनल रिपोर्ट',
        'freq_title': '📊 पूर्ण आवृत्ति विश्लेषण',
        'missing_title': '🔍 लुप्त अंक (Missing Numbers)',
        'repeated_title': '🔥 दोहराए गए अंक',
        'missing_desc': 'ये अनुपस्थित आवृत्तियां कर्म पाठ और विकासात्मक क्षेत्रों को दर्शाती हैं जिनमें सचेत सुधार की आवश्यकता है।',
        'repeated_desc': 'दोहराए गए कंपन ऊर्जा की तीव्रता को बढ़ाते हैं और विशिष्ट व्यक्तित्व आयामों को मजबूत करते हैं।',
        'mental_title': '🧠 मानसिक तल विश्लेषण (Mental Plane)',
        'mental_desc': 'मानसिक तल बौद्धिक स्पष्टता, योजना क्षमता, स्मृति संरचना और विश्लेषणात्मक दृष्टि को दर्शाता है। मजबूत मानसिक अंक रणनीतिक बुद्धिमत्ता और शक्तिशाली कल्पना क्षमता का संकेत देते हैं।',
        'emotional_title': '❤️ भावनात्मक तल विश्लेषण (Emotional Plane)',
        'emotional_desc': 'भावनात्मक तल सहानुभूति, भावनात्मक प्रतिक्रियाओं, अंतर्ज्ञान, करुणा और संबंधों के प्रति संवेदनशीलता का प्रतिनिधित्व करता है। संतुलित भावनात्मक अंक सद्भाव और भावनात्मक परिपक्वता में सुधार करते हैं।',
        'practical_title': '💼 व्यावहारिक तल विश्लेषण (Practical Plane)',
        'practical_desc': 'व्यावहारिक तल निष्पादन क्षमता, अनुशासन, वित्तीय स्थिरता, निरंतरता और करियर कार्यान्वयन को नियंत्रित करता है। मजबूत व्यावहारिक अंक संरचित प्रगति और भौतिक सफलता की क्षमता बनाते हैं।',
        'arrow_title': '🧿 तीर विश्लेषण (Arrow Analysis)',
        'arrow_desc': 'आपका लो शू ग्रिड दृढ़ संकल्प, इच्छाशक्ति, भावनात्मक नियंत्रण, आध्यात्मिकता, अनुशासन और संचार शैली को प्रभावित करने वाले छिपे हुए ऊर्जा मार्गों को प्रकट करता है।',
        'raj_title': '👑 राजयोग क्षमता',
        'raj_desc': 'आपके ड्राइवर नंबर, भाग्य कंपन और लो शू संरचना के बीच का तालमेल पहचान, अधिकार, नेतृत्व और दीर्घकालिक प्रभाव की मजबूत क्षमता का सुझाव देता है।',
        'psych_title': '🧠 मनोवैज्ञानिक लक्षण',
        'psych_desc': 'आपका चार्ट सचेत महत्वाकांक्षा और अवचेतन कर्मिक स्मृति पैटर्न दोनों से प्रभावित एक गहरी मनोवैज्ञानिक संरचना का सुझाव देता है। आप अस्थायी उपलब्धियों के बजाय स्वाभाविक रूप से स्थिरता और भावनात्मक सुरक्षा की तलाश कर सकते हैं।',
        'spiritual_title': '🪷 आध्यात्मिक लक्षण',
        'spiritual_desc': 'आद्यात्मिक विकास तब महत्वपूर्ण हो जाता है जब आपका आंतरिक कंपन भावनात्मक स्पष्टता, ऊर्जावान संतुलन और गहरे जीवन उद्देश्य की खोज शुरू करता है। ध्यान और आत्म-जागरूकता से स्थिरता आती है।',
        'career_title': '💼 करियर मार्गदर्शन',
        'career_desc': 'आपकी अंकज्योतिष संरचना संचार, मार्गदर्शन, शिक्षण, प्रबंधन, आध्यात्मिकता, परामर्श, विश्लेषण और व्यवसाय विकास से जुड़े क्षेत्रों का समर्थन करती है।',
        'rel_title': '❤️ संबंध मार्गदर्शन',
        'rel_desc': 'धैर्य, भावनात्मक खुलेपन, संतुलित संचार और आपसी समझ के माध्यम से संबंधों में सामंजस्य सुधरता है। आपका कंपन रिश्तों में ईमानदारी, सम्मान और वफादारी चाहता है।',
        'fin_title': '💰 वित्तीय मार्गदर्शन',
        'fin_desc': 'रणनीतिक योजना, दीर्घकालिक अनुशासन और व्यावहारिक धन प्रबंधन के माध्यम से वित्तीय स्थिरता बढ़ती है। भावनात्मक रूप से अस्थिर अवधि के दौरान जल्दबाजी में वित्तीय निर्णय लेने से बचें।',
        'lucky_title': '🍀 भाग्यशाली संकेतक',
        'deep_title': '🧠 मानव-शैली गहन व्याख्या',
        'deep_desc': 'आपका संपूर्ण अंकज्योतिष खाका बौद्धिक संवेदनशीलता और दीर्घकालिक विकास क्षमता दोनों से युक्त व्यक्तित्व को प्रकट करता है। आपके ड्राइवर कंपन, भाग्य पथ और नाम आवृत्ति के बीच की परस्पर क्रिया आत्म-विकास और जिम्मेदारी पर केंद्रित जीवन पैटर्न बनाती है।',
        'forecast_title': '📈 वार्षिक पूर्वानुमान',
        'forecast_desc': 'आगामी ऊर्जा चक्र संरचित निर्णय लेने, रणनीतिक योजना, वित्तीय जागरूकता और भावनात्मक परिपक्वता के अनुकूल है। संचार और नेटवर्किंग के माध्यम से नए अवसर उभर सकते हैं।',
        'roadmap_title': '🪷 आध्यात्मिक रोडमैप',
        'roadmap_desc': 'ध्यान, केंद्रित दिनचर्या, आध्यात्मिक अध्ययन, आभार व्यक्त करना और संतुलित वातावरण आपके ऊर्जा क्षेत्र को स्थिर करने में मदद करते हैं। नकारात्मक परिवेश से बचें।',
        'remedies_title': '🧿 उपाय',
        'success_title': '🚀 सफलता की रणनीति',
        'success_desc': 'दीर्घकालिक सफलता तब उभरती है जब भावनात्मक बुद्धिमत्ता, अनुशासन, संचार कौशल और आध्यात्मिक संतुलन एक साथ काम करते हैं। आपका चार्ट शॉर्टकट के बजाय निरंतरता को पुरस्कृत करता है।',
        'premium_box_title': '📥 अपनी संपूर्ण प्रीमियम ऑफलाइन रिपोर्ट प्राप्त करें',
        'premium_box_desc': 'अपने पूरी तरह से व्यक्तिगत, खूबसूरती से स्वरूपित व्यापक मास्टर ब्लूप्रिंट संस्करण को अनलॉक करें।',
        'scan_pay': 'भुगतान करने के लिए PhonePe / किसी भी UPI ऐप के माध्यम से स्कैन करें:',
        'important_note': '⚠️ महत्वपूर्ण: अपना भुगतान पूरा करने के बाद, स्क्रीनशॉट के साथ मुझे तुरंत ईमेल के माध्यम से सूचित करने के लिए नीचे दिए गए बटन पर क्लिक करें।',
        'btn_paid': 'मैंने भुगतान कर दिया है - ईमेल के माध्यम से सूचित करें'
    },
    'as': {
        'workspace_menu': 'কৰ্মক্ষেত্ৰ মেনু',
        'name_label': 'বিশ্লেষণৰ বাবে নাম',
        'dob_label': 'জন্মৰ তাৰিখ',
        'mobile_label': 'ম’বাইল নম্বৰ (ঐচ্ছিক)',
        'lang_label': 'বিশ্লেষণৰ ভাষা বাছনি কৰক',
        'btn_analyze': 'এতিয়াই বিশ্লেষণ কৰক',
        'consult_folder': 'পৰামৰ্শ ফোল্ডাৰ',
        'strategist': 'প্ৰাথমিক ৰণনীতিবিদ:',
        'contact': 'যোগাযোগ:',
        'chat_wa': '💬 হোৱাটছএপত চেট কৰক',
        'premium_services': 'প্ৰিমিয়াম ব্যক্তিগত সেৱাসমূহ:',
        'btn_consult': 'আনন্দ শৰ্মাৰ সৈতে পৰামৰ্শ কৰক',
        'wa_group_folder': 'হোৱাটছএপ গ্ৰুপ ফোল্ডাৰ',
        'btn_open_wa': 'হোৱাটছএপ গ্ৰুপ খোলক',
        'p1_title': '📘 পৃষ্ঠা ১ — মূল সংখ্যাতত্ত্ব প্ৰফাইল',
        'p2_title': '📗 পৃষ্ঠা ২ — পূৰ্ণ লো শ্বু গ্ৰীড বিশ্লেষণ',
        'p3_title': '📙 পৃষ্ঠা ৩ — উন্নত মানসিক আৰু আধ্যাত্মিক বিশ্লেষণ',
        'p4_title': '📕 পৃষ্ঠা ৪ — নাম সংশোধন আৰু জীৱন নিৰ্দেশনা',
        'p5_title': '📒 পৃষ্ঠা ৫ — গভীৰ এআই প্ৰফেচনেল ৰিপৰ্ট',
        'freq_title': '📊 সম্পূৰ্ণ ফ্ৰিকুৱেন্সী বিশ্লেষণ',
        'missing_title': '🔍 হেৰুৱা সংখ্যাসমূহ (Missing Numbers)',
        'repeated_title': '🔥 পুনৰাবৃত্তি হোৱা সংখ্যা',
        'missing_desc': 'এই অনুপস্থিত কম্পনসমূহে কৰ্মফলৰ শিক্ষা আৰু সচেতন উন্নতিৰ প্ৰয়োজন হোৱা বিকাশৰ ক্ষেত্ৰসমূহ সূচায়।',
        'repeated_desc': 'পুনৰাবৃত্তি হোৱা কম্পনে শক্তিৰ তীব্ৰতা বৃদ্ধি কৰে আৰু নিৰ্দিষ্ট ব্যক্তিত্বৰ মাত্ৰাসমূহ প্ৰসাৰিত কৰে।',
        'mental_title': '🧠 মানসিক সমতল বিশ্লেষণ (Mental Plane)',
        'mental_desc': 'মানসিক সমতলে বৌদ্ধিক স্পষ্টতা, পৰিকল্পনা ক্ষমতা, স্মৃতিশক্তিৰ গঠন আৰু বিশ্লেষণাত্মক দৃষ্টিভংগী প্ৰতিফলিত কৰে। শক্তিশালী মানসিক সংখ্যাই ৰণনৈতিক বুদ্ধিমত্তা সূচায়।',
        'emotional_title': '❤️ আৱেগিক সমতল বিশ্লেষণ (Emotional Plane)',
        'emotional_desc': 'আৱেগিক সমতলে সহানুভূতি, আৱেগিক প্ৰতিক্ৰিয়া, অন্তৰ্দৃষ্টি আৰু সম্পৰ্কৰ প্ৰতি সংবেদনশীলতাক প্ৰতিনিধিত্ব কৰে। সন্তুলিত আৱেগিক সংখ্যাই সম্পৰ্ক মধুৰ কৰে।',
        'practical_title': '💼 ব্যৱহাৰিক সমতল বিশ্লেষণ (Practical Plane)',
        'practical_desc': 'ব্যৱহাৰিক সমতলে কাৰ্য্যকৰী ক্ষমতা, অনুশাসন, বিত্তীয় স্থিৰতা আৰু কেৰিয়াৰ ৰূপায়ণ নিয়ন্ত্ৰণ কৰে। শক্তিশালী ব্যৱহাৰিক সংখ্যাই বস্তুগত সফলতাৰ সম্ভাৱনা সৃষ্টি কৰে।',
        'arrow_title': '🧿 কাড় বিশ্লেষণ (Arrow Analysis)',
        'arrow_desc': 'আপোনাৰ লো শ্বু গ্ৰীডে দৃঢ় সংকল্প, ইচ্ছাশক্তি, আৱেগিক নিয়ন্ত্ৰণ, আধ্যাত্মিকতা আৰু যোগাযোগ শৈলীক প্ৰভাৱিত কৰা গুপ্ত শক্তিৰ পথসমূহ প্ৰকাশ কৰে।',
        'raj_title': '👑 ৰাজ যোগ সম্ভাৱনা',
        'raj_desc': 'আপোনাৰ ড্ৰাইভাৰ নম্বৰ, ভাগ্যৰ কম্পন আৰু লো শ্বু গঠনৰ মাজৰ ভাৰসাম্যই স্বীকৃতি, কৰ্তৃত্ব, নেতৃত্ব আৰু দীৰ্ঘকালীন প্ৰভাৱৰ শক্তিশালী সম্ভাৱনা সূচায়।',
        'psych_title': '🧠 মানসিক বৈশিষ্ট্যসমূহ',
        'psych_desc': 'আপোনাৰ চাৰ্টে সচেতন উচ্চাকাংক্ষা আৰু অৱচেতন কৰ্মফলৰ স্মৃতি দুয়োটাৰে প্ৰভাৱিত এক গভীৰ মানসিক গাঁথনি সূচায়। আপুনি সাময়িক সাফল্যতকৈ স্থিৰতা বিচাৰিব পাৰে।',
        'spiritual_title': '🪷 আধ্যাত্মিক বৈশিষ্ট্যসমূহ',
        'spiritual_desc': 'আধ্যাত্মিক বিকাশ তেতিয়া গুৰুত্বপূৰ্ণ হৈ পৰে যেতিয়া আপোনাৰ অন্তৰ্নিহিত কম্পনে আৱেগিক স্পষ্টতা আৰু গভীৰ জীৱনৰ উদ্দেশ্য বিচাৰিবলৈ আৰম্ভ কৰে।',
        'career_title': '💼 কেৰিয়াৰ নিৰ্দেশনা',
        'career_desc': 'আপোনার সংখ্যাতাত্ত্বিক গঠনে যোগাযোগ, নিৰ্দেশনা, শিক্ষাদান, ব্যৱস্থাপনা, আধ্যাত্মিকতা, পৰামৰ্শ আৰু ব্যৱসায়িক বিকাশৰ সৈতে জড়িত ক্ষেত্ৰসমূহক সমৰ্থন কৰে।',
        'rel_title': '❤️ সম্পৰ্ক নিৰ্দেশনা',
        'rel_desc': 'ধৈৰ্য্য, আৱেগিক উদাৰতা, সন্তুলিত যোগাযোগ আৰু পাৰস্পৰিক বুজাবুজিৰ জৰিয়তে সম্পৰ্কৰ মধুৰতা বৃদ্ধি পায়। আপোনাৰ কম্পনে সম্পৰ্কত সততা আৰু আনুগত্য বিচাৰে।',
        'fin_title': '💰 বিত্তীয় নিৰ্দেশনা',
        'fin_desc': 'ৰণনৈতিক পৰিকল্পনা, দীৰ্ঘকালীন অনুশাসন আৰু ব্যৱহাৰিক ধন ব্যৱস্থাপনাৰ জৰিয়তে বিত্তীয় স্থিৰতা বৃদ্ধি পায়। আৱেগিকভাৱে অস্হিৰ সময়ত বিত্তীয় সিদ্ধান্ত নলব।',
        'lucky_title': '🍀 ভাগ্যশালী সূচকসমূহ',
        'deep_title': '🧠 মানৱ-শৈলীৰ গভীৰ ব্যাখ্যা',
        'deep_desc': 'আপোনাৰ সম্পূৰ্ণ সংখ্যাতত্ত্বৰ ব্লুপ্ৰিণ্টে বৌদ্ধিক সংবেদনশীলতা আৰু দীৰ্ঘকালীন বিকাশৰ সম্ভাৱনা দুয়োলাকে কঢ়িয়াই অনা এটা ব্যক্তিত্ব প্ৰকাশ কৰে। ই আত্ম-বিকাশত সহায় কৰে।',
        'forecast_title': '📈 বাৰ্ষিক পূৰ্বানুমান',
        'forecast_desc': 'অহা শক্তিৰ চক্ৰটোৱে গাঁথনিগত সিদ্ধান্ত গ্ৰহণ, ৰণনৈতিক পৰিকল্পনা, বিত্তীয় সজাগতা আৰু আৱেগিক পৰিপক্কতাক সমৰ্থন কৰে। নতুন সুযোগৰ সৃষ্টি হ’ব পাৰে।',
        'roadmap_title': '🪷 আধ্যাত্মিক ৰোডমেপ',
        'roadmap_desc': 'ধ্যান, কেন্দ্ৰীভূত দিনচৰ্যা, আধ্যাত্মিক পঠন আৰু কৃতজ্ঞতা অনুশীলনে আপোনাৰ শক্তি ক্ষেত্ৰখনক সুস্থিৰ কৰাত সহায় কৰে। ঋণাত্মক পৰিৱেশ পৰিহাৰ কৰক।',
        'remedies_title': '🧿 প্ৰতিকাৰসমূহ',
        'success_title': '🚀 সফলতাৰ ৰণনীতি',
        'success_desc': 'দীৰ্ঘকালীন সফলতা তেতিয়া আহে যেতিয়া আৱেগিক বুদ্ধিমত্তা, অনুশাসন, যোগাযোগ দক্ষতা আৰু আধ্যাত্মিক ভাৰসাম্য একেলগে কাম কৰে। চুটি পথতকৈ ধাৰাবাহিকতাক গুৰুত্ব দিয়ক।',
        'premium_box_title': '📥 আপোনাৰ সম্পূৰ্ণ প্ৰিমিয়াম অফলাইন ৰিপৰ্ট লাভ কৰক',
        'premium_box_desc': 'আপোনাৰ সম্পূৰ্ণ ব্যক্তিগতকৃত, ধুনীয়াকৈ ফৰ্মেট কৰা মাষ্টাৰ ব্লুপ্ৰিণ্ট সংস্কৰণটো আনলক কৰক।',
        'scan_pay': 'পৰিশোধ কৰিবলৈ PhonePe / যিকোনো UPI অ্যাপৰ জৰিয়তে স্কেন কৰক:',
        'important_note': '⚠️ গুৰুত্বপূৰ্ণ: আপোনাৰ ধন পৰিশোধ সম্পূৰ্ণ কৰাৰ পিছত, স্ক্ৰীণশ্বটৰ সৈতে মোক লগে লগে ইমেইলৰ জৰিয়তে জনাবলৈ তলৰ বুটামত ক্লিক কৰক।',
        'btn_paid': 'মই পৰিশোধ কৰিছোঁ - ইমেইলৰ জৰিয়তে জনাওক'
    }
}

# =========================================================
# CSS + UI
# =========================================================
STYLE = """
:root{ --bg:#070d19; --card:#10192d; --accent:#00ffd5; --accent2:#00a2ff; --text:#f3f3f3; --muted:#9ba7ba; --border:#243b60; } 
body{ margin:0; padding:0; font-family:'Segoe UI',Arial; background: radial-gradient(circle at top left,#00ffd511,transparent 25%), radial-gradient(circle at top right,#00a2ff11,transparent 25%), linear-gradient(135deg,#050816,#09111f,#10192d); color:var(--text); overflow-x:hidden; } 
.hero{ padding:70px 20px; text-align:center; } 
.hero h1{ font-size:55px; margin:0; color:var(--accent); text-shadow:0 0 25px #00ffd566; } 
.hero p{ max-width:950px; margin:auto; margin-top:20px; line-height:1.9; font-size:18px; color:var(--muted); } 
.main{ display:flex; gap:20px; padding:20px; } 
.sidebar{ width:340px; min-width:340px; background:rgba(16,25,45,0.95); border:1px solid var(--border); border-radius:22px; padding:24px; height:fit-content; backdrop-filter:blur(10px); } 
.content{ flex:1; } 
.card{ background:rgba(16,25,45,0.96); border:1px solid var(--border); border-radius:22px; padding:25px; margin-bottom:22px; box-shadow:0 0 25px rgba(0,0,0,0.35); animation:fadeUp .5s ease; } 
.card h2,.card h3{ margin-top:0; color:var(--accent); } 
.small{ font-size:15px; line-height:1.9; color:var(--muted); } 
input, select, textarea { width:100%; padding:14px; margin-top:8px; margin-bottom:18px; background:#08101f; border:1px solid #314d79; border-radius:12px; color:white; font-size:15px; box-sizing: border-box; } 
button{ width:100%; padding:14px; border:none; border-radius:12px; font-weight:bold; background:linear-gradient(135deg,var(--accent),var(--accent2)); cursor:pointer; font-size:15px; color: black; } 
button:hover{ opacity:.9; } 
.grid{ display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:18px; } 
.badge{ display:inline-block; padding:7px 15px; border-radius:999px; background:var(--accent); color:black; font-weight:bold; margin:5px; } 
.success{ background:#0d3520; padding:18px; border-left:5px solid #00ff88; border-radius:12px; line-height:1.8; } 
.warning{ background:#3d2407; padding:18px; border-left:5px solid orange; border-radius:12px; line-height:1.8; margin-bottom: 15px; } 
.loshu{ margin:auto; border-collapse:separate; border-spacing:12px; } 
.loshu td{ width:95px; height:95px; text-align:center; vertical-align:middle; background:#0b1325; border:2px solid #31486f; border-radius:18px; font-size:28px; font-weight:bold; color:var(--accent); } 
.empty{ color:#445 !important; } 
.meter{ height:16px; background:#1f2f4a; border-radius:999px; overflow:hidden; margin-top:12px; } 
.fill{ height:100%; background:linear-gradient(90deg,#00ffd5,#00a2ff); } 
.zoom-controls{ position:fixed; right:18px; bottom:18px; display:flex; flex-direction:column; gap:8px; z-index:999; } 
.zoom-btn{ width:55px; height:55px; border-radius:50%; font-size:18px; background:var(--card); border:1px solid var(--border); color:var(--accent); cursor:pointer;} 
.footer{ text-align:center; padding:35px; color:#7b8699; } 
ul li{ margin-bottom:10px; line-height:1.8; } 
@keyframes fadeUp{ from{ opacity:0; transform:translateY(15px); } to{ opacity:1; transform:translateY(0); } } 
@media(max-width:900px){ .main{ flex-direction:column; } .sidebar{ width:100%; min-width:100%; } .hero h1{ font-size:36px; } .loshu td{ width:72px; height:72px; font-size:20px; } }
"""

# =========================================================
# ENGINE CODE (UNTOUCHED)
# =========================================================
class NumerologyEngine:
    LOSHU_LAYOUT = [ [4,9,2], [3,5,7], [8,1,6] ]
    
    def __init__(self, name, dob, mobile=""):
        self.name = name.strip()
        self.dob = dob.strip()
        self.mobile = mobile.strip()
        self.driver = 0
        self.conductor = 0
        self.name_total = 0
        self.name_single = 0
        self.grid_numbers = []
        self.freq = {i:0 for i in range(1,10)}
        self.grid_map = {i:[] for i in range(1,10)}
        self.parsed_date = None

    def reduce(self, n, master=True):
        if master and n in MASTER_NUMBERS:
            return n
        while n > 9:
            n = sum(int(x) for x in str(n))
        if master and n in MASTER_NUMBERS:
            return n
        return n

    def parse_date(self):
        s = self.dob.replace("/","-").replace(".","-")
        if re.match(r"^\d{2}-\d{2}-\d{4}$", s):
            self.parsed_date = datetime.strptime(s, "%d-%m-%Y").date()
        else:
            self.parsed_date = parser.parse(s, dayfirst=True).date()

    def calculate(self):
        self.parse_date()
        digits = [int(x) for x in self.parsed_date.strftime("%d%m%Y") if x != "0"]
        self.grid_numbers = digits
        self.driver = self.reduce(self.parsed_date.day)
        full = self.parsed_date.day + self.parsed_date.month + self.parsed_date.year
        self.conductor = self.reduce(full)
        
        for n in digits + [self.driver, self.conductor]:
            if 1 <= n <= 9:
                self.freq[n] += 1
                self.grid_map[n].append(str(n))
                
        total = 0
        for ch in self.name.upper():
            if ch.isalpha():
                total += CHALDEAN_MAP.get(ch, 0)
        self.name_total = total
        self.name_single = self.reduce(total)

    def loshu_html(self):
        html = "<table class='loshu'>"
        for row in self.LOSHU_LAYOUT:
            html += "<tr>"
            for n in row:
                vals = self.grid_map[n]
                if vals:
                    html += f"<td>{''.join(vals)}</td>"
                else:
                    html += "<td class='empty'>-</td>"
            html += "</tr>"
        html += "</table>"
        return html

    def compatibility_score(self):
        score = 0
        name_digit = self.reduce(self.name_single)
        d_rel = NUM_RELATIONS.get(self.driver, {})
        if name_digit in d_rel.get('friends', []):
            score += 45
        elif name_digit in d_rel.get('neutral', []):
            score += 25
        else:
            score += 8
            
        c_rel = NUM_RELATIONS.get(self.conductor, {})
        if name_digit in c_rel.get('friends', []):
            score += 45
        elif name_digit in c_rel.get('neutral', []):
            score += 25
        else:
            score += 8
            
        missing = [n for n in range(1,10) if self.freq[n] == 0]
        name_digits = [int(x) for x in str(self.name_total) if x.isdigit()]
        recovered = [x for x in missing if x in name_digits]
        score += min(10, len(recovered)*2)
        return min(100, score)

    def intelligent_name_analysis(self, lang='en'):
        score = self.compatibility_score()
        missing = [n for n in range(1,10) if self.freq[n] == 0]
        
        msg_perfect = {
            'en': f"✅ Congratulations!\n\nYour current name vibration is strongly aligned with your Driver Number ({self.driver}), Conductor Number ({self.conductor}), and native Lo Shu Grid frequencies.\n\nNo correction is required because your present name already carries a professionally balanced numerological frequency.",
            'hi': f"✅ बधाई हो!\n\nआपका वर्तमान नाम कंपन आपके ड्राइवर नंबर ({self.driver}), कंडक्टर नंबर ({self.conductor}), और मूल लो शू ग्रिड आवृत्तियों के साथ दृढ़ता से संरेखित है।\n\nकिसी सुधार की आवश्यकता नहीं है क्योंकि आपका वर्तमान नाम पहले से ही एक पेशेवर रूप से संतुलित संख्यात्मक आवृत्ति रखता है।",
            'as': f"✅ অভিনন্দন!\n\nআপোনাৰ বৰ্তমানৰ নামৰ কম্পন আপোনাৰ ড্ৰাইভাৰ নম্বৰ ({self.driver}), কণ্ডাক্টৰ নম্বৰ ({self.conductor}), আৰু থলুৱা লো শ্বু গ্ৰীড ফ্ৰিকুৱেন্সীৰ সৈতে দৃঢ়ভাৱে সংৰেখিত হৈছে।\n\nকোনো সংশোধনৰ প্ৰয়োজন নাই কাৰণ আপোনাৰ বৰ্তমানৰ নামত ইতিমধ্যে এটা পেচাদাৰীভাৱে সন্তুলিত সংখ্যাতাত্ত্বিক কম্পন আছে।"
        }
        
        msg_warning = {
            'en': "⚠️ Name Vibration Improvement Recommended\n\nYour current name is functional, but it does not fully synchronize with your complete Lo Shu Grid structure and destiny frequencies. A professionally optimized spelling can significantly improve energetic balance.",
            'hi': "⚠️ नाम कंपन सुधार की सिफारिश की जाती है\n\nआपका वर्तमान नाम काम तो कर रहा है, लेकिन यह आपकी पूरी लो शू ग्रिड संरचना और भाग्य आवृत्तियों के साथ पूरी तरह से सिंक्रनाइज़ नहीं है। एक पेशेवर रूप से अनुकूलित वर्तनी ऊर्जावान संतुलन में महत्वपूर्ण सुधार कर सकती है।",
            'as': "⚠️ নামৰ কম্পন উন্নত কৰাৰ পৰামৰ্শ দিয়া হৈছে\n\nআপোনাৰ বৰ্তমানৰ নামটো কাৰ্য্যক্ষম, কিন্তু ই আপোনাৰ সম্পূৰ্ণ লো শ্বু গ্ৰীড গঠন আৰু ভাগ্যৰ কম্পনৰ সৈতে সম্পূৰ্ণৰূপে সৰ্বসমিল নহয়। এটা পেচাদাৰীভাৱে অপ্টিমাইজ কৰা বানান বাছনি কৰিলে শক্তিৰ ভাৰসাম্য লক্ষণীয়ভাৱে উন্নত হ’ব পাৰে।"
        }
        
        reason_text = {
            'en': f"This spelling introduces stronger energetic synchronization with Driver Number {self.driver} and Destiny Number {self.conductor}.",
            'hi': f"यह वर्तनी ड्राइवर नंबर {self.driver} और भाग्य नंबर {self.conductor} के साथ मजबूत ऊर्जावान सिंक्रनाइज़ेशन पेश करती है।",
            'as': f"এই বানানে ড্ৰাইভাৰ নম্বৰ {self.driver} আৰু ভাগ্য নম্বৰ {self.conductor} ৰ সৈতে অধিক শক্তিশালী শক্তিৰ সমিলমিল ঘটায়।"
        }
        
        if score >= 85:
            return { "perfect":True, "score":score, "message": msg_perfect[lang], "suggestions":[] }
            
        suggestions = []
        test_names = [
            self.name + "h", self.name + " Raj", self.name + " Dev", self.name + " Anand",
            self.name + " Kumar", "Aar" + self.name, self.name + " Sharma", self.name + " Sai"
        ]
        used = set()
        for nm in test_names:
            total = 0
            for ch in nm.upper():
                if ch.isalpha():
                    total += CHALDEAN_MAP.get(ch,0)
            single = self.reduce(total)
            if single in NUM_RELATIONS[self.driver]['friends']:
                if nm not in used:
                    used.add(nm)
                    sc = random.randint(84,96)
                    suggestions.append({
                        "name":nm, "number":single, "score":sc, "reason": reason_text[lang]
                    })
        return { "perfect":False, "score":score, "message": msg_warning[lang], "suggestions":suggestions[:3] }

# =========================================================
# GLOBAL TEMPLATE FRAMEWORK
# =========================================================
PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Numero Annand AI</title>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <style>""" + STYLE + """</style>
</head>
<body>
    <div class='hero'>
        <h1>🔮 Numero Annand AI</h1>
        <p>Advanced Premium Lo Shu Grid Numerology Platform powered by deep energetic analysis, professional numerology intelligence, personality interpretation systems, career guidance algorithms, karmic vibration decoding and futuristic spiritual analytics.</p>
    </div>
    
    <div class='main'>
        <div class='sidebar'>
            <form action='/checkout' method='POST'>
                <h3>{{ t.workspace_menu }}</h3>
                
                <label>{{ t.name_label }}</label>
                <input type='text' name='name' value='{{ name }}' required>
                
                <label>{{ t.dob_label }}</label>
                <input type='text' name='dob' placeholder='DD-MM-YYYY' value='{{ dob }}' required>
                
                <label>{{ t.mobile_label }}</label>
                <input type='text' name='mobile' value='{{ mobile }}'>
                
                <label>{{ t.lang_label }}</label>
                <select name='lang' id='lang_select' onchange="location.href='/?lang='+this.value;">
                    <option value='en' {% if lang == 'en' %}selected{% endif %}>English</option>
                    <option value='hi' {% if lang == 'hi' %}selected{% endif %}>हिंदी (Hindi)</option>
                    <option value='as' {% if lang == 'as' %}selected{% endif %}>অসমীয়া (Assamese)</option>
                </select>
                
                <button type='submit'>{{ t.btn_analyze }}</button>
            </form>
            
            <br>
            <div class='card' style='margin-bottom:12px; padding:15px;'>
                <h3>📞 {{ t.consult_folder }}</h3>
                <p class='small'><b>{{ t.strategist }}</b> Annand Sarma</p>
                <p class='small'><b>{{ t.contact }}</b> <a href='{{ consult_link }}' target='_blank' style='color:var(--accent); text-decoration:none;'>{{ t.chat_wa }}</a></p>
                <hr style='border-color:var(--border);'>
                <p class='small'><b>{{ t.premium_services }}</b></p>
                <ul class='small' style='padding-left:15px;'>
                    <li>Name Correction: ₹500</li>
                    <li>Advance Lo Shu Grid Chart: ₹1000</li>
                    <li>Career Guidance: ₹200</li>
                    <li>Relationship: ₹200</li>
                </ul>
                <a href='{{ consult_link }}' target='_blank'><button type='button' style='background:linear-gradient(135deg,#00ffd5,#00a2ff); color:black;'>{{ t.btn_consult }}</button></a>
            </div>
            
            <div class='card' style='padding:15px;'>
                <h3>👥 {{ t.wa_group_folder }}</h3>
                <a href='{{ group }}' target='_blank'><button type='button' style='background:linear-gradient(135deg,#25D366,#128C7E); color:white;'>{{ t.btn_open_wa }}</button></a>
            </div>
        </div>
        
        <div class='content'>
            {{ content|safe }}
        </div>
    </div>
    
    <div class='zoom-controls'>
        <button class='zoom-btn' onclick='zoomIn()'>+</button>
        <button class='zoom-btn' onclick='zoomOut()'>−</button>
        <button class='zoom-btn' onclick='resetZoom()'>⟳</button>
    </div>
    
    <div class='footer'>
        Numero Annand AI • Premium Numerology Platform
    </div>

    <script>
        let currentZoom = 1;
        function setZoom(z){
            currentZoom = Math.max(0.7, Math.min(1.5, z));
            document.body.style.transform = 'scale('+currentZoom+')';
            document.body.style.transformOrigin = 'top center';
        }
        function zoomIn(){ setZoom(currentZoom + 0.1); }
        function zoomOut(){ setZoom(currentZoom - 0.1); }
        function resetZoom(){ setZoom(1); }
    </script>
</body>
</html>
"""

# =========================================================
# HOME
# =========================================================
@app.route('/')
def index():
    lang = request.args.get('lang', 'en')
    t = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    
    home = f"""
    <div class='card'>
        <h2>✨ Welcome To Numero Annand AI</h2>
        <div class='grid'>
            <div style='background:#0b1325; padding:15px; border-radius:12px; border:1px solid var(--border);'>
                <h3>🔢 Lo Shu Grid Intelligence</h3>
                <p class='small'>Ancient Lo Shu Grid system enhanced with advanced AI-powered energetic interpretation and deep psychological decoding.</p>
            </div>
            <div style='background:#0b1325; padding:15px; border-radius:12px; border:1px solid var(--border);'>
                <h3>🧠 Personality Blueprint</h3>
                <p class='small'>Discover hidden behavioral patterns, karmic strengths, emotional tendencies and subconscious personality architecture.</p>
            </div>
            <div style='background:#0b1325; padding:15px; border-radius:12px; border:1px solid var(--border);'>
                <h3>💼 Career & Wealth Guidance</h3>
                <p class='small'>Understand financial vibrations, business success indicators, leadership patterns and prosperity alignment.</p>
            </div>
            <div style='background:#0b1325; padding:15px; border-radius:12px; border:1px solid var(--border);'>
                <h3>❤️ Relationship Compatibility</h3>
                <p class='small'>Analyze emotional resonance, communication harmony, marriage compatibility and relationship energy flow.</p>
            </div>
        </div>
    </div>
    """
    return render_template_string(PAGE, content=home, name='', dob='', mobile='', lang=lang, t=t, consult_link=WHATSAPP_CONSULT_LINK, group=WHATSAPP_GROUP_LINK)

# =========================================================
# GATEWAY CHECKOUT ROUTE
# =========================================================
@app.route('/checkout', methods=['POST'])
def checkout():
    name = request.form.get('name', '')
    dob = request.form.get('dob', '')
    mobile = request.form.get('mobile', '')
    lang = request.form.get('lang', 'en')
    t = TRANSLATIONS.get(lang, TRANSLATIONS['en'])

    checkout_html = f"""
    <div class='card' style='text-align: center;'>
        <h2>📥 Order Gateway — { t['premium_box_title'] }</h2>
        <p class='small'>{ t['premium_box_desc'] }</p>
        
        <form action='/verify-payment' method='POST'>
            <input type='hidden' name='name' value='{name}'>
            <input type='hidden' name='dob' value='{dob}'>
            <input type='hidden' name='mobile' value='{mobile}'>
            <input type='hidden' name='lang' value='{lang}'>

            <div style='margin: 20px 0; text-align: left; background: #0b1325; padding: 20px; border-radius: 12px; border: 1px solid var(--border);'>
                <h4 style='margin-top:0; color: var(--accent);'>Step 1: Choose Your Premium Delivery Format</h4>
                <label style='display:block; margin-bottom: 12px; cursor:pointer;'>
                    <input type='radio' name='order_type' value='pdf' checked style='width:auto; margin:0 10px 0 0;'> <b>Download Full Digital PDF Version (Instant AI) — ₹201</b>
                </label>
                <label style='display:block; cursor:pointer;'>
                    <input type='radio' name='order_type' value='offline' style='width:auto; margin:0 10px 0 0;'> <b>Premium Printed Home Delivery Version — ₹501</b>
                </label>
            </div>

            <div style='margin: 20px 0;'>
                <p class='small'><b>{ t['scan_pay'] }</b></p>
                <div style='margin: 15px auto; width:220px; background:white; padding:10px; border-radius:12px; border:3px solid #243b60;'>
                    <img src='https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=upi://pay?pa=7099805039@ybl%26pn=Ananda%20Sarmah' style='width:100%; display:block;'>
                </div>
            </div>

            <div style='text-align: left; background: #131f37; padding: 20px; border-radius: 12px; border: 1px solid #ffaa0033;'>
                <h4 style='margin-top:0; color: #ffaa00;'>Step 2: Anti-Fraud Payment Proof Verification</h4>
                <p class='small' style='color: #9ba7ba; margin-bottom:10px;'>Please complete your UPI transaction via PhonePe/GPay/Paytm, copy the <b>12-Digit UTR/Transaction ID</b> from your bank receipt, and enter it below to securely unlock your system profile tracking loop.</p>
                
                <label><b>Enter 12-Digit Transaction UTR Code Number:</b></label>
                <input type='text' name='utr_number' placeholder='e.g., 618274930124' minlength='12' maxlength='16' required style='border:1px solid #ffaa00; background:#08101f;'>
            </div>

            <button type='submit' style='background:linear-gradient(135deg, #00ff88, #00a2ff); margin-top:20px; color:black;'>Verify Transaction & Proceed</button>
        </form>
    </div>
    """
    return render_template_string(PAGE, content=checkout_html, name=name, dob=dob, mobile=mobile, lang=lang, t=t, consult_link=WHATSAPP_CONSULT_LINK, group=WHATSAPP_GROUP_LINK)

# =========================================================
# PAYMENT VERIFICATION ROUTE (ANTI-FRAUD SYSTEM)
# =========================================================
@app.route('/verify-payment', methods=['POST'])
def verify_payment():
    name = request.form.get('name', '')
    dob = request.form.get('dob', '')
    mobile = request.form.get('mobile', '')
    lang = request.form.get('lang', 'en')
    order_type = request.form.get('order_type', 'pdf')
    utr_number = request.form.get('utr_number', '').strip()
    t = TRANSLATIONS.get(lang, TRANSLATIONS['en'])

    if not utr_number or len(utr_number) < 12:
        error_html = "<div class='card'><div class='warning'>❌ Invalid Transaction ID. Please recheck your banking app receipt entry.</div><a href='/'><button>Back to Home</button></a></div>"
        return render_template_string(PAGE, content=error_html, name=name, dob=dob, mobile=mobile, lang=lang, t=t, consult_link=WHATSAPP_CONSULT_LINK, group=WHATSAPP_GROUP_LINK)

    # Database Security Guard against duplicate UTR submission fraud
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()
    try:
        if order_type == 'offline':
            # Lock out process until tracking address details are obtained securely
            conn.close()
            address_form_html = f"""
            <div class='card'>
                <h2>📦 Payment Provisionally Accepted — Delivery Address Required</h2>
                <p class='small' style='color:#00ff88;'>UTR Reference Check {utr_number} submitted successfully. Because you requested Premium Printed Home Delivery, please fill out your physical delivery destination details below.</p>
                
                <form action='/confirm-offline-order' method='POST'>
                    <input type='hidden' name='name' value='{name}'>
                    <input type='hidden' name='dob' value='{dob}'>
                    <input type='hidden' name='mobile' value='{mobile}'>
                    <input type='hidden' name='lang' value='{lang}'>
                    <input type='hidden' name='utr_number' value='{utr_number}'>
                    <input type='hidden' name='order_type' value='{order_type}'>

                    <label><b>Recipient Phone Number for Shipping Updates:</b></label>
                    <input type='text' name='shipping_phone' value='{mobile}' required>

                    <label><b>Full Home / Shipping Delivery Address (With Landmark & Pincode):</b></label>
                    <textarea name='shipping_address' rows='4' placeholder='Enter complete house door number, street, landmark, city, state, and pin code clearly' required style='width:100; font-family:inherit;'></textarea>
                    
                    <button type='submit' style='background:linear-gradient(135deg,#00ffd5,#00a2ff); color:black; margin-top:15px;'>Submit Address & Generate Final AI Master Blueprint</button>
                </form>
            </div>
            """
            return render_template_string(PAGE, content=address_form_html, name=name, dob=dob, mobile=mobile, lang=lang, t=t, consult_link=WHATSAPP_CONSULT_LINK, group=WHATSAPP_GROUP_LINK)
        
        else:
            # Digital Entry Processing
            cursor.execute("INSERT INTO orders (utr_number, name, dob, mobile, lang, order_type, address) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                           (utr_number, name, dob, mobile, lang, order_type, "Digital Download"))
            conn.commit()
            conn.close()
            return generate_final_report(name, dob, mobile, lang, order_type, utr_number)

    except sqlite3.IntegrityError:
        conn.close()
        fraud_html = """
        <div class='card'>
            <div class='warning'>
                <h3>⚠️ Transaction Registry Verification Security Alert</h3>
                <p class='small'>This Transaction UTR Reference Code has already been parsed inside our system database. Multiple duplicate submissions using the identical verification code are automatically flagged to block fraud loops.</p>
            </div>
            <p class='small'>If you believe this is a technical system anomaly, please drop a structural transaction error check log directly to our management line.</p>
            <a href='/'><button style='margin-top:15px;'>Return to Workspace System</button></a>
        </div>
        """
        return render_template_string(PAGE, content=fraud_html, name=name, dob=dob, mobile=mobile, lang=lang, t=t, consult_link=WHATSAPP_CONSULT_LINK, group=WHATSAPP_GROUP_LINK)

# =========================================================
# OFFLINE ADDRESS PROCESSING ROUTE
# =========================================================
@app.route('/confirm-offline-order', methods=['POST'])
def confirm_offline_order():
    name = request.form.get('name', '')
    dob = request.form.get('dob', '')
    mobile = request.form.get('mobile', '')
    lang = request.form.get('lang', 'en')
    utr_number = request.form.get('utr_number', '')
    order_type = request.form.get('order_type', 'offline')
    shipping_phone = request.form.get('shipping_phone', '')
    shipping_address = request.form.get('shipping_address', '')
    t = TRANSLATIONS.get(lang, TRANSLATIONS['en'])

    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()
    try:
        full_shipping_log = f"Phone: {shipping_phone} | Address: {shipping_address}"
        cursor.execute("INSERT INTO orders (utr_number, name, dob, mobile, lang, order_type, address) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                       (utr_number, name, dob, mobile, lang, order_type, full_shipping_log))
        conn.commit()
        conn.close()
        return generate_final_report(name, dob, mobile, lang, order_type, utr_number, shipping_address)
    except sqlite3.IntegrityError:
        conn.close()
        return redirect(url_for('index'))

# =========================================================
# CENTRAL AI GENERATION MODULE ENGINE RENDER
# =========================================================
def generate_final_report(name, dob, mobile, lang, order_type, utr_number, address_log=None):
    t = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    engine = NumerologyEngine(name, dob, mobile)
    engine.calculate()
    check = engine.intelligent_name_analysis(lang=lang)
    score = engine.compatibility_score()
    missing = [n for n in range(1,10) if engine.freq[n] == 0]
    repeated = [n for n,c in engine.freq.items() if c >= 2]
    
    delivery_receipt_box = ""
    if order_type == 'offline':
        delivery_receipt_box = f"""
        <div class='card success' style='margin-bottom: 22px; background: #0c2540; border-left: 5px solid var(--accent2);'>
            <h3 style='color: var(--accent); margin-top: 0;'>📦 Premium Print Order Processed Successfully!</h3>
            <p class='small' style='color:#f3f3f3;'>Your verified payment UTR <b>{utr_number}</b> has logged structural confirmation status. The master copy will be dispatched to your destination details below:</p>
            <p class='small' style='color:var(--muted); margin-bottom: 0;'><b>Shipping Logistics Destination:</b> {address_log}</p>
        </div>
        """
    else:
        delivery_receipt_box = f"""
        <div class='card success' style='margin-bottom: 22px;'>
            <h3 style='margin-top: 0;'>⚡ Transaction Confirmed Securely!</h3>
            <p class='small' style='color:#f3f3f3; margin-bottom: 0;'>Digital Profile Access tracking matching UTR Reference <b>{utr_number}</b> has logged authorization profile status. You can now save or print your complete analysis below.</p>
        </div>
        """

    result = delivery_receipt_box + f"""
    <div class='card'>
        <h2>{ t['p1_title'] }</h2>
        <p><b>Full Name:</b> {name}</p>
        <p><b>Date Of Birth:</b> {engine.parsed_date.strftime('%d-%m-%Y')}</p>
        <p><b>Driver Number:</b> {engine.driver}</p>
        <p><b>Conductor Number:</b> {engine.conductor}</p>
        <p><b>Name Number:</b> {engine.name_single}</p>
        <p><b>Compound Name Value:</b> {engine.name_total}</p>
        
        <h3>⚡ Energy Balance Score</h3>
        <p class='small'>Your energetic compatibility score is calculated through synchronization between Driver Number, Destiny vibration, Lo Shu Grid structure, missing number recovery potential, and Chaldean name resonance patterns.</p>
        <div class='meter'><div class='fill' style='width: {score}%'></div></div>
        <p class='small'><b>Current Name Compatibility:</b> {score}%</p>
    </div>

    <div class='card'>
        <h2>{ t['p2_title'] }</h2>
        {engine.loshu_html()}
        <br>
        <h3>{ t['missing_title'] }</h3>
        <p class='small'>{missing if missing else 'None'}</p>
        <p class='small'>{ t['missing_desc'] }</p>
        
        <h3>{ t['repeated_title'] }</h3>
        <p class='small'>{repeated if repeated else 'None'}</p>
        <p class='small'>{ t['repeated_desc'] }</p>
    </div>

    <div class='card'>
        <h2>{ t['p3_title'] }</h2>
        <h3>{ t['mental_title'] }</h3>
        <p class='small'>{ t['mental_desc'] }</p>
        <h3>{ t['emotional_title'] }</h3>
        <p class='small'>{ t['emotional_desc'] }</p>
        <h3>{ t['practical_title'] }</h3>
        <p class='small'>{ t['practical_desc'] }</p>
        <h3>{ t['arrow_title'] }</h3>
        <p class='small'>{ t['arrow_desc'] }</p>
        <h3>{ t['raj_title'] }</h3>
        <p class='small'>{ t['raj_desc'] }</p>
        <h3>{ t['psych_title'] }</h3>
        <p class='small'>{ t['psych_desc'] }</p>
        <h3>{ t['spiritual_title'] }</h3>
        <p class='small'>{ t['spiritual_desc'] }</p>
    </div>

    <div class='card'>
        <h2>{ t['p4_title'] }</h2>
        <div class='{"success" if check["perfect"] else "warning"}'>
            <p style='white-space: pre-line;'>{check['message']}</p>
        </div>
    """
    
    if check['suggestions']:
        result += f"<br><h3>✨ Professionally Suggested Corrected Names</h3><div class='grid'>"
        for s in check['suggestions']:
            result += f"""
            <div style='background:#0b1325; padding:15px; border-radius:12px; border:1px solid var(--border);'>
                <h4 style='margin:0 0 10px 0; color:var(--accent);'>{s['name']}</h4>
                <p class='small' style='margin:5px 0;'><b>Improved Compatibility:</b> {s['score']}%</p>
                <p class='small' style='margin:5px 0;'><b>New Vibration Number:</b> {s['number']}</p>
                <p class='small' style='margin:5px 0; font-size:13px; color:var(--muted);'>{s['reason']}</p>
            </div>
            """
        result += "</div>"
        
    result += f"""
        <br>
        <h3>{ t['career_title'] }</h3>
        <p class='small'>{ t['career_desc'] }</p>
        <h3>{ t['rel_title'] }</h3>
        <p class='small'>{ t['rel_desc'] }</p>
        <h3>{ t['fin_title'] }</h3>
        <p class='small'>{ t['fin_desc'] }</p>
        <h3>{ t['lucky_title'] }</h3>
        <p class='small'><b>Lucky Numbers:</b> {engine.driver}, {engine.conductor}, {engine.name_single}</p>
        <p class='small'><b>Lucky Days:</b> Sunday, Wednesday, Friday</p>
        <p class='small'><b>Lucky Colors:</b> Aqua Blue, White, Emerald Green</p>
    </div>

    <div class='card'>
        <h2>{ t['p5_title'] }</h2>
        <h3>{ t['deep_title'] }</h3>
        <p class='small'>{ t['deep_desc'] }</p>
        <h3>{ t['forecast_title'] }</h3>
        <p class='small'>{ t['forecast_desc'] }</p>
        <h3>{ t['roadmap_title'] }</h3>
        <p class='small'>{ t['roadmap_desc'] }</p>
        <h3>{ t['remedies_title'] }</h3>
        <ul class='small'>
            <li>Practice daily meditation for 11 minutes.</li>
            <li>Maintain structured sleep and work routine.</li>
            <li>Use positive affirmations consistently.</li>
        </ul>
        <h3>{ t['success_title'] }</h3>
        <p class='small'>{ t['success_desc'] }</p>
    </div>

    <div class='card'>
        <h2>{ t['freq_title'] }</h2>
    """
    for n, c in engine.freq.items():
        if c == 0:
            result += f"<p class='small'>❌ Number {n} is missing from the Lo Shu Grid.</p>"
        elif c == 1:
            result += f"<p class='small'>⚖️ Number {n} appears once.</p>"
        elif c == 2:
            result += f"<p class='small'>✅ Number {n} appears twice.</p>"
        else:
            result += f"<p class='small'>🔥 Number {n} appears {c} times.</p>"
    result += "</div>"
    
    return render_template_string(PAGE, content=result, name=name, dob=dob, mobile=mobile, lang=lang, t=t, consult_link=WHATSAPP_CONSULT_LINK, group=WHATSAPP_GROUP_LINK)

# =========================================================
# RUN SYSTEM
# =========================================================
if __name__ == "__main__":
    app.run(debug=True, port=8501)
