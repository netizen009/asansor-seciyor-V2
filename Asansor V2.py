import streamlit as st
import math

st.set_page_config(page_title="Asansör Sistem Seçici v2", page_icon="🛗", layout="wide")

# ─────────────────────────────────────────────────────────────────
#  SABİT DEĞERLER
# ─────────────────────────────────────────────────────────────────
KAT_YUKSEKLIGI      = 3000   # mm
YATAKLAMA_TOPLAM    = 150    # mm  (her iki süspansiyon yatağı)
RAY_DUVAR_BOSLUGU   = 100    # mm  (standart taraf)
KABIN_ARKA_BOSLUGU  = 50     # mm  (kabin arka dış — kuyu arka duvarı)
ARKADAN_CW_PAYI     = 300    # mm  (KbD'den düşülür)
CW_Y_BOYU          = 1380   # mm  (CW y-ekseni boyutu)
CW_X_BOYU          = 150    # mm  (CW karkas x-boyutu)
CW_DUVAR_BOSLUGU    = 50     # mm  (CW sağ kenarı — kuyu duvarı, c)
CW_CALISMA_BOSLUGU  = 75     # mm  (CW her iki y ucunda çalışma boşluğu)
CW_RAY_BOSLUGU      = 100    # mm  (CW sol kenarı — kabin sağ dış arası ray+boşluk)
# b = CW_DUVAR_BOSLUGU + CW_X_BOYU + CW_RAY_BOSLUGU = 50+150+100 = 300 mm
CW_B_MESAFE         = CW_DUVAR_BOSLUGU + CW_X_BOYU + CW_RAY_BOSLUGU  # 300 mm
UZAK_MONTE_MESAFE   = 310    # mm  (çakışma durumunda ray-kuyu duvarı arası)

# ─────────────────────────────────────────────────────────────────
#  MEKANİZMA TABLOSU (Tablo A)
#  on_bosluk: kapı tarafı toplam (mekanizma + çalışma boşluğu)
#  arka_bosluk: sabit 50 mm (kabin arka duvarı boşluğu)
# ─────────────────────────────────────────────────────────────────
MEKANIZMA = {
    "Merkezi 2 panel":     {"on": 240, "arka": KABIN_ARKA_BOSLUGU},
    "Merkezi 4 panel":     {"on": 330, "arka": KABIN_ARKA_BOSLUGU},
    "Teleskopik 2 panel":  {"on": 310, "arka": KABIN_ARKA_BOSLUGU},
    "Teleskopik 3 panel":  {"on": 400, "arka": KABIN_ARKA_BOSLUGU},
    "Teleskopik 4 panel":  {"on": 490, "arka": KABIN_ARKA_BOSLUGU},
}

# ─────────────────────────────────────────────────────────────────
#  ANA RAY TABLOSU
#  taban: ray taban genişliği (mm), tip: /A veya /B
# ─────────────────────────────────────────────────────────────────
ANA_RAY = {
    "T50/A  (50 mm)":   {"taban": 50,  "tip": "A", "kapasite_max": 320,  "hiz_max": 1.0},
    "T70/A  (70 mm)":   {"taban": 70,  "tip": "A", "kapasite_max": 630,  "hiz_max": 1.6},
    "T89/B  (89 mm)":   {"taban": 89,  "tip": "B", "kapasite_max": 1000, "hiz_max": 2.5},
    "T114/B (114 mm)":  {"taban": 114, "tip": "B", "kapasite_max": 2000, "hiz_max": 4.0},
    "T127/B (127 mm)":  {"taban": 127, "tip": "B", "kapasite_max": 5000, "hiz_max": 6.0},
}

