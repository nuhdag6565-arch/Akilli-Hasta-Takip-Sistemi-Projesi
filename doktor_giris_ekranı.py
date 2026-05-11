"""
Modül Adı: doktor_giris_ekrani.py
Açıklama : Doktor Giriş ve Kayıt Ekranı (Streamlit)

           Ekran 1 → GİRİŞ   : TC + Şifre
           Ekran 2 → KAYIT   : TC + Ad + Soyad + Uzmanlık + Şifre
           Ekran 3 → ŞİFRE   : TC + Güvenlik Sorusu Cevabı
           Ekran 4 → PROFİL  : Ad, Soyad, Uzmanlık, Son Giriş

Çalıştırma:
           streamlit run doktor_giris_ekrani.py

Sorumlu  : Nuh Dağ (Veritabanı)
Tarih    : 2026-05-08
Version  : 1.0
"""

import streamlit as st
from datetime import datetime

# Veritabanı fonksiyonları
from database.doktor_islemleri import (
    doktor_kayit,
    doktor_giris,
    doktor_profil_getir,
    guvenlik_sorusu_getir,
    sifre_sifirla,
    sifre_guncelle,
    GECERLI_UZMANLIKLAR,
    GUVENLIK_SORUSU,
)


# ════════════════════════════════════════════════════════════════
# SAYFA AYARLARI
# ════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="İnme Risk Sistemi — Doktor Girişi",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# ════════════════════════════════════════════════════════════════
# GENEL STİL
# ════════════════════════════════════════════════════════════════

