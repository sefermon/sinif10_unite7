import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
# 1. Sayfa Yapılandırması
st.set_page_config(page_title="Dinamik Test Platformu", layout="wide")

# 2. Veri Yapısı (Data Structure)
# İleride tüm yeni testleri buraya bir JSON dosyası gibi ekleyeceğiz. Şimdilik iki örnek var.
QUIZ_DATA = {
    "10. Sınıf İngilizce - Ünite 7 (Food and Festivals)": [
        {
            "question": "1. In Turkey, traditional desserts like baklava ________ during religious festivals.",
            "topic": "Passive Voice - Present (Geniş Zaman Edilgen Çatı)",
            "lesson": "Eylemi yapanın değil, eylemden etkilenen nesnenin odak noktasında olduğu durumlarda edilgen yapı (Passive Voice) kullanılır. Geniş zaman için 'am/is/are + Verb 3 (Fiilin 3. hali)' kuralı geçerlidir.",
            "studyAdvice": "Geniş zamanda edilgen yapı kurallarına ve düzenli/düzensiz fiillerin 3. hallerine (Past Participle) çalış.",
            "options": ["are serving", "are served", "serve", "served"],
            "correct_index": 1,
            "feedbacks": [
                "Yanlış. 'Are serving' şimdiki zaman etken (Active) yapıdır. Tatlılar kendi kendine servis yapamaz.",
                "Doğru! Nesne çoğul (desserts) olduğu için 'are' yardımcı fiili ve 'serve' fiilinin 3. hali (served) kullanılmıştır.",
                "Yanlış. 'Serve' geniş zaman etken yapıdır.",
                "Yanlış. 'Served' geçmiş zaman etken yapıdır."
            ]
        },
        {
            "question": "2. During the ________ of the new year, people usually watch the fireworks display at midnight.",
            "topic": "Vocabulary - Festivals (Kelime Bilgisi - Festivaller)",
            "lesson": "Yeni yıl, ulusal bayram veya özel günlerin 'kutlaması' anlamına gelen isim (noun) formundaki kelime 'celebration'dır.",
            "studyAdvice": "7. Ünitenin (Food and Festivals) odak kelimelerinden olan kutlama, tören ve gelenek bildiren isimlere odaklan.",
            "options": ["celebration", "preparation", "destination", "reservation"],
            "correct_index": 0,
            "feedbacks": [
                "Doğru! 'Celebration' kutlama demektir.",
                "Yanlış. 'Preparation' hazırlık demektir. Yeni yılın hazırlığı sırasında gece yarısı havai fişek izlenmez, kutlaması sırasında izlenir.",
                "Yanlış. 'Destination' varış noktası demektir.",
                "Yanlış. 'Reservation' rezervasyon demektir."
            ]
        },
        {
            "question": "3. The first Thanksgiving feast ________ by the Pilgrims and the Wampanoag people in 1621.",
            "topic": "Passive Voice - Past (Geçmiş Zaman Edilgen Çatı)",
            "lesson": "Geçmişte tamamlanmış ve nesnesi (feast - ziyafet) vurgulanan eylemler için 'was/were + Verb 3' yapısı kullanılır. Cümlede 'in 1621' ifadesi olayın geçmişte yaşandığını kanıtlar.",
            "studyAdvice": "Geçmiş zaman (Simple Past) ile edilgen (Passive) yapının nasıl birleştiğini (was/were + V3) tekrar et.",
            "options": ["was sharing", "shared", "is shared", "was shared"],
            "correct_index": 3,
            "feedbacks": [
                "Yanlış. 'Was sharing' geçmişte devam eden etken yapıdır (paylaşıyordu).",
                "Yanlış. 'Shared' geçmiş zaman etken yapıdır. Ziyafet (feast) kendi kendini paylaşamaz.",
                "Yanlış. 'Is shared' geniş zaman edilgen yapıdır ancak olay 1621'de gerçekleşmiştir.",
                "Doğru! Ziyafet tekil olduğu için 'was' ve fiilin 3. hali 'shared' kullanılmıştır. (Paylaşıldı)."
            ]
        },
        {
            "question": "4. To make a good omelette, you should first ________ the eggs in a bowl before pouring them into the pan.",
            "topic": "Vocabulary - Cooking Methods (Yemek Pişirme Yöntemleri)",
            "lesson": "Yumurta veya krema gibi sıvı malzemeleri hızlıca çırpmak için 'whisk' fiili kullanılır. Tariflerin (recipes) temel eylemlerinden biridir.",
            "studyAdvice": "Yemek tarifleri bağlamında kullanılan hazırlama (chop, peel, whisk) ve pişirme (boil, fry, bake) fiillerine çalış.",
            "options": ["roast", "whisk", "bake", "slice"],
            "correct_index": 1,
            "feedbacks": [
                "Yanlış. 'Roast' fırında veya ateşte et/sebze kızartmak demektir.",
                "Doğru! 'Whisk' çırpmak anlamına gelir. Omlet yaparken yumurtalar çırpılır.",
                "Yanlış. 'Bake' hamur işlerini fırında pişirmek demektir.",
                "Yanlış. 'Slice' dilimlemek demektir. Çiğ yumurta dilimlenemez."
            ]
        },
        {
            "question": "5. ________, boil some water in a pot. Then, add the pasta and salt. Finally, drain the water.",
            "topic": "Sequencers (Sıralama Zarfları)",
            "lesson": "Bir sürecin, talimatın veya tarifin ilk adımını belirtirken her zaman 'First' (İlk olarak) bağlacı kullanılır. Devamında süreci ilerletmek için 'Then, Next, After that' ve işlemi bitirmek için 'Finally' gelir.",
            "studyAdvice": "Bir olayı kronolojik (zaman sırasına göre) anlatmaya yarayan sıralayıcılara (First, Then, Next, Finally) çalış.",
            "options": ["Next", "First", "After that", "Usually"],
            "correct_index": 1,
            "feedbacks": [
                "Yanlış. 'Next' (Sonra), ilk adımdan sonraki aşamalar için kullanılır.",
                "Doğru! Bir sürecin ilk adımı anlatılırken 'First' kullanılır.",
                "Yanlış. 'After that' (Ondan sonra), süreç başladıktan sonraki adımları ifade eder.",
                "Yanlış. 'Usually' (Genellikle) bir sıklık zarfıdır, sıralama bildirmez."
            ]
        },
        {
            "question": "6. If you want to make traditional French fries, you must ________ the sliced potatoes in hot oil.",
            "topic": "Vocabulary - Cooking Methods (Pişirme Yöntemleri)",
            "lesson": "Sıcak yağda kızartma işlemi için 'fry' fiili kullanılır. Suda kaynatmak (boil), fırında pişirmek (bake) veya buharda pişirmek (steam) farklı termal işlemlerdir.",
            "studyAdvice": "Isı uygulama yöntemlerine göre değişen pişirme fiillerini (fry, boil, bake, roast, grill) sınıflandırarak çalış.",
            "options": ["boil", "bake", "fry", "steam"],
            "correct_index": 2,
            "feedbacks": [
                "Yanlış. 'Boil' kaynatmak demektir. Patates kızartması (French fries) suda kaynatılmaz.",
                "Yanlış. 'Bake' fırında pişirmek demektir.",
                "Doğru! 'Fry' kızartmak anlamına gelir. Yağda (in hot oil) yapılan işlem budur.",
                "Yanlış. 'Steam' buharda pişirmek demektir."
            ]
        },
        {
            "question": "7. The local people organized a magnificent ________ in the city center to celebrate their Independence Day.",
            "topic": "Vocabulary - Festivals (Festivaller)",
            "lesson": "Özel günleri veya bayramları kutlamak amacıyla sokaklarda yapılan resmi ve gösterişli yürüyüşlere 'parade' (geçit töreni) denir.",
            "studyAdvice": "Kutlama etkinliklerini tanımlayan isim türündeki kelimelere (parade, feast, custom, tradition) çalış.",
            "options": ["parade", "recipe", "ingredient", "cuisine"],
            "correct_index": 0,
            "feedbacks": [
                "Doğru! 'Parade' geçit töreni demektir ve şehir merkezindeki kutlamalar için doğru ifadedir.",
                "Yanlış. 'Recipe' yemek tarifi demektir.",
                "Yanlış. 'Ingredient' içindekiler/malzeme demektir.",
                "Yanlış. 'Cuisine' mutfak (kültürü) demektir."
            ]
        },
        {
            "question": "8. (Okuma Parçası) 'La Tomatina is a famous festival held in Spain. Every year on the last Wednesday of August, thousands of people gather in the town of Buñol to throw overripe tomatoes at each other purely for entertainment.' \n\nAccording to the text, what is the main purpose of the La Tomatina festival?",
            "topic": "Reading Comprehension - Scanning (Taramalı Okuma)",
            "lesson": "Okuma parçalarında spesifik bir bilgi (main purpose - ana amaç) sorulduğunda, metindeki anahtar kelimeler (purely for entertainment - tamamen eğlence için) taranarak (scanning) bulunur.",
            "studyAdvice": "Paragraf sorularında önce soru kökünü oku, ardından metin içinde o kelimelerin eş anlamlılarını veya tam karşılıklarını ara.",
            "options": ["To protest against the government", "To cook a massive amount of tomato soup", "For entertainment and fun", "To sell overripe tomatoes"],
            "correct_index": 2,
            "feedbacks": [
                "Yanlış. Metinde hükümeti protesto etmekten bahsedilmemektedir.",
                "Yanlış. Metinde domates çorbası (tomato soup) pişirmekten bahsedilmemektedir.",
                "Doğru! Metindeki 'purely for entertainment' (tamamen eğlence için) ifadesi, festivalin amacını doğrudan belirtmektedir.",
                "Yanlış. Domatesleri satmak (sell) değil, birbirlerine fırlatmak (throw) eylemi vurgulanmıştır."
            ]
        },
        {
            "question": "9. Flour, sugar, and eggs are the basic ________ you need to prepare this traditional dessert.",
            "topic": "Vocabulary - Cooking (Malzemeler)",
            "lesson": "Bir yemeği veya tatlıyı hazırlamak için gereken maddelerin her birine 'ingredient' (malzeme/içindekiler) denir.",
            "studyAdvice": "Yemek tarifi yapısını oluşturan ana bileşen kelimelerine (ingredients, directions, process) çalış.",
            "options": ["utensils", "ingredients", "celebrations", "destinations"],
            "correct_index": 1,
            "feedbacks": [
                "Yanlış. 'Utensils' mutfak aletleri (çatal, kaşık, tencere) demektir. Un ve şeker alet değildir.",
                "Doğru! 'Ingredients' malzemeler demektir. Un, şeker ve yumurta birer malzemedir.",
                "Yanlış. 'Celebrations' kutlamalar demektir.",
                "Yanlış. 'Destinations' varış noktaları demektir."
            ]
        },
        {
            "question": "10. (Okuma Parçası) 'Diwali, also known as the Festival of Lights, is one of the most popular Hindu festivals. During this time, houses are decorated with clay lamps, and families share traditional sweets with their neighbors.' \n\nWhich of the following is TRUE according to the passage?",
            "topic": "Reading Comprehension - Specific Details (Spesifik Detaylar)",
            "lesson": "True/False (Doğru/Yanlış) formatındaki sorularda, seçeneklerdeki yargılar metindeki ifadelerle birebir eşleştirilmelidir. Metin dışı çıkarım (inference) yapılmamalıdır.",
            "studyAdvice": "Metindeki eylemlerin (decorate) ve nesnelerin (clay lamps, traditional sweets) bağlam içindeki ilişkilerini analiz et.",
            "options": ["Diwali is only celebrated in complete darkness.", "People decorate their homes with lamps.", "Families fast (eat nothing) during the entire festival.", "It is mainly a food competition."],
            "correct_index": 1,
            "feedbacks": [
                "Yanlış. Metinde tamamen karanlıkta kutlandığına dair bir bilgi yoktur; aksine bir ışık festivalidir.",
                "Doğru! Metindeki 'houses are decorated with clay lamps' ifadesi bu seçeneğin doğruluğunu kanıtlar.",
                "Yanlış. Oruç tutmaktan (fasting) bahsedilmemiştir, aksine tatlı paylaştıkları (share sweets) belirtilmiştir.",
                "Yanlış. Metinde bir yemek yarışmasından (food competition) bahsedilmemektedir."
            ]
        }
    ] ,
    "10. Sınıf İngilizce - Ünite 1": [
        # İleride seninle hazırlayacağımız konseptler buraya liste içine eklenecek.
    ],
    "YDS Kelime Çalışması": [
        # Başka bir konsept şablonu.
    ]
}