# ─────────────────────────────────────────────────────────────────
#  ASANSÖR SİSTEM VERİTABANI
# ─────────────────────────────────────────────────────────────────
SISTEMLER = [
    {
        "id": "MRL_GL_11",
        "ad": "MRL · Dişlisiz · 1:1",
        "hiz_secenekler": [1.0, 1.6, 2.5],
        "kapasite_max": 2000, "kapasite_min": 200,
        "kat_max": 40,
        "pit_min": 1100, "overhead_min": 3500,
        "mrdairesi": False,
        "cw_yandan": True, "cw_arkadan": True,
        "avantajlar": ["Makine dairesi gerekmez", "Enerji verimli", "Modern"],
        "dezavantajlar": ["Kuyu üstü ≥3500 mm", "Motor kuyu içinde"],
    },
    {
        "id": "MRL_GL_21",
        "ad": "MRL · Dişlisiz · 2:1",
        "hiz_secenekler": [1.0, 1.6],
        "kapasite_max": 3500, "kapasite_min": 400,
        "kat_max": 20,
        "pit_min": 1200, "overhead_min": 3800,
        "mrdairesi": False,
        "cw_yandan": True, "cw_arkadan": True,
        "avantajlar": ["Makine dairesi gerekmez", "Yüksek kapasite"],
        "dezavantajlar": ["Daha fazla kasnak", "Kuyu üstü kritik"],
    },
    {
        "id": "MRL_GL_11_BACK",
        "ad": "MRL · Dişlisiz · 1:1 · Alttan Palanga",
        "hiz_secenekler": [0.63, 1.0, 1.6],
        "kapasite_max": 1600, "kapasite_min": 200,
        "kat_max": 20,
        "pit_min": 1200, "overhead_min": 2800,
        "mrdairesi": False,
        "cw_yandan": False, "cw_arkadan": True,
        "avantajlar": ["Çok düşük kuyu üstü (≥2800 mm)", "Renovasyon için ideal"],
        "dezavantajlar": ["Kapasite ≤1600 kg", "Karmaşık alt çerçeve"],
    },
    {
        "id": "MR_GR_11",
        "ad": "MR · Dişlili · 1:1",
        "hiz_secenekler": [0.63, 1.0, 1.6],
        "kapasite_max": 2000, "kapasite_min": 200,
        "kat_max": 20,
        "pit_min": 1200, "overhead_min": 3600,
        "mrdairesi": True,
        "cw_yandan": True, "cw_arkadan": True,
        "avantajlar": ["Düşük maliyet", "Yaygın yedek parça"],
        "dezavantajlar": ["Makine dairesi gerekir", "Hız ≤1.6 m/s"],
    },
    {
        "id": "MR_GR_21",
        "ad": "MR · Dişlili · 2:1",
        "hiz_secenekler": [0.63, 1.0],
        "kapasite_max": 5000, "kapasite_min": 500,
        "kat_max": 15,
        "pit_min": 1400, "overhead_min": 4200,
        "mrdairesi": True,
        "cw_yandan": True, "cw_arkadan": True,
        "avantajlar": ["Yüksek kapasite (≤5000 kg)", "Küçük motor"],
        "dezavantajlar": ["Makine dairesi gerekir", "Hız ≤1.0 m/s"],
    },
    {
        "id": "MR_GL_11",
        "ad": "MR · Dişlisiz · 1:1",
        "hiz_secenekler": [2.5, 4.0, 6.0],
        "kapasite_max": 2500, "kapasite_min": 400,
        "kat_max": 100,
        "pit_min": 1500, "overhead_min": 4000,
        "mrdairesi": True,
        "cw_yandan": True, "cw_arkadan": True,
        "avantajlar": ["Çok yüksek hız (≤10 m/s)", "Uzun ömür", "Sessiz"],
        "dezavantajlar": ["Makine dairesi gerekir", "Yüksek maliyet"],
    },
]

# ─────────────────────────────────────────────────────────────────
#  HESAPLAMA FONKSİYONLARI
# ─────────────────────────────────────────────────────────────────

def ray_sec(kapasite, hiz):
    """Kapasiteye ve hıza göre uygun ana ray tipini döndür."""
    for isim, r in ANA_RAY.items():
        if kapasite <= r["kapasite_max"] and hiz <= r["hiz_max"]:
            return isim, r
    # En büyük ray
    isim = list(ANA_RAY.keys())[-1]
    return isim, ANA_RAY[isim]

def kbd_hesapla(kyd, mek_adi, cw_konum):
    """Kabin derinliğini hesapla."""
    mek = MEKANIZMA[mek_adi]
    arka = ARKADAN_CW_PAYI if cw_konum == "Arkadan" else mek["arka"]
    kbd = kyd - mek["on"] - arka
    return kbd

def ray_y_hesapla(kyd, mek_adi, cw_konum):
    """Ana rayın y-eksenindeki konumunu hesapla."""
    kbd = kbd_hesapla(kyd, mek_adi, cw_konum)
    ray_y = KABIN_ARKA_BOSLUGU + kbd / 2
    return ray_y, kbd