st.markdown("""
<style>
/* ── Arka plan ve genel yazı tipi ── */
html, body, [data-testid="stAppViewContainer"] {
    background: #0a0f1e;
    color: #e2e8f0;
    font-family: 'Segoe UI', system-ui, sans-serif;
}

/* ── Merkez kart ── */
.giris-kart {
    background: linear-gradient(135deg, #111827 0%, #1a2540 100%);
    border: 1px solid #1e3a5f;
    border-radius: 20px;
    padding: 2.5rem 2.8rem;
    box-shadow: 0 25px 60px rgba(0,0,0,0.6),
                0 0 0 1px rgba(59,130,246,0.08);
    margin: 0 auto;
    max-width: 480px;
}

/* ── Logo alanı ── */
.logo-alan {
    text-align: center;
    margin-bottom: 2rem;
}
.logo-simge {
    font-size: 3rem;
    display: block;
    margin-bottom: 0.5rem;
    filter: drop-shadow(0 0 16px #3b82f6aa);
}
.logo-baslik {
    font-size: 1.45rem;
    font-weight: 700;
    color: #f1f5f9;
    letter-spacing: -0.3px;
    margin: 0;
}
.logo-alt {
    font-size: 0.82rem;
    color: #64748b;
    margin-top: 4px;
}

/* ── Alan etiketleri ── */
label[data-testid="stWidgetLabel"] p,
.stTextInput label, .stSelectbox label {
    color: #94a3b8 !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    text-transform: uppercase !important;
}

/* ── Input alanları ── */
input[type="text"], input[type="password"],
.stTextInput input, .stSelectbox select {
    background: #0f172a !important;
    border: 1.5px solid #1e3a5f !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    padding: 0.6rem 0.9rem !important;
    font-size: 0.95rem !important;
    transition: border-color 0.2s;
}
input:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
    outline: none !important;
}

/* ── Ana buton ── */
div[data-testid="stButton"] > button {
    width: 100%;
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 1.5rem !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.3px !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 15px rgba(37,99,235,0.35) !important;
    margin-top: 0.4rem;
}
div[data-testid="stButton"] > button:hover {
    background: linear-gradient(135deg, #1d4ed8, #1e40af) !important;
    box-shadow: 0 6px 20px rgba(37,99,235,0.5) !important;
    transform: translateY(-1px) !important;
}

/* ── İkincil bağlantı butonları ── */
.baglanti-buton {
    background: none;
    border: none;
    color: #3b82f6;
    font-size: 0.85rem;
    cursor: pointer;
    padding: 4px 8px;
    border-radius: 6px;
    text-decoration: underline;
    text-underline-offset: 3px;
}
.baglanti-buton:hover { color: #60a5fa; }

/* ── Ayırıcı ── */
.ayirici {
    border: none;
    border-top: 1px solid #1e3a5f;
    margin: 1.5rem 0;
}

/* ── Bilgi kutuları ── */
.bilgi-kutu {
    background: rgba(59,130,246,0.08);
    border: 1px solid rgba(59,130,246,0.25);
    border-radius: 10px;
    padding: 0.8rem 1rem;
    font-size: 0.85rem;
    color: #93c5fd;
    margin-bottom: 1rem;
}
.hata-kutu {
    background: rgba(239,68,68,0.08);
    border: 1px solid rgba(239,68,68,0.3);
    border-radius: 10px;
    padding: 0.8rem 1rem;
    font-size: 0.85rem;
    color: #fca5a5;
    margin-bottom: 1rem;
}
.basari-kutu {
    background: rgba(16,185,129,0.08);
    border: 1px solid rgba(16,185,129,0.3);
    border-radius: 10px;
    padding: 0.8rem 1rem;
    font-size: 0.85rem;
    color: #6ee7b7;
    margin-bottom: 1rem;
}

/* ── Profil kartı ── */
.profil-satir {
    display: flex;
    justify-content: space-between;
    padding: 0.55rem 0;
    border-bottom: 1px solid #1e3a5f;
    font-size: 0.9rem;
}
.profil-etiket { color: #64748b; }
.profil-deger  { color: #e2e8f0; font-weight: 600; }

/* ── Rozet ── */
.rozet {
    display: inline-block;
    background: rgba(59,130,246,0.15);
    color: #60a5fa;
    border: 1px solid rgba(59,130,246,0.3);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.5px;
}

/* Streamlit varsayılan gereksiz boşlukları kaldır */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem !important; }
.stAlert { border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# OTURUM DEĞİŞKENLERİ
# ════════════════════════════════════════════════════════════════

def oturum_baslat():
    """Session state değişkenlerini ilk değerleriyle başlatır."""
    varsayilanlar = {
        "ekran":          "giris",   # giris | kayit | sifre_unut | profil
        "giris_yapildi":  False,
        "doktor_bilgisi": None,      # Giriş sonrası doktor dict'i
        "hata_mesaji":    "",
        "basari_mesaji":  "",
    }
    for anahtar, deger in varsayilanlar.items():
        if anahtar not in st.session_state:
            st.session_state[anahtar] = deger


def ekran_degistir(hedef: str):
    """Ekranı değiştirir ve mesajları temizler."""
    st.session_state.ekran        = hedef
    st.session_state.hata_mesaji  = ""
    st.session_state.basari_mesaji = ""
    st.rerun()


def cikis_yap():
    """Oturumu sonlandırır ve giriş ekranına döner."""
    st.session_state.giris_yapildi  = False
    st.session_state.doktor_bilgisi = None
    ekran_degistir("giris")


# ════════════════════════════════════════════════════════════════
# LOGO BİLEŞENİ
# ════════════════════════════════════════════════════════════════

def logo_goster(alt_baslik: str = "Doktor Portalı"):
    st.markdown(f"""
    <div class="logo-alan">
        <span class="logo-simge">🧠</span>
        <p class="logo-baslik">İnme Risk Sistemi</p>
        <p class="logo-alt">{alt_baslik}</p>
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# MESAJ BİLEŞENİ
# ════════════════════════════════════════════════════════════════

def mesaj_goster():
    """Hata veya başarı mesajı varsa gösterir."""
    if st.session_state.hata_mesaji:
        st.markdown(
            f'<div class="hata-kutu">⚠️ &nbsp;{st.session_state.hata_mesaji}</div>',
            unsafe_allow_html=True,
        )
    if st.session_state.basari_mesaji:
        st.markdown(
            f'<div class="basari-kutu">✅ &nbsp;{st.session_state.basari_mesaji}</div>',
            unsafe_allow_html=True,
        )


# ════════════════════════════════════════════════════════════════
# EKRAN 1 — GİRİŞ
# ════════════════════════════════════════════════════════════════

def giris_ekrani():
    """
    TC kimlik numarası ve şifre ile giriş ekranı.
    İlk kez gelenler için 'Kayıt Ol' butonu,
    şifresini unutanlar için 'Şifremi Unuttum' bağlantısı.
    """
    logo_goster("Doktor Girişi")
    mesaj_goster()

    st.markdown(
        '<div class="bilgi-kutu">'
        '🔑 &nbsp;Sisteme giriş için TC kimlik numaranızı '
        've şifrenizi giriniz.'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── Form alanları ──────────────────────────────────────────
    tc    = st.text_input(
        "TC Kimlik Numarası",
        placeholder="11 haneli TC numaranız",
        max_chars=11,
        key="giris_tc",
    )
    sifre = st.text_input(
        "Şifre",
        type="password",
        placeholder="Şifrenizi giriniz",
        key="giris_sifre",
    )

    # ── Giriş Yap butonu ───────────────────────────────────────
    if st.button("🔐  Giriş Yap", key="btn_giris"):
        if not tc.strip() or not sifre:
            st.session_state.hata_mesaji = "TC ve şifre alanları zorunludur."
            st.rerun()
        else:
            sonuc = doktor_giris(tc_no=tc.strip(), sifre=sifre)
            if sonuc["basarili"]:
                st.session_state.giris_yapildi  = True
                st.session_state.doktor_bilgisi = sonuc["doktor"]
                st.session_state.basari_mesaji  = sonuc["mesaj"]
                ekran_degistir("profil")
            else:
                st.session_state.hata_mesaji = sonuc["mesaj"]
                st.rerun()

    # ── Ayırıcı ───────────────────────────────────────────────
    st.markdown('<hr class="ayirici">', unsafe_allow_html=True)

    # ── Alt bağlantılar ────────────────────────────────────────
    sol, sag = st.columns(2)

    with sol:
        if st.button("📋  Kayıt Ol", key="btn_kayit_git",
                     help="Sisteme ilk kez girecekseniz tıklayın"):
            ekran_degistir("kayit")

    with sag:
        if st.button("🔓  Şifremi Unuttum", key="btn_sifre_git",
                     help="Şifrenizi sıfırlamak için tıklayın"):
            ekran_degistir("sifre_unut")

    st.markdown(
        '<p style="text-align:center;color:#334155;'
        'font-size:0.75rem;margin-top:1.5rem;">'
        'Sisteme erişim yalnızca yetkili sağlık personeline açıktır.'
        '</p>',
        unsafe_allow_html=True,
    )


# ════════════════════════════════════════════════════════════════
# EKRAN 2 — KAYIT OL
# ════════════════════════════════════════════════════════════════

def kayit_ekrani():
    """
    İlk kez giren doktorların TC, ad, soyad, uzmanlık,
    şifre ve güvenlik sorusu cevabını doldurduğu kayıt formu.
    """
    logo_goster("Yeni Hesap Oluştur")
    mesaj_goster()

    st.markdown(
        '<div class="bilgi-kutu">'
        '📋 &nbsp;Sisteme ilk kez giriyorsanız aşağıdaki formu '
        'doldurun. Kayıt sonrasında TC ve şifrenizle giriş yapabilirsiniz.'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── Kişisel Bilgiler ───────────────────────────────────────
    st.markdown("**Kişisel Bilgiler**")

    tc    = st.text_input(
        "TC Kimlik Numarası *",
        placeholder="11 haneli TC numaranız",
        max_chars=11,
        key="kayit_tc",
    )
    ad    = st.text_input(
        "Ad *",
        placeholder="Adınız",
        key="kayit_ad",
    )
    soyad = st.text_input(
        "Soyad *",
        placeholder="Soyadınız",
        key="kayit_soyad",
    )
    uzmanlik = st.selectbox(
        "Uzmanlık Alanı *",
        options=["— Seçiniz —"] + GECERLI_UZMANLIKLAR,
        key="kayit_uzmanlik",
    )

    st.markdown('<hr class="ayirici">', unsafe_allow_html=True)

    # ── Şifre ─────────────────────────────────────────────────
    st.markdown("**Şifre Belirleme**")

    sifre        = st.text_input(
        "Şifre * (en az 6 karakter)",
        type="password",
        placeholder="Şifrenizi belirleyin",
        key="kayit_sifre",
    )
    sifre_tekrar = st.text_input(
        "Şifre Tekrar *",
        type="password",
        placeholder="Şifrenizi tekrar girin",
        key="kayit_sifre_tekrar",
    )

    st.markdown('<hr class="ayirici">', unsafe_allow_html=True)

    # ── Güvenlik Sorusu ────────────────────────────────────────
    st.markdown("**Güvenlik Sorusu**")
    st.markdown(
        f'<p style="color:#94a3b8;font-size:0.85rem;margin-bottom:8px;">'
        f'🔒 &nbsp;<em>{GUVENLIK_SORUSU}</em>'
        f'</p>',
        unsafe_allow_html=True,
    )
    guvenlik = st.text_input(
        "Cevabınız * (şifre sıfırlamada kullanılır)",
        placeholder="Cevabınızı giriniz",
        key="kayit_guvenlik",
    )

    st.markdown("")

    # ── Kayıt Ol butonu ────────────────────────────────────────
    if st.button("✅  Hesap Oluştur", key="btn_kayit"):
        if uzmanlik == "— Seçiniz —":
            st.session_state.hata_mesaji = "Lütfen uzmanlık alanınızı seçin."
            st.rerun()
        else:
            sonuc = doktor_kayit(
                tc_no           = tc.strip(),
                ad              = ad.strip(),
                soyad           = soyad.strip(),
                uzmanlik        = uzmanlik,
                sifre           = sifre,
                sifre_tekrar    = sifre_tekrar,
                guvenlik_cevabi = guvenlik.strip(),
            )
            if sonuc["basarili"]:
                st.session_state.basari_mesaji = (
                    f"{sonuc['mesaj']}  |  ID: {sonuc['doktor_id']}"
                )
                ekran_degistir("giris")
            else:
                st.session_state.hata_mesaji = sonuc["mesaj"]
                st.rerun()

    # ── Geri Dön ──────────────────────────────────────────────
    st.markdown("")
    if st.button("← Giriş Ekranına Dön", key="btn_kayit_geri"):
        ekran_degistir("giris")


# ════════════════════════════════════════════════════════════════
# EKRAN 3 — ŞİFREMİ UNUTTUM
# ════════════════════════════════════════════════════════════════

def sifre_unut_ekrani():
    """
    İki adımlı şifre sıfırlama:
    Adım 1 → TC gir, güvenlik sorusunu al
    Adım 2 → Güvenlik sorusu cevabı + yeni şifre
    """
    logo_goster("Şifre Sıfırlama")
    mesaj_goster()

    # ── Adım 1: TC ile güvenlik sorusunu getir ─────────────────
    st.markdown("**Adım 1 — TC Kimlik Numaranızı Girin**")

    tc = st.text_input(
        "TC Kimlik Numarası",
        placeholder="11 haneli TC numaranız",
        max_chars=11,
        key="sifre_tc",
    )

    soru_metni = None

    if st.button("🔍  Devam Et", key="btn_soru_getir"):
        if not tc.strip():
            st.session_state.hata_mesaji = "TC kimlik numarası boş olamaz."
            st.rerun()
        else:
            soru_sonuc = guvenlik_sorusu_getir(tc.strip())
            if soru_sonuc["basarili"]:
                st.session_state["sifre_tc_onaylandi"] = tc.strip()
                st.session_state["guvenlik_soru"]      = soru_sonuc["soru"]
                st.session_state.hata_mesaji  = ""
                st.rerun()
            else:
                st.session_state.hata_mesaji = soru_sonuc["mesaj"]
                st.rerun()

    # ── Adım 2: Güvenlik sorusu + yeni şifre ──────────────────
    if st.session_state.get("sifre_tc_onaylandi"):

        st.markdown('<hr class="ayirici">', unsafe_allow_html=True)
        st.markdown("**Adım 2 — Güvenlik Sorusu ve Yeni Şifre**")

        soru = st.session_state.get("guvenlik_soru", GUVENLIK_SORUSU)
        st.markdown(
            f'<div class="bilgi-kutu">'
            f'🔒 &nbsp;{soru}'
            f'</div>',
            unsafe_allow_html=True,
        )

        cevap         = st.text_input(
            "Güvenlik Sorusu Cevabı",
            placeholder="Cevabınızı giriniz",
            key="sifre_cevap",
        )
        yeni_sifre    = st.text_input(
            "Yeni Şifre (en az 6 karakter)",
            type="password",
            placeholder="Yeni şifrenizi belirleyin",
            key="yeni_sifre",
        )
        yeni_tekrar   = st.text_input(
            "Yeni Şifre Tekrar",
            type="password",
            placeholder="Yeni şifrenizi tekrar girin",
            key="yeni_sifre_tekrar",
        )

        if st.button("🔄  Şifremi Sıfırla", key="btn_sifre_sifirla"):
            onaylanan_tc = st.session_state["sifre_tc_onaylandi"]
            sonuc = sifre_sifirla(
                tc_no              = onaylanan_tc,
                guvenlik_cevabi    = cevap.strip(),
                yeni_sifre         = yeni_sifre,
                yeni_sifre_tekrar  = yeni_tekrar,
            )
            if sonuc["basarili"]:
                # Adım durumunu temizle
                st.session_state.pop("sifre_tc_onaylandi", None)
                st.session_state.pop("guvenlik_soru",      None)
                st.session_state.basari_mesaji = sonuc["mesaj"]
                ekran_degistir("giris")
            else:
                st.session_state.hata_mesaji = sonuc["mesaj"]
                st.rerun()

    # ── Geri Dön ──────────────────────────────────────────────
    st.markdown("")
    if st.button("← Giriş Ekranına Dön", key="btn_sifre_geri"):
        st.session_state.pop("sifre_tc_onaylandi", None)
        st.session_state.pop("guvenlik_soru",      None)
        ekran_degistir("giris")


# ════════════════════════════════════════════════════════════════
# EKRAN 4 — PROFİL
# ════════════════════════════════════════════════════════════════

def profil_ekrani():
    """
    Giriş yaptıktan sonra gösterilen profil ekranı.
    Ad, Soyad, Uzmanlık, TC, Kayıt Tarihi, Son Giriş bilgileri.
    Şifre güncelleme seçeneği de bulunur.
    """
    doktor = st.session_state.doktor_bilgisi
    if not doktor:
        ekran_degistir("giris")
        return

    # ── Başarı mesajı (giriş sonrası) ─────────────────────────
    mesaj_goster()

    # ── Profil başlığı ─────────────────────────────────────────
    st.markdown(f"""
    <div style="text-align:center;margin-bottom:1.5rem;">
        <div style="font-size:3rem;margin-bottom:0.4rem;">👨‍⚕️</div>
        <div style="font-size:1.3rem;font-weight:700;color:#f1f5f9;">
            Dr. {doktor.get('ad','')} {doktor.get('soyad','')}
        </div>
        <div style="margin-top:6px;">
            <span class="rozet">
                🩺 &nbsp;{doktor.get('uzmanlik','—')}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Profil bilgi satırları ─────────────────────────────────
    st.markdown('<hr class="ayirici">', unsafe_allow_html=True)
    st.markdown("**Hesap Bilgileri**")

    def satir(etiket, deger):
        st.markdown(f"""
        <div class="profil-satir">
            <span class="profil-etiket">{etiket}</span>
            <span class="profil-deger">{deger}</span>
        </div>
        """, unsafe_allow_html=True)

    satir("Doktor ID",    doktor.get("doktor_id", "—"))
    satir("TC No",        doktor.get("tc_no",     "—"))
    satir("Ad Soyad",
          f"Dr. {doktor.get('ad','')} {doktor.get('soyad','')}")
    satir("Uzmanlık",     doktor.get("uzmanlik",  "—"))

    kayit = doktor.get("kayit_tarihi")
    satir("Kayıt Tarihi",
          kayit.strftime("%d.%m.%Y") if isinstance(kayit, datetime) else str(kayit or "—"))

    son_giris = doktor.get("son_giris")
    satir("Son Giriş",
          son_giris.strftime("%d.%m.%Y %H:%M")
          if isinstance(son_giris, datetime) else "İlk giriş")

    satir("Toplam Giriş", str(doktor.get("giris_sayisi", 1)))

    st.markdown('<hr class="ayirici">', unsafe_allow_html=True)

    # ── Şifre güncelleme ───────────────────────────────────────
    with st.expander("🔑  Şifre Değiştir"):
        eski   = st.text_input("Mevcut Şifre", type="password",
                               key="profil_eski_sifre")
        yeni   = st.text_input("Yeni Şifre (en az 6 karakter)",
                               type="password", key="profil_yeni_sifre")
        tekrar = st.text_input("Yeni Şifre Tekrar",
                               type="password", key="profil_yeni_tekrar")

        if st.button("💾  Şifremi Güncelle", key="btn_sifre_guncelle"):
            sonuc = sifre_guncelle(
                tc_no             = doktor["tc_no"],
                eski_sifre        = eski,
                yeni_sifre        = yeni,
                yeni_sifre_tekrar = tekrar,
            )
            if sonuc["basarili"]:
                st.session_state.basari_mesaji = sonuc["mesaj"]
                st.rerun()
            else:
                st.session_state.hata_mesaji = sonuc["mesaj"]
                st.rerun()

    st.markdown("")

    # ── Sisteme Devam Et / Çıkış ──────────────────────────────
    sol, sag = st.columns(2)

    with sol:
        if st.button("🏥  Hasta Modülüne Geç", key="btn_hasta_modul"):
            # İleride dashboard.py'ye yönlendirme buraya gelecek
            st.info("Hasta modülü yakında aktif olacak.")

    with sag:
        if st.button("🚪  Çıkış Yap", key="btn_cikis"):
            cikis_yap()

    st.markdown(
        '<p style="text-align:center;color:#334155;'
        'font-size:0.75rem;margin-top:1.5rem;">'
        '🔒 &nbsp;Bu oturum güvenli bağlantı üzerinden yürütülmektedir.'
        '</p>',
        unsafe_allow_html=True,
    )


# ════════════════════════════════════════════════════════════════
# ANA AKIŞ
# ════════════════════════════════════════════════════════════════

def main():
    oturum_baslat()

    # Doktor giriş yapmışsa ama profil ekranındaysa doğrudan göster
    if st.session_state.giris_yapildi and st.session_state.ekran != "profil":
        st.session_state.ekran = "profil"

    # Merkez sütun düzeni
    _, orta, _ = st.columns([1, 2.2, 1])

    with orta:
        st.markdown('<div class="giris-kart">', unsafe_allow_html=True)

        ekran = st.session_state.ekran

        if ekran == "giris":
            giris_ekrani()
        elif ekran == "kayit":
            kayit_ekrani()
        elif ekran == "sifre_unut":
            sifre_unut_ekrani()
        elif ekran == "profil":
            profil_ekrani()
        else:
            ekran_degistir("giris")

        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()