# 3. Durum Yönetimi (Session State)
# Uygulama her yenilendiğinde verilerin kaybolmaması için state tanımlamaları
if 'current_category' not in st.session_state:
    st.session_state.current_category = list(QUIZ_DATA.keys())[0]
if 'current_q_index' not in st.session_state:
    st.session_state.current_q_index = 0
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {} # Örn: {'AÖL İngilizce 8': {0: 1, 1: 1}}

# Kategori (Konsept) değiştiğinde soru numarasını sıfırlayan fonksiyon
def reset_index():
    st.session_state.current_q_index = 0
# Veritabanı Bağlantı ve Yazma Fonksiyonları
def get_gsheet_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    # .streamlit/secrets.toml içindeki verileri çekip yetkilendirme objesine dönüştürüyoruz
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes
    )
    client = gspread.authorize(credentials)
    return client

def save_results_to_sheet(category, correct_count, wrong_count):
    try:
        client = get_gsheet_client()
        # Hedef tablonun adını yeni isme göre belirledik
        sheet = client.open("sinif10unite7sonuclari").sheet1
        
        # Zaman damgası (timestamp) oluşturma
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row_data = [now, category, correct_count, wrong_count]
        
        sheet.append_row(row_data)
        return True
    except Exception as e:
        st.error(f"Veritabanı bağlantı hatası (Exception): {e}")
        return False