def cw_yandan_kontrol(kyg, kyd, mek_adi, ray_taban):
    """
    Yandan CW karar ağacı.
    Döndürür: (gecerli, senaryo, cw_ust, cw_alt, ray_x_sag, mesaj)
    senaryo: 'cakisiyor' | 'cakismiyor' | 'gecersiz'
    """
    ray_y, kbd = ray_y_hesapla(kyd, mek_adi, "Yandan")

    # Adım 1: CW alt köşeye yerleştir, sığıyor mu?
    cw_alt_kose_alt = kyd - CW_CALISMA_BOSLUGU
    cw_alt_kose_ust = kyd - CW_CALISMA_BOSLUGU - CW_Y_BOYU

    if cw_alt_kose_ust < 0:
        return False, "gecersiz", 0, 0, 0, \
            f"CW kuyu içine sığmıyor (CW üst kenarı = {cw_alt_kose_ust:.0f} mm < 0)"

    # Adım 2: Alt köşe konumunda ray_y ile çakışıyor mu?
    cakisiyor = (cw_alt_kose_ust <= ray_y <= cw_alt_kose_alt)

    if cakisiyor:
        # Çakışıyor → CW'yi Ray_y'ye ortala
        cw_ust = ray_y - CW_Y_BOYU / 2
        cw_alt = ray_y + CW_Y_BOYU / 2
        # Ek kontrol: bu konumda kuyu içinde mi?
        if cw_ust < 0 or cw_alt > kyd:
            return False, "gecersiz", 0, 0, 0, \
                "CW çakışıyor ama ortalandığında kuyu dışına çıkıyor"
        ray_x_sag = kyg - UZAK_MONTE_MESAFE - ray_taban / 2
        mesaj = "CW ana ray ile çakışıyor → ray 310 mm uzak monte"
        return True, "cakisiyor", cw_ust, cw_alt, ray_x_sag, mesaj
    else:
        # Çakışmıyor → CW alt köşede
        cw_ust = cw_alt_kose_ust
        cw_alt = cw_alt_kose_alt
        ray_x_sag = kyg - RAY_DUVAR_BOSLUGU - ray_taban / 2
        mesaj = "CW ana ray ile çakışmıyor → ray standart konumda"
        return True, "cakisiyor_degil", cw_ust, cw_alt, ray_x_sag, mesaj

def kbg_hesapla(kyg, ray_taban, cw_konum, cw_gecerli):
    """Kabin genişliğini hesapla."""
    a_sol = RAY_DUVAR_BOSLUGU + ray_taban + YATAKLAMA_TOPLAM / 2

    if cw_konum == "Yandan" and cw_gecerli:
        # Sağ taraf: b = 300 mm sabit (her iki senaryoda da)
        kbg = kyg - a_sol - CW_B_MESAFE
    else:
        a_sag = RAY_DUVAR_BOSLUGU + ray_taban + YATAKLAMA_TOPLAM / 2
        kbg = kyg - a_sol - a_sag

    return kbg

def overhead_hesapla(kuyu_toplam_boy, pit, kat_sayisi):
    """Overhead = Kuyu toplam boy - Pit - Seyir yüksekliği."""
    seyir = (kat_sayisi - 1) * KAT_YUKSEKLIGI
    overhead = kuyu_toplam_boy - pit - seyir
    return overhead, seyir

def sistem_filtrele(kapasite, kat_sayisi, pit, overhead, mr_var):
    """Sistem veritabanını filtrele."""
    uygun = []
    for s in SISTEMLER:
        if kapasite < s["kapasite_min"] or kapasite > s["kapasite_max"]:
            continue
        if kat_sayisi > s["kat_max"]:
            continue
        if pit < s["pit_min"]:
            continue
        if overhead < s["overhead_min"]:
            continue
        if mr_var is False and s["mrdairesi"]:
            continue
        if mr_var is True and not s["mrdairesi"]:
            continue
        uygun.append(s)
    return uygun

# ─────────────────────────────────────────────────────────────────
#  SVG ÜST GÖRÜNÜŞ ÇİZİMİ
# ─────────────────────────────────────────────────────────────────

def svg_ciz(kyg, kyd, kbg, kbd, ray_y, ray_x_sol, ray_x_sag,
            cw_konum, cw_gecerli, cw_ust=None, cw_alt=None,
            mek_adi="", on_bosluk=0):
    """
    Üstten görünüş SVG çizimi.
    Koordinat sistemi: sol üst köşe orijin, sağ=+x, aşağı=+y
    SVG'de: kuyu sol üst = (margin, margin)
    """
    margin = 60
    etiket_alani = 180  # sağ taraf etiket alanı
    W = 680
    H_svg = 500

    # Ölçek: kuyu KyG → SVG genişliğine sığdır
    olcek = (W - 2 * margin - etiket_alani) / max(kyg, kyd, 1)
    # Her iki boyutu da sığdır
    olcek = min(
        (W - 2 * margin - etiket_alani) / kyg,
        (H_svg - 2 * margin) / kyd
    )

    def px(mm):
        return mm * olcek

    # SVG koordinatları
    kx = margin          # kuyu sol kenar
    ky = margin          # kuyu üst kenar
    kw = px(kyg)         # kuyu genişliği
    kh = px(kyd)         # kuyu derinliği

    # Kabin konumu (sol üst köşe)
    # x: sol taraf = 100 + ray_taban + yataklama/2 ... ama ray_x_sol zaten
    # Kabin sol kenarı = a = 100 + ray_taban + 75
    # Ama biz ray_x_sol'u biliyoruz, kabin sol kenarı = ray_x_sol - ray_taban/2 - 75
    # Basitleştirmek için: kabin sol = on_boslugu_yok tarafından hesaplıyoruz
    # kabin sol x = kuyu sol + (KyG - KbG)/2 değil, asimetrik!
    # Sol kenar: 100 + ray + 75 = a_sol
    # Sağ kenar: KyG - (CW_B ya da a_sag)
    # Kabin sol x koordinatı:
    a_sol_mm = RAY_DUVAR_BOSLUGU + (ray_x_sol - margin/olcek - RAY_DUVAR_BOSLUGU) + YATAKLAMA_TOPLAM/2
    # Daha basit: kabin sol kenarı = sol ray merkezi - yataklama/2
    kabin_sol_mm  = ray_x_sol - YATAKLAMA_TOPLAM / 2
    kabin_ust_mm  = on_bosluk  # ön boşluk = kapı tarafı = y=0'dan
    kabin_sag_mm  = kabin_sol_mm + kbg
    kabin_alt_mm  = kabin_ust_mm + kbd

    # SVG px
    kbx = kx + px(kabin_sol_mm)
    kby = ky + px(kabin_ust_mm)
    kbw = px(kbg)
    kbh = px(kbd)

    # Ray pozisyonları
    ray_sol_px  = kx + px(ray_x_sol)
    ray_sag_px  = kx + px(ray_x_sag)
    ray_y_px    = ky + px(ray_y)
    ray_r       = max(4, px(20))  # ray sembolü yarıçapı

    # CW
    cw_svg = ""
    if cw_konum == "Yandan" and cw_gecerli and cw_ust is not None:
        cw_x_sol_mm = kyg - CW_DUVAR_BOSLUGU - CW_X_BOYU
        cw_x_sag_mm = kyg - CW_DUVAR_BOSLUGU
        cx1 = kx + px(cw_x_sol_mm)
        cx2 = kx + px(cw_x_sag_mm)
        cy1 = ky + px(cw_ust)
        cy2 = ky + px(cw_alt)
        cw_svg = f"""
        <rect x="{cx1:.1f}" y="{cy1:.1f}" width="{cx2-cx1:.1f}" height="{cy2-cy1:.1f}"
              fill="none" stroke="#E24B4A" stroke-width="1.5" stroke-dasharray="4 2"/>
        <text x="{(cx1+cx2)/2:.1f}" y="{(cy1+cy2)/2:.1f}" text-anchor="middle"
              dominant-baseline="central" font-size="11" fill="#E24B4A">CW</text>
        <line x1="{(cx1+cx2)/2:.1f}" y1="{cy1:.1f}" x2="{(cx1+cx2)/2:.1f}" y2="{cy2:.1f}"
              stroke="#E24B4A" stroke-width="0.5" stroke-dasharray="2 2"/>
        """
    elif cw_konum == "Arkadan" and kbg > 0:
        # CW arkada: kuyu alt duvarına yaslanmış dikdörtgen
        cw_h_mm = ARKADAN_CW_PAYI
        cw_w_mm = kbg  # kabin genişliği kadar
        cx1 = kbx
        cy1 = ky + px(kyd - cw_h_mm)
        cw_svg = f"""
        <rect x="{cx1:.1f}" y="{cy1:.1f}" width="{kbw:.1f}" height="{px(cw_h_mm):.1f}"
              fill="none" stroke="#E24B4A" stroke-width="1.5" stroke-dasharray="4 2"/>
        <text x="{cx1 + kbw/2:.1f}" y="{cy1 + px(cw_h_mm)/2:.1f}" text-anchor="middle"
              dominant-baseline="central" font-size="11" fill="#E24B4A">CW</text>
        """

    # Tarama için çizgiler (kabin içi diyagonal)
    tarama = ""
    adim = px(120)
    for i in range(-20, 30):
        x1t = kbx + i * adim
        y1t = kby
        x2t = kbx + i * adim + kbh
        y2t = kby + kbh
        # Kırp (basit - sadece çizim sınırları içinde)
        tarama += f'<line x1="{x1t:.1f}" y1="{y1t:.1f}" x2="{x2t:.1f}" y2="{y2t:.1f}" stroke="var(--color-border-secondary)" stroke-width="0.5" clip-path="url(#kabin_clip)"/>'

    svg_h = int(kh + 2 * margin + 20)

    svg = f"""<svg width="100%" viewBox="0 0 {W} {svg_h}" role="img">
<title>Asansör üstten görünüş — {kyg}×{kyd} mm kuyu</title>
<desc>Kuyu, kabin, ana raylar ve karşı ağırlık yerleşiminin üstten görünüşü</desc>
<defs>
  <clipPath id="kabin_clip">
    <rect x="{kbx:.1f}" y="{kby:.1f}" width="{kbw:.1f}" height="{kbh:.1f}"/>
  </clipPath>
</defs>

<!-- Kuyu duvarları (kalın) -->
<rect x="{kx}" y="{ky}" width="{kw:.1f}" height="{kh:.1f}"
      fill="var(--color-background-secondary)" stroke="var(--color-text-primary)" stroke-width="2.5"/>

<!-- Kabin tarama arka plan -->
<rect x="{kbx:.1f}" y="{kby:.1f}" width="{kbw:.1f}" height="{kbh:.1f}"
      fill="var(--color-background-primary)"/>
{tarama}

<!-- Kabin dış çerçeve -->
<rect x="{kbx:.1f}" y="{kby:.1f}" width="{kbw:.1f}" height="{kbh:.1f}"
      fill="none" stroke="var(--color-text-primary)" stroke-width="1.5"/>

<!-- Kabin etiketi -->
<text x="{kbx + kbw/2:.1f}" y="{kby + kbh/2:.1f}"
      text-anchor="middle" dominant-baseline="central"
      font-size="13" font-weight="500" fill="var(--color-text-primary)">kabin</text>

<!-- CW -->
{cw_svg}

<!-- Ana raylar (daire sembolü) -->
<circle cx="{ray_sol_px:.1f}" cy="{ray_y_px:.1f}" r="{ray_r:.1f}"
        fill="none" stroke="#185FA5" stroke-width="1.5"/>
<circle cx="{ray_sol_px:.1f}" cy="{ray_y_px:.1f}" r="2" fill="#185FA5"/>

<circle cx="{ray_sag_px:.1f}" cy="{ray_y_px:.1f}" r="{ray_r:.1f}"
        fill="none" stroke="#185FA5" stroke-width="1.5"/>
<circle cx="{ray_sag_px:.1f}" cy="{ray_y_px:.1f}" r="2" fill="#185FA5"/>

<!-- Ana ray ekseni (yatay mavi çizgi) -->
<line x1="{kx:.1f}" y1="{ray_y_px:.1f}" x2="{kx + kw:.1f}" y2="{ray_y_px:.1f}"
      stroke="#185FA5" stroke-width="0.5" stroke-dasharray="6 3" opacity="0.5"/>

<!-- Ölçü çizgisi: KyG -->
<line x1="{kx:.1f}" y1="{ky - 18:.1f}" x2="{kx + kw:.1f}" y2="{ky - 18:.1f}"
      stroke="var(--color-text-secondary)" stroke-width="0.8"/>
<line x1="{kx:.1f}" y1="{ky - 24:.1f}" x2="{kx:.1f}" y2="{ky - 12:.1f}"
      stroke="var(--color-text-secondary)" stroke-width="0.8"/>
<line x1="{kx + kw:.1f}" y1="{ky - 24:.1f}" x2="{kx + kw:.1f}" y2="{ky - 12:.1f}"
      stroke="var(--color-text-secondary)" stroke-width="0.8"/>
<text x="{kx + kw/2:.1f}" y="{ky - 28:.1f}" text-anchor="middle"
      font-size="11" fill="var(--color-text-secondary)">KyG = {kyg} mm</text>

<!-- Ölçü çizgisi: KyD -->
<line x1="{kx + kw + 18:.1f}" y1="{ky:.1f}" x2="{kx + kw + 18:.1f}" y2="{ky + kh:.1f}"
      stroke="var(--color-text-secondary)" stroke-width="0.8"/>
<line x1="{kx + kw + 12:.1f}" y1="{ky:.1f}" x2="{kx + kw + 24:.1f}" y2="{ky:.1f}"
      stroke="var(--color-text-secondary)" stroke-width="0.8"/>
<line x1="{kx + kw + 12:.1f}" y1="{ky + kh:.1f}" x2="{kx + kw + 24:.1f}" y2="{ky + kh:.1f}"
      stroke="var(--color-text-secondary)" stroke-width="0.8"/>
<text x="{kx + kw + 32:.1f}" y="{ky + kh/2:.1f}" text-anchor="start"
      dominant-baseline="central" font-size="11" fill="var(--color-text-secondary)">KyD = {kyd} mm</text>

<!-- Ölçü: KbG -->
<line x1="{kbx:.1f}" y1="{kby + kbh + 14:.1f}" x2="{kbx + kbw:.1f}" y2="{kby + kbh + 14:.1f}"
      stroke="#1D9E75" stroke-width="0.8"/>
<line x1="{kbx:.1f}" y1="{kby + kbh + 8:.1f}" x2="{kbx:.1f}" y2="{kby + kbh + 20:.1f}"
      stroke="#1D9E75" stroke-width="0.8"/>
<line x1="{kbx + kbw:.1f}" y1="{kby + kbh + 8:.1f}" x2="{kbx + kbw:.1f}" y2="{kby + kbh + 20:.1f}"
      stroke="#1D9E75" stroke-width="0.8"/>
<text x="{kbx + kbw/2:.1f}" y="{kby + kbh + 30:.1f}" text-anchor="middle"
      font-size="11" fill="#1D9E75">KbG = {kbg:.0f} mm</text>

<!-- Ölçü: KbD -->
<line x1="{kbx - 14:.1f}" y1="{kby:.1f}" x2="{kbx - 14:.1f}" y2="{kby + kbh:.1f}"
      stroke="#1D9E75" stroke-width="0.8"/>
<line x1="{kbx - 20:.1f}" y1="{kby:.1f}" x2="{kbx - 8:.1f}" y2="{kby:.1f}"
      stroke="#1D9E75" stroke-width="0.8"/>
<line x1="{kbx - 20:.1f}" y1="{kby + kbh:.1f}" x2="{kbx - 8:.1f}" y2="{kby + kbh:.1f}"
      stroke="#1D9E75" stroke-width="0.8"/>
<text x="{kbx - 24:.1f}" y="{kby + kbh/2:.1f}" text-anchor="middle"
      dominant-baseline="central" font-size="11" fill="#1D9E75"
      transform="rotate(-90, {kbx - 24:.1f}, {kby + kbh/2:.1f})">KbD = {kbd:.0f} mm</text>

<!-- Etiket: x ekseni yönü -->
<text x="{kx + 4:.1f}" y="{ky - 4:.1f}" font-size="10"
      fill="var(--color-text-secondary)">← x (KyG)</text>
<text x="{kx - 12:.1f}" y="{ky + 30:.1f}" font-size="10"
      fill="var(--color-text-secondary)"
      transform="rotate(-90, {kx - 12:.1f}, {ky + 30:.1f})">y (KyD) ↓</text>

<!-- Mekanizma etiketi (kapı tarafı) -->
<text x="{kbx + kbw/2:.1f}" y="{ky + px(on_bosluk/2):.1f}"
      text-anchor="middle" dominant-baseline="central"
      font-size="10" fill="var(--color-text-secondary)">{mek_adi}</text>

</svg>"""
    return svg