# 4. Arayüz Tasarımı (UI)
st.sidebar.title("Menü")
selected_category = st.sidebar.selectbox(
    "Test Konseptini Seçin:", 
    list(QUIZ_DATA.keys()), 
    on_change=reset_index
)

questions = QUIZ_DATA[selected_category]

# Eğer seçilen konseptte henüz soru yoksa uyarı verip durduruyoruz.
if not questions:
    st.warning("Bu konsept için henüz soru eklenmedi. İleride eklenecek.")
    st.stop()

# Mevcut sorunun verilerini çekme
current_idx = st.session_state.current_q_index
q_data = questions[current_idx]

# Ekranı iki sütuna ayırma (Sorular | Pedagojik Açıklamalar)
col1, col2 = st.columns([2, 1], gap="large")

with col1:
    st.markdown(f"### {q_data['question']}")
    
    # Kullanıcı daha önce bu soruya cevap vermiş mi kontrolü
    saved_answer = st.session_state.user_answers.get(selected_category, {}).get(current_idx, None)
    
    # Form yapısı kullanımı (Tıklama anında sayfanın gereksiz yenilenmesini önler)
    with st.form(key=f"form_{current_idx}"):
        selected_option = st.radio(
            "Seçenekler:", 
            q_data["options"], 
            index=saved_answer if saved_answer is not None else 0
        )
        submit_btn = st.form_submit_button("Cevapla")
        
        if submit_btn:
            selected_idx = q_data["options"].index(selected_option)
            # Seçimi kaydet
            if selected_category not in st.session_state.user_answers:
                st.session_state.user_answers[selected_category] = {}
            st.session_state.user_answers[selected_category][current_idx] = selected_idx
            st.rerun() # Geri bildirimi göstermek için sayfayı yenile

    # Eğer form gönderildiyse (kullanıcının cevabı varsa) Geri Bildirim göster
    current_saved = st.session_state.user_answers.get(selected_category, {}).get(current_idx, None)
    if current_saved is not None:
        is_correct = (current_saved == q_data["correct_index"])
        feedback_text = q_data["feedbacks"][current_saved]
        
        if is_correct:
            st.success(feedback_text)
        else:
            st.error(feedback_text)