# ─────────────────────────────────────────────────────────────────
#  STREAMLIT ARAYÜZÜ
# ─────────────────────────────────────────────────────────────────
st.title("🛗 Asansör Sistem Seçici v2.0")
st.caption("EN 81-20/50 · 2014/33/EU · Ön değerlendirme aracı")

# ── Sidebar: Girdi Parametreleri ─────────────────────────────────
st.sidebar.header("📐 Kuyu Ölçüleri")

kyg = st.sidebar.number_input("Kuyu Genişliği — KyG (mm)", 800, 5000, 2000, 50)
kyd = st.sidebar.number_input("Kuyu Derinliği — KyD (mm)", 800, 6000, 2200, 50)
pit = st.sidebar.number_input("Kuyu Dibi Derinliği — Pit (mm)", 200, 3000, 1200, 50)
kuyu_toplam_boy = st.sidebar.number_input("Kuyu Toplam Boyu (mm) [en alttan en üste]",
                                           3000, 200000, 30000, 500)

st.sidebar.header("🏢 Proje Parametreleri")
kat_sayisi  = st.sidebar.number_input("Kat Sayısı (zemin dahil)", 2, 150, 8, 1)
kapasite    = st.sidebar.slider("Taşıma Kapasitesi (kg)", 100, 5000, 630, 10)
uygulama    = st.sidebar.selectbox("Kullanım Amacı",
                ["Konut", "Ofis/Ticari", "Hastane", "Endüstriyel/Yük", "Otel/Turizm"])

st.sidebar.header("🎯 Tercihler")
mr_durum    = st.sidebar.selectbox("Makine Dairesi",
                ["Makine dairesi yok (MRL)", "Makine dairesi var (MR)", "Fark etmez"])
butce       = st.sidebar.select_slider("Bütçe", ["Ekonomik", "Orta", "Premium"], "Orta")
deprem      = st.sidebar.checkbox("Deprem Bölgesi (EN 81-77)")
yangin      = st.sidebar.checkbox("İtfaiyeci Asansörü (EN 81-72)")

# mr_var çözümle
mr_var = None
if "yok" in mr_durum: mr_var = False
elif "var" in mr_durum: mr_var = True

# ── Hesaplamalar ─────────────────────────────────────────────────
overhead, seyir = overhead_hesapla(kuyu_toplam_boy, pit, kat_sayisi)

# Sistem filtrele
uygun_sistemler = sistem_filtrele(kapasite, kat_sayisi, pit, overhead, mr_var)

# ── Ana Sayfa ─────────────────────────────────────────────────────
col_bilgi1, col_bilgi2, col_bilgi3, col_bilgi4 = st.columns(4)
col_bilgi1.metric("Seyir Yüksekliği", f"{seyir/1000:.1f} m")
col_bilgi2.metric("Overhead (Hesaplanan)", f"{overhead} mm",
                  delta="✓ Yeterli" if overhead > 0 else "✗ Yetersiz",
                  delta_color="normal" if overhead > 0 else "inverse")