with col2:
    st.info("💡 **Bu Soruyu Doğru Yapmak İçin Neleri Bilmeliydim?**")
    st.markdown(f"**Konu:** {q_data['topic']}")
    st.markdown(f"**Ders Notu:** {q_data['lesson']}")
    st.warning(f"🎯 **Neye Çalışmalısın:** {q_data['studyAdvice']}")

# 5. Navigasyon Butonları
st.divider()
nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])

with nav_col1:
    if st.button("⬅ Önceki Soru", disabled=(current_idx == 0)):
        st.session_state.current_q_index -= 1
        st.rerun()

with nav_col2:
    st.markdown(f"<div style='text-align: center; font-weight: bold; color: gray;'>Soru: {current_idx + 1} / {len(questions)}</div>", unsafe_allow_html=True)

with nav_col3:
    if st.button("Sonraki Soru ➡", disabled=(current_idx == len(questions) - 1)):
        st.session_state.current_q_index += 1
        st.rerun()
        # 6. Analitik ve Veritabanı Kayıt Aşaması
st.divider()
total_questions = len(questions)
answered_questions_count = len(st.session_state.user_answers.get(selected_category, {}))

# Sadece tüm sorular cevaplandığında bu blok aktif olur
if answered_questions_count == total_questions:
    st.info("Tüm soruları yanıtladınız. Performans verilerinizi veritabanına kaydedebilirsiniz.")
    
    # Doğru/Yanlış hesaplama (Iteration)
    corrects = 0
    wrongs = 0
    for q_idx, ans_idx in st.session_state.user_answers[selected_category].items():
        if ans_idx == questions[q_idx]["correct_index"]:
            corrects += 1
        else:
            wrongs += 1
            
    # Metrikleri ekrana yansıtma
    col_res1, col_res2 = st.columns(2)
    col_res1.metric("Doğru Sayısı", corrects)
    col_res2.metric("Yanlış Sayısı", wrongs)
    
    # Veritabanına Push işlemi
    if st.button("Sonuçları Kaydet ve Testi Bitir"):
        with st.spinner('Veriler Google E-Tablolar\'a aktarılıyor...'):
            success = save_results_to_sheet(selected_category, corrects, wrongs)
            if success:
                st.success("İşlem başarılı. Verileriniz kalıcı olarak kaydedildi.")