col_bilgi3.metric("Pit", f"{pit} mm")
col_bilgi4.metric("Uygun Sistem Sayısı", len(uygun_sistemler))

if overhead <= 0:
    st.error(f"⚠ Overhead hesabı negatif ({overhead} mm). "
             f"Kuyu toplam boyunu veya kat sayısını kontrol edin.")
    st.stop()

st.divider()

if not uygun_sistemler:
    st.error("❌ Girilen parametrelerle uyumlu sistem bulunamadı. Kısıtları gevşetin.")
    st.stop()

st.subheader(f"📊 Uygun Sistemler ({len(uygun_sistemler)} adet)")

# Her sistem için sekme
sistem_adlari = [s["ad"] for s in uygun_sistemler]
tabs = st.tabs(sistem_adlari)

for tab, sistem in zip(tabs, uygun_sistemler):
    with tab:

        # Her CW konumu için
        cw_konumlari = []
        if sistem["cw_yandan"]:  cw_konumlari.append("Yandan")
        if sistem["cw_arkadan"]: cw_konumlari.append("Arkadan")

        for cw_konum in cw_konumlari:
            st.markdown(f"#### Karşı Ağırlık: **{cw_konum}**")

            # Her mekanizma tipi için
            sonuclar = []
            for mek_adi, mek in MEKANIZMA.items():
                kbd = kbd_hesapla(kyd, mek_adi, cw_konum)
                if kbd <= 0:
                    continue

                ray_y_pos, _ = ray_y_hesapla(kyd, mek_adi, cw_konum)

                # Yandan CW kontrolü
                cw_gecerli = True
                cw_senaryo = "-"
                cw_ust_val = cw_alt_val = None
                ray_x_sag_val = kyg - RAY_DUVAR_BOSLUGU

                if cw_konum == "Yandan":
                    cw_gecerli, cw_senaryo, cw_ust_val, cw_alt_val, ray_x_sag_val, cw_mesaj = \
                        cw_yandan_kontrol(kyg, kyd, mek_adi, 89)  # T89 varsayılan
                    if not cw_gecerli:
                        continue

                # Her hız için ray seç ve KbG hesapla
                for hiz in sistem["hiz_secenekler"]:
                    ray_isim, ray_bilgi = ray_sec(kapasite, hiz)
                    ray_taban = ray_bilgi["taban"]

                    # Ray konumları
                    ray_x_sol = RAY_DUVAR_BOSLUGU + ray_taban / 2

                    if cw_konum == "Yandan":
                        _, _, cw_ust_v, cw_alt_v, ray_x_sag_v, _ = \
                            cw_yandan_kontrol(kyg, kyd, mek_adi, ray_taban)
                    else:
                        ray_x_sag_v = kyg - RAY_DUVAR_BOSLUGU - ray_taban / 2
                        cw_ust_v = cw_alt_v = None

                    kbg = kbg_hesapla(kyg, ray_taban, cw_konum,
                                      cw_gecerli if cw_konum == "Yandan" else True)

                    if kbg <= 0:
                        continue

                    sonuclar.append({
                        "mek": mek_adi,
                        "hiz": hiz,
                        "ray": ray_isim,
                        "ray_taban": ray_taban,
                        "kbg": kbg,
                        "kbd": kbd,
                        "ray_x_sol": ray_x_sol,
                        "ray_x_sag": ray_x_sag_v,
                        "ray_y": ray_y_pos,
                        "cw_ust": cw_ust_v,
                        "cw_alt": cw_alt_v,
                        "cw_senaryo": cw_senaryo,
                    })

            if not sonuclar:
                st.warning(f"Bu sistem + {cw_konum} CW kombinasyonunda geçerli sonuç yok.")
                continue

            # Sonuç tablosu
            tablo_veri = []
            for r in sonuclar:
                tablo_veri.append({
                    "Mekanizma": r["mek"],
                    "Hız (m/s)": r["hiz"],
                    "Ana Ray": r["ray"],
                    "KbG (mm)": f"{r['kbg']:.0f}",
                    "KbD (mm)": f"{r['kbd']:.0f}",
                    "CW Durum": r["cw_senaryo"] if cw_konum == "Yandan" else "—",
                })
            st.dataframe(tablo_veri, use_container_width=True, hide_index=True)

            # En iyi sonuç için çizim (ilk hız, ilk mekanizma)
            if sonuclar:
                r = sonuclar[0]
                st.markdown("**📐 Üstten Görünüş** *(ilk kombinasyon)*")
                svg_kodu = svg_ciz(
                    kyg=kyg, kyd=kyd,
                    kbg=r["kbg"], kbd=r["kbd"],
                    ray_y=r["ray_y"],
                    ray_x_sol=r["ray_x_sol"],
                    ray_x_sag=r["ray_x_sag"],
                    cw_konum=cw_konum,
                    cw_gecerli=cw_konum != "Yandan" or r["cw_senaryo"] != "gecersiz",
                    cw_ust=r["cw_ust"],
                    cw_alt=r["cw_alt"],
                    mek_adi=r["mek"],
                    on_bosluk=MEKANIZMA[r["mek"]]["on"],
                )
                st.markdown(svg_kodu, unsafe_allow_html=True)

            st.divider()

        # Sistem bilgileri
        with st.expander("ℹ️ Sistem Detayları"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**✔ Avantajlar**")
                for av in sistem["avantajlar"]:
                    st.markdown(f"- {av}")
            with col2:
                st.markdown("**⚠ Dikkat Edilecekler**")
                for dez in sistem["dezavantajlar"]:
                    st.markdown(f"- {dez}")
            st.markdown(f"**Pit min:** {sistem['pit_min']} mm | "
                        f"**Overhead min:** {sistem['overhead_min']} mm | "
                        f"**Maks kat:** {sistem['kat_max']}")

st.divider()
st.caption("⚠ Bu analiz ön değerlendirme amaçlıdır. Kesin seçim için lisanslı mühendis onayı gerekir.")
if deprem:
    st.warning("⚠ Deprem bölgesi: EN 81-77 sismik gereksinimlerini inceleyin.")
if yangin:
    st.warning("⚠ İtfaiyeci asansörü: EN 81-72 kapsamında ayrı kuyu ve özel kapı gerekir.")