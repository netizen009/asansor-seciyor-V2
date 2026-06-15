import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Asansör Sistem Seçici v2", page_icon="🛗", layout="wide")

# ─────────────────────────────────────────────────────────────────
#  SABİT DEĞERLER
# ─────────────────────────────────────────────────────────────────
KAT_YUKSEKLIGI     = 3000
YATAKLAMA_TOPLAM   = 150
RAY_DUVAR_BOSLUGU  = 100
KABIN_ARKA_BOSLUGU = 50
ARKADAN_CW_PAYI    = 300
CW_Y_BOYU          = 1380
CW_X_BOYU          = 150
CW_DUVAR_BOSLUGU   = 50
CW_CALISMA_BOSLUGU = 75
CW_B_MESAFE        = 300   # 50+150+100
UZAK_MONTE_MESAFE  = 310
#duvar_payi         = 20

# ─────────────────────────────────────────────────────────────────
#  TABLOLAR
# ─────────────────────────────────────────────────────────────────
MEKANIZMA = {
    "Merkezi 2 panel":    {"on": 240},
    "Merkezi 4 panel":    {"on": 330},
    "Teleskopik 2 panel": {"on": 310},
    "Teleskopik 3 panel": {"on": 400},
    "Teleskopik 4 panel": {"on": 490},
}

ANA_RAY = [
    {"isim": "T50/A  (50mm)",  "taban": 50,  "kap_max": 320,  "hiz_max": 1.0},
    {"isim": "T70/A  (65mm)",  "taban": 65,  "kap_max": 630,  "hiz_max": 1.6},
    {"isim": "T90/B  (75mm)",  "taban": 75,  "kap_max": 1000, "hiz_max": 2.5},
    {"isim": "T114/B (89mm)",  "taban": 89,  "kap_max": 2000, "hiz_max": 4.0},
    {"isim": "T127/B (89mm)",  "taban": 89,  "kap_max": 5000, "hiz_max": 6.0},
]

SISTEMLER = [
    {"id":"MRL_GL_11",      "ad":"MRL · Dişlisiz · 1:1",
     "hizlar":[1.0,1.6,2.5], "kap_min":200,  "kap_max":2000, "kat_max":40,
     "pit_min":1100, "oh_min":3500, "mr":False,
     "cw_yandan":True, "cw_arkadan":True,
     "avantajlar":["Makine dairesi gerekmez","Enerji verimli","Modern"],
     "dezavantajlar":["Kuyu üstü ≥3500mm","Motor kuyu içinde"]},

    {"id":"MRL_GL_21",      "ad":"MRL · Dişlisiz · 2:1",
     "hizlar":[1.0,1.6],     "kap_min":400,  "kap_max":3500, "kat_max":20,
     "pit_min":1200, "oh_min":3800, "mr":False,
     "cw_yandan":True, "cw_arkadan":True,
     "avantajlar":["Makine dairesi gerekmez","Yüksek kapasite"],
     "dezavantajlar":["Daha fazla kasnak","Kuyu üstü kritik"]},

    {"id":"MRL_GL_11_BACK", "ad":"MRL · Dişlisiz · 1:1 · Alttan Palanga",
     "hizlar":[0.63,1.0,1.6],"kap_min":200,  "kap_max":1600, "kat_max":20,
     "pit_min":1200, "oh_min":2800, "mr":False,
     "cw_yandan":False,"cw_arkadan":True,
     "avantajlar":["Çok düşük kuyu üstü (≥2800mm)","Renovasyon için ideal"],
     "dezavantajlar":["Kapasite ≤1600kg","Karmaşık alt çerçeve"]},

    {"id":"MR_GR_11",       "ad":"MR · Dişlili · 1:1",
     "hizlar":[0.63,1.0,1.6],"kap_min":200,  "kap_max":2000, "kat_max":20,
     "pit_min":1200, "oh_min":3600, "mr":True,
     "cw_yandan":True, "cw_arkadan":True,
     "avantajlar":["Düşük maliyet","Yaygın yedek parça"],
     "dezavantajlar":["Makine dairesi gerekir","Hız ≤1.6m/s"]},

    {"id":"MR_GR_21",       "ad":"MR · Dişlili · 2:1",
     "hizlar":[0.63,1.0],    "kap_min":500,  "kap_max":5000, "kat_max":15,
     "pit_min":1400, "oh_min":4200, "mr":True,
     "cw_yandan":True, "cw_arkadan":True,
     "avantajlar":["Yüksek kapasite (≤5000kg)","Küçük motor"],
     "dezavantajlar":["Makine dairesi gerekir","Hız ≤1.0m/s"]},

    {"id":"MR_GL_11",       "ad":"MR · Dişlisiz · 1:1",
     "hizlar":[2.5,4.0,6.0], "kap_min":400,  "kap_max":2500, "kat_max":100,
     "pit_min":1500, "oh_min":4000, "mr":True,
     "cw_yandan":True, "cw_arkadan":True,
     "avantajlar":["Çok yüksek hız","Uzun ömür","Sessiz"],
     "dezavantajlar":["Makine dairesi gerekir","Yüksek maliyet"]},
]

# ─────────────────────────────────────────────────────────────────
#  HESAPLAMA FONKSİYONLARI
# ─────────────────────────────────────────────────────────────────

def ray_sec(kapasite, hiz):
    for r in ANA_RAY:
        if kapasite <= r["kap_max"] and hiz <= r["hiz_max"]:
            return r
    return ANA_RAY[-1]

def kbd_hesapla(kyd, on_bosluk, cw_arkadan):
    arka = ARKADAN_CW_PAYI if cw_arkadan else KABIN_ARKA_BOSLUGU
    return kyd - on_bosluk - arka 

def ray_y_hesapla(kyd, on_bosluk, cw_arkadan):
    kbd = kbd_hesapla(kyd, on_bosluk, cw_arkadan)
    # Kabin on_bosluk'tan başladığı için, ortası on_bosluk + kbd/2 olur
    return on_bosluk + kbd / 2, kbd

def cw_yandan_karar(kyg, kyd, on_bosluk, ray_taban):
    """
    Döner: dict {
      gecerli: bool,
      senaryo: 'cakisiyor'|'cakismiyor'|'gecersiz',
      cw_ust, cw_alt,
      ray_x_sag,
      mesaj
    }
    """
    ray_y, kbd = ray_y_hesapla(kyd, on_bosluk, cw_arkadan=False)

    if kbd <= 0:
        return {"gecerli": False, "senaryo": "gecersiz",
                "mesaj": "KbD ≤ 0, mekanizma kuyu derinliğini aşıyor"}

    # Adım 1: CW alt köşeye yerleştir
    cw_alt_k = kyd - CW_CALISMA_BOSLUGU
    cw_ust_k = cw_alt_k - CW_Y_BOYU

    if cw_ust_k < 0:
        return {"gecerli": False, "senaryo": "gecersiz",
                "mesaj": f"CW kuyu derinliğine sığmıyor (CW üst={cw_ust_k:.0f}mm < 0)"}

    # Adım 2: Çakışma kontrolü
    cakisiyor = (cw_ust_k <= ray_y <= cw_alt_k)

    if cakisiyor:
        # CW'yi ray_y'ye ortala
        cw_ust = ray_y - CW_Y_BOYU / 2
        cw_alt = ray_y + CW_Y_BOYU / 2
        if cw_ust < 0 or cw_alt > kyd:
            return {"gecerli": False, "senaryo": "gecersiz",
                    "mesaj": "CW ortalandığında kuyu dışına çıkıyor"}
        ray_x_sag = kyg - UZAK_MONTE_MESAFE - ray_taban / 2
        return {"gecerli": True, "senaryo": "cakisiyor",
                "cw_ust": cw_ust, "cw_alt": cw_alt,
                "ray_x_sag": ray_x_sag,
                "mesaj": f"Ray ana ağırlıkla çakışıyor → ray {UZAK_MONTE_MESAFE}mm uzak monte"}
    else:
        ray_x_sag = kyg - CW_B_MESAFE - ray_taban / 2
        return {"gecerli": True, "senaryo": "cakismiyor",
                "cw_ust": cw_ust_k, "cw_alt": cw_alt_k,
                "ray_x_sag": ray_x_sag,
                "mesaj": "Ray çakışmıyor → standart konumda"}

def kbg_hesapla(ray_x_sol, ray_x_sag, ray_taban):
    return ray_x_sag - ray_x_sol - ray_taban - YATAKLAMA_TOPLAM

def kombinasyon_puani(r, sistem, seyir_mm, kapasite):
    puan = 0

    seyir_m = seyir_mm / 1000

    # ── Seyir yüksekliği ──────────────────────────
    if "Dişlili" in sistem["ad"]:
        if seyir_m <= 20:
            puan += 100
        elif seyir_m <= 40:
            puan += 50

    elif "Dişlisiz" in sistem["ad"]:
        if seyir_m <= 20:
            puan += 70
        elif seyir_m <= 60:
            puan += 100
        else:
            puan += 80

    # ── Kapasite ─────────────────────────────────
    if kapasite <= 1000:
        if "1:1" in sistem["ad"]:
            puan += 50

    elif kapasite <= 3000:
        if "2:1" in sistem["ad"]:
            puan += 50

    else:
        if "2:1" in sistem["ad"]:
            puan += 100

    # ── Kapı genişliği ───────────────────────────
    puan += r["ll"] / 20

    # ── Kabin alanı ──────────────────────────────
    alan = r["kbg"] * r["kbd"]
    puan += alan / 50000

    # ── Ray ekonomisi ────────────────────────────
    ray_puanlari = {
        50: 100,
        75: 90,
        90: 80,
        114: 70,
        127: 60,
    }

    puan += ray_puanlari.get(r["ray_taban"], 50)

    # ── MRL bonusu ───────────────────────────────
    if not sistem["mr"]:
        puan += 20

    return round(puan, 1)

def tum_kombinasyonlari_hesapla(
    kyg,
    kyd,
    kapasite,
    sistem,
    seyir_mm
):
    """
    Tüm geçerli (cw_konum, mekanizma, hız) kombinasyonlarını hesapla.
    Her biri için kabin boyutları ve ray konumlarını döndür.
    """
    sonuclar = []

    cw_konumlari = []
    if sistem["cw_yandan"]:   cw_konumlari.append("Yandan")
    if sistem["cw_arkadan"]:  cw_konumlari.append("Arkadan")

    for cw_konum in cw_konumlari:
        for mek_adi, mek in MEKANIZMA.items():
            on_bosluk = mek["on"]
            cw_arkadan = (cw_konum == "Arkadan")

            kbd = kbd_hesapla(kyd, on_bosluk, cw_arkadan)
            if kbd <= 200:   # minimum kabin derinliği
                continue

            ray_y, _ = ray_y_hesapla(kyd, on_bosluk, cw_arkadan)

            for hiz in sistem["hizlar"]:
                ray = ray_sec(kapasite, hiz)
                ray_taban = ray["taban"]
                ray_x_sol = RAY_DUVAR_BOSLUGU + ray_taban / 2

                if cw_konum == "Yandan":
                    cw = cw_yandan_karar(kyg, kyd, on_bosluk, ray_taban)
                    if not cw["gecerli"]:
                        continue
                    ray_x_sag = cw["ray_x_sag"]
                    cw_ust    = cw["cw_ust"]
                    cw_alt    = cw["cw_alt"]
                    cw_senaryo = cw["senaryo"]
                    cw_mesaj   = cw["mesaj"]
                    kbg_max = kbg_hesapla(ray_x_sol, ray_x_sag, ray_taban)
                    kullanilabilir_w = kyg - CW_B_MESAFE  # CW tarafı hariç kullanılabilir genişlik
                else:
                    ray_x_sag = kyg - RAY_DUVAR_BOSLUGU - ray_taban / 2
                    cw_ust = cw_alt = None
                    cw_senaryo = "—"
                    cw_mesaj   = "Arkadan CW"
                    kbg_max = kbg_hesapla(ray_x_sol, ray_x_sag, ray_taban)
                    kullanilabilir_w = kyg

                if kbg_max <= 200:  # minimum kabin genişliği
                    continue

                # Kapı (LL) ve Mekanizma Genişliği (TMG) Hesabı
                max_ll = kbg_max - 200
                
                # Standart adımlara göre kapı seçimi
                if "3 panel" in mek_adi or "4 panel" in mek_adi:
                    uygun_ll_listesi = [ll for ll in [800, 900, 1000, 1100, 1200] if ll <= max_ll]
                else:
                    uygun_ll_listesi = [ll for ll in [700, 800, 900, 1000, 1100, 1200] if ll <= max_ll]
                
                if not uygun_ll_listesi:
                    continue  # Bu kuyuya standart bir kapı sığmıyor
                    
                gecerli_ll_ve_tmg = []
                for secilen_ll in uygun_ll_listesi:
                    # TMG (Toplam Mekanizma Genişliği) formülleri
                    if mek_adi == "Merkezi 2 panel": tmg = (2.0 * secilen_ll) + 50
                    elif mek_adi == "Merkezi 4 panel": tmg = (1.5 * secilen_ll) + 50
                    elif mek_adi == "Teleskopik 2 panel": tmg = (1.5 * secilen_ll) + 100
                    elif mek_adi == "Teleskopik 3 panel": tmg = (1.33 * secilen_ll) + 100
                    elif mek_adi == "Teleskopik 4 panel": tmg = (1.25 * secilen_ll) + 100
                    else: tmg = (2.0 * secilen_ll) + 50
                    
                    # TMG kuyuya sığıyor mu? (50 mm çalışma toleransı ile)
                    if tmg + 50 <= kullanilabilir_w:
                        gecerli_ll_ve_tmg.append((secilen_ll, tmg))
                        
                if not gecerli_ll_ve_tmg:
                    continue
                    
                # En büyükten başlayarak 3 adede kadar al (2 basamak altı)
                gecerli_ll_ve_tmg.sort(key=lambda x: x[0], reverse=True)
                sinirli_ll_listesi = gecerli_ll_ve_tmg[:3]

                puan = kombinasyon_puani(
                    {
                        "ll": secilen_ll,
                        "kbg": round(kbg_max),
                        "kbd": round(kbd),
                        "ray_taban": ray_taban
                    },
                    sistem,
                    seyir_mm,
                    kapasite
                )
                
                for secilen_ll, tmg in sinirli_ll_listesi:
                    sonuclar.append({
                        "cw_konum":   cw_konum,
                        "mek":        mek_adi,
                        "hiz":        hiz,
                        "ray_isim":   ray["isim"],
                        "ray_taban":  ray_taban,
                        "kbg":        round(kbg_max),
                        "kbd":        round(kbd),
                        "ray_x_sol":  ray_x_sol,
                        "ray_x_sag":  ray_x_sag,
                        "ray_y":      ray_y,
                        "cw_ust":     cw_ust,
                        "cw_alt":     cw_alt,
                        "cw_senaryo": cw_senaryo,
                        "cw_mesaj":   cw_mesaj,
                        "on_bosluk":  on_bosluk,
                        "ll":         secilen_ll,
                        "tmg":        round(tmg),
                        "puan":       puan,
                    })

    sonuclar.sort(
    key=lambda x: x["puan"],
    reverse=True
    )
    return sonuclar

# ─────────────────────────────────────────────────────────────────
#  SVG ÜST GÖRÜNÜŞ
# ─────────────────────────────────────────────────────────────────

def svg_ciz(r, kyg, kyd, uid="0"):
    """Üstten görünüş teknik şeması."""
    clip_id = f"cb_{uid}"
    SVG_W  = 760
    ML     = 70    # sol margin  (KbD ölçüsü)
    MR     = 100   # sağ margin  (KyD ölçüsü)
    MT     = 50    # üst margin  (KyG ölçüsü)
    MB     = 50    # alt margin  (KbG ölçüsü)

    olcek = min(
        (SVG_W - ML - MR) / kyg,
        (SVG_W - ML - MR) / kyd
    )
    def px(mm): return mm * olcek
    def sx(mm): return ML + px(mm)
    def sy(mm): return MT + px(mm)

    kw = px(kyg); kh = px(kyd)
    SVG_H = int(kh + MT + MB + 20)

    # ── Geometri ──────────────────────────────────────────────────
    kabin_sol = r["ray_x_sol"] + r["ray_taban"]/2 + YATAKLAMA_TOPLAM/2
    kabin_ust = r["on_bosluk"]
    kabin_sag = kabin_sol + r["kbg"]
    kabin_alt = kabin_ust + r["kbd"]

    kbx1 = sx(kabin_sol); kby1 = sy(kabin_ust)
    kbx2 = sx(kabin_sag); kby2 = sy(kabin_alt)
    kbw  = kbx2 - kbx1;  kbh  = kby2 - kby1

    rsx = sx(r["ray_x_sol"]); rsy = sy(r["ray_y"])
    rdx = sx(r["ray_x_sag"]); rdy = sy(r["ray_y"])
    rr  = max(5, px(13))
    kabin_cx = (kbx1 + kbx2) / 2

    # ── Açılım formülleri (programa gömülü) ──────────────────────
    kpg = r["ll"]
    acilim_mm = {
        "Merkezi 2 panel":    (kpg/2 + 25) * 2 + kpg,
        "Merkezi 4 panel":    (kpg/4 + 25) * 2 + kpg,
        "Teleskopik 2 panel": (kpg/2 + 25)     + kpg,
        "Teleskopik 3 panel": (kpg/3 + 25)     + kpg,
        "Teleskopik 4 panel": (kpg/4 + 25)     + kpg,
    }.get(r["mek"], kpg)

    # ── Tarama (kabin içi) ────────────────────────────────────────
    tarama = ""
    adim = max(12, px(90))
    for i in range(-2, int((kbw+kbh)/adim)+4):
        x1t = kbx1 + i*adim; x2t = kbx1
        y1t = kby1;           y2t = kby1 + i*adim
        tarama += (f'<line x1="{x1t:.1f}" y1="{y1t:.1f}" '
                   f'x2="{x2t:.1f}" y2="{y2t:.1f}" '
                   f'stroke="#94A3B8" stroke-width="0.4" '
                   f'clip-path="url(#{clip_id})"/>')

    # ── Mekanizma kutusu (3 satır, çakışmasın) ───────────────────
    mek_h_px = px(r["on_bosluk"])
    mek_svg  = ""
    if mek_h_px > 20:
        # 3 satır için yeterli alan var mı? yoksa iki satıra sığdır
        satirlar = [r["mek"], f"KpG={kpg}mm  Açılım={acilim_mm:.0f}mm"]
        if mek_h_px > 36:
            satirlar = [r["mek"], f"KpG = {kpg} mm", f"Açılım = {acilim_mm:.0f} mm"]
        mek_svg = (
            f'<rect x="{kbx1:.1f}" y="{MT:.1f}" '
            f'width="{kbw:.1f}" height="{mek_h_px:.1f}" '
            f'fill="#DBEAFE" stroke="#3B82F6" stroke-width="0.8" stroke-dasharray="4 2"/>'
        )
        n_satir = len(satirlar)
        for idx, satir in enumerate(satirlar):
            oy = MT + mek_h_px * (idx + 1) / (n_satir + 1)
            mek_svg += (
                f'<text x="{kabin_cx:.1f}" y="{oy:.1f}" '
                f'text-anchor="middle" dominant-baseline="central" '
                f'font-size="9" fill="#1D4ED8">{satir}</text>'
            )

    # ── CW ───────────────────────────────────────────────────────
    cw_svg = ""
    if r["cw_konum"] == "Yandan" and r["cw_ust"] is not None:
        cx1 = sx(kyg - CW_DUVAR_BOSLUGU - CW_X_BOYU)
        cx2 = sx(kyg - CW_DUVAR_BOSLUGU)
        cy1 = sy(r["cw_ust"]); cy2 = sy(r["cw_alt"])
        cw_cx = (cx1+cx2)/2;   cw_cy = (cy1+cy2)/2
        cw_svg = (
            f'<rect x="{cx1:.1f}" y="{cy1:.1f}" '
            f'width="{cx2-cx1:.1f}" height="{cy2-cy1:.1f}" '
            f'fill="#FEE2E2" stroke="#DC2626" stroke-width="1.5"/>'
            f'<line x1="{cw_cx:.1f}" y1="{cy1:.1f}" '
            f'x2="{cw_cx:.1f}" y2="{cy2:.1f}" '
            f'stroke="#DC2626" stroke-width="0.5" stroke-dasharray="3 2"/>'
            f'<text x="{cw_cx:.1f}" y="{cw_cy:.1f}" '
            f'text-anchor="middle" dominant-baseline="central" '
            f'font-size="10" font-weight="bold" fill="#DC2626">CW</text>'
        )
    elif r["cw_konum"] == "Arkadan":
        cw_w = CW_Y_BOYU; cw_h = CW_X_BOYU
        cx1 = sx(kyg/2 - cw_w/2); cx2 = sx(kyg/2 + cw_w/2)
        cy1 = sy(kyd - ARKADAN_CW_PAYI + (ARKADAN_CW_PAYI - cw_h)/2)
        cy2 = cy1 + px(cw_h)
        cw_cx = (cx1+cx2)/2; cw_cy = (cy1+cy2)/2
        cw_svg = (
            f'<rect x="{cx1:.1f}" y="{cy1:.1f}" '
            f'width="{cx2-cx1:.1f}" height="{cy2-cy1:.1f}" '
            f'fill="#FEE2E2" stroke="#DC2626" stroke-width="1.5"/>'
            f'<text x="{cw_cx:.1f}" y="{cw_cy:.1f}" '
            f'text-anchor="middle" dominant-baseline="central" '
            f'font-size="10" font-weight="bold" fill="#DC2626">CW</text>'
        )

    # ── RA ölçüsü (ray arası, ray ekseninin altında) ──────────────
    if r["cw_konum"] == "Arkadan":
        ra_mm = kyg - 2 * (RAY_DUVAR_BOSLUGU + r["ray_taban"])

    elif r["cw_senaryo"] == "cakisiyor":
        ra_mm = kyg - RAY_DUVAR_BOSLUGU - UZAK_MONTE_MESAFE - 2 * r["ray_taban"]

    else:
        ra_mm = kyg - RAY_DUVAR_BOSLUGU - CW_B_MESAFE - 2 * r["ray_taban"]
    ra_y  = rsy + rr + 20
    ra_svg = (
        f'<line x1="{rsx:.1f}" y1="{ra_y:.1f}" '
        f'x2="{rdx:.1f}" y2="{ra_y:.1f}" stroke="#1D4ED8" stroke-width="0.8"/>'
        f'<polygon points="{rsx:.1f},{ra_y:.1f} {rsx+7:.1f},{ra_y-3:.1f} {rsx+7:.1f},{ra_y+3:.1f}" fill="#1D4ED8"/>'
        f'<polygon points="{rdx:.1f},{ra_y:.1f} {rdx-7:.1f},{ra_y-3:.1f} {rdx-7:.1f},{ra_y+3:.1f}" fill="#1D4ED8"/>'
        f'<line x1="{rsx:.1f}" y1="{rsy+rr:.1f}" x2="{rsx:.1f}" y2="{ra_y:.1f}" '
        f'stroke="#1D4ED8" stroke-width="0.4" stroke-dasharray="2 2"/>'
        f'<line x1="{rdx:.1f}" y1="{rdy+rr:.1f}" x2="{rdx:.1f}" y2="{ra_y:.1f}" '
        f'stroke="#1D4ED8" stroke-width="0.4" stroke-dasharray="2 2"/>'
        f'<text x="{(rsx+rdx)/2:.1f}" y="{ra_y-5:.1f}" '
        f'text-anchor="middle" font-size="9" fill="#1D4ED8" font-family="monospace">'
        f'RA={ra_mm:.0f}mm | {r["ray_isim"]}</text>'
    )

    # ── SVG ──────────────────────────────────────────────────────
    # Ölçü konumları (çakışmasın diye net ayrılmış)
    kyg_y  = MT - 32            # KyG ölçüsü: kuyunun üstünde
    kyd_x  = ML + kw + 30      # KyD ölçüsü: kuyunun sağında
    kbg_y  = MT + kh + 28      # KbG ölçüsü: kuyunun altında
    kbd_x  = ML - 32            # KbD ölçüsü: kuyunun solunda

    svg = f"""<svg width="100%" viewBox="0 0 {SVG_W} {SVG_H}"
     xmlns="http://www.w3.org/2000/svg"
     style="background:white">
<defs>
  <clipPath id="{clip_id}">
    <rect x="{kbx1:.1f}" y="{kby1:.1f}" width="{kbw:.1f}" height="{kbh:.1f}"/>
  </clipPath>
</defs>

<!-- Kuyu -->
<rect x="{ML}" y="{MT}" width="{kw:.1f}" height="{kh:.1f}"
      fill="#F1F5F9" stroke="#1E293B" stroke-width="3"/>

<!-- Kabin zemin + tarama -->
<rect x="{kbx1:.1f}" y="{kby1:.1f}" width="{kbw:.1f}" height="{kbh:.1f}" fill="white"/>
{tarama}
<rect x="{kbx1:.1f}" y="{kby1:.1f}" width="{kbw:.1f}" height="{kbh:.1f}"
      fill="none" stroke="#1E293B" stroke-width="1.8"/>

<!-- Kabin etiketi — alt yarıda, RA ölçüsünün ÜSTÜNDE -->
<text x="{kabin_cx:.1f}" y="{(kby1*0.35 + kby2*0.65):.1f}"
      text-anchor="middle" dominant-baseline="central"
      font-size="13" font-weight="600" fill="#334155">kabin</text>
<text x="{kabin_cx:.1f}" y="{(kby1*0.35 + kby2*0.65) + 16:.1f}"
      text-anchor="middle" dominant-baseline="central"
      font-size="10" fill="#64748B">{r["kbg"]}×{r["kbd"]} mm</text>

<!-- Mekanizma -->
{mek_svg}

<!-- CW -->
{cw_svg}

<!-- Ana raylar (daire + dolu kare = T-ray sembolü) -->
<circle cx="{rsx:.1f}" cy="{rsy:.1f}" r="{rr:.1f}"
        fill="white" stroke="#1E3A8A" stroke-width="1.8"/>
<rect x="{rsx-rr*0.42:.1f}" y="{rsy-rr*0.42:.1f}"
      width="{rr*0.84:.1f}" height="{rr*0.84:.1f}" fill="#1E3A8A"/>
<circle cx="{rdx:.1f}" cy="{rdy:.1f}" r="{rr:.1f}"
        fill="white" stroke="#1E3A8A" stroke-width="1.8"/>
<rect x="{rdx-rr*0.42:.1f}" y="{rdy-rr*0.42:.1f}"
      width="{rr*0.84:.1f}" height="{rr*0.84:.1f}" fill="#1E3A8A"/>

<!-- Ağırlık merkezi ekseni (yatay kesik) -->
<line x1="{ML:.1f}" y1="{rsy:.1f}" x2="{ML+kw:.1f}" y2="{rsy:.1f}"
      stroke="#2563EB" stroke-width="0.7" stroke-dasharray="10 4" opacity="0.55"/>

<!-- Kabin simetri ekseni (dikey kesik) -->
<line x1="{kabin_cx:.1f}" y1="{kby1:.1f}" x2="{kabin_cx:.1f}" y2="{kby2:.1f}"
      stroke="#94A3B8" stroke-width="0.5" stroke-dasharray="5 3"/>

<!-- RA ölçüsü -->
{ra_svg}

<!-- ── KyG (üst) ── -->
<line x1="{ML:.1f}" y1="{kyg_y:.1f}" x2="{ML+kw:.1f}" y2="{kyg_y:.1f}"
      stroke="#374151" stroke-width="0.8"/>
<polygon points="{ML:.1f},{kyg_y:.1f} {ML+7:.1f},{kyg_y-3:.1f} {ML+7:.1f},{kyg_y+3:.1f}" fill="#374151"/>
<polygon points="{ML+kw:.1f},{kyg_y:.1f} {ML+kw-7:.1f},{kyg_y-3:.1f} {ML+kw-7:.1f},{kyg_y+3:.1f}" fill="#374151"/>
<line x1="{ML:.1f}" y1="{MT:.1f}" x2="{ML:.1f}" y2="{kyg_y+1:.1f}"
      stroke="#9CA3AF" stroke-width="0.5" stroke-dasharray="2 2"/>
<line x1="{ML+kw:.1f}" y1="{MT:.1f}" x2="{ML+kw:.1f}" y2="{kyg_y+1:.1f}"
      stroke="#9CA3AF" stroke-width="0.5" stroke-dasharray="2 2"/>
<text x="{ML+kw/2:.1f}" y="{kyg_y-7:.1f}" text-anchor="middle"
      font-size="10" fill="#374151" font-family="monospace">KyG = {kyg} mm</text>

<!-- ── KyD (sağ) ── -->
<line x1="{kyd_x:.1f}" y1="{MT:.1f}" x2="{kyd_x:.1f}" y2="{MT+kh:.1f}"
      stroke="#374151" stroke-width="0.8"/>
<polygon points="{kyd_x:.1f},{MT:.1f} {kyd_x-3:.1f},{MT+7:.1f} {kyd_x+3:.1f},{MT+7:.1f}" fill="#374151"/>
<polygon points="{kyd_x:.1f},{MT+kh:.1f} {kyd_x-3:.1f},{MT+kh-7:.1f} {kyd_x+3:.1f},{MT+kh-7:.1f}" fill="#374151"/>
<line x1="{ML+kw:.1f}" y1="{MT:.1f}" x2="{kyd_x-1:.1f}" y2="{MT:.1f}"
      stroke="#9CA3AF" stroke-width="0.5" stroke-dasharray="2 2"/>
<line x1="{ML+kw:.1f}" y1="{MT+kh:.1f}" x2="{kyd_x-1:.1f}" y2="{MT+kh:.1f}"
      stroke="#9CA3AF" stroke-width="0.5" stroke-dasharray="2 2"/>
<text x="{kyd_x+5:.1f}" y="{MT+kh/2:.1f}" text-anchor="start" dominant-baseline="central"
      font-size="10" fill="#374151" font-family="monospace">KyD={kyd}mm</text>

<!-- ── KbG (alt) ── -->
<line x1="{kbx1:.1f}" y1="{kbg_y:.1f}" x2="{kbx2:.1f}" y2="{kbg_y:.1f}"
      stroke="#059669" stroke-width="0.8"/>
<polygon points="{kbx1:.1f},{kbg_y:.1f} {kbx1+7:.1f},{kbg_y-3:.1f} {kbx1+7:.1f},{kbg_y+3:.1f}" fill="#059669"/>
<polygon points="{kbx2:.1f},{kbg_y:.1f} {kbx2-7:.1f},{kbg_y-3:.1f} {kbx2-7:.1f},{kbg_y+3:.1f}" fill="#059669"/>
<line x1="{kbx1:.1f}" y1="{MT+kh:.1f}" x2="{kbx1:.1f}" y2="{kbg_y-1:.1f}"
      stroke="#6EE7B7" stroke-width="0.5" stroke-dasharray="2 2"/>
<line x1="{kbx2:.1f}" y1="{MT+kh:.1f}" x2="{kbx2:.1f}" y2="{kbg_y-1:.1f}"
      stroke="#6EE7B7" stroke-width="0.5" stroke-dasharray="2 2"/>
<text x="{kabin_cx:.1f}" y="{kbg_y+14:.1f}" text-anchor="middle"
      font-size="10" fill="#059669" font-family="monospace">KbG={r["kbg"]}mm</text>

<!-- ── KbD (sol) ── -->
<line x1="{kbd_x:.1f}" y1="{kby1:.1f}" x2="{kbd_x:.1f}" y2="{kby2:.1f}"
      stroke="#059669" stroke-width="0.8"/>
<polygon points="{kbd_x:.1f},{kby1:.1f} {kbd_x-3:.1f},{kby1+7:.1f} {kbd_x+3:.1f},{kby1+7:.1f}" fill="#059669"/>
<polygon points="{kbd_x:.1f},{kby2:.1f} {kbd_x-3:.1f},{kby2-7:.1f} {kbd_x+3:.1f},{kby2-7:.1f}" fill="#059669"/>
<line x1="{kbx1:.1f}" y1="{kby1:.1f}" x2="{kbd_x-1:.1f}" y2="{kby1:.1f}"
      stroke="#6EE7B7" stroke-width="0.5" stroke-dasharray="2 2"/>
<line x1="{kbx1:.1f}" y1="{kby2:.1f}" x2="{kbd_x-1:.1f}" y2="{kby2:.1f}"
      stroke="#6EE7B7" stroke-width="0.5" stroke-dasharray="2 2"/>
<text x="{kbd_x-5:.1f}" y="{(kby1+kby2)/2:.1f}" text-anchor="middle"
      dominant-baseline="central" font-size="10" fill="#059669" font-family="monospace"
      transform="rotate(-90,{kbd_x-5:.1f},{(kby1+kby2)/2:.1f})">KbD={r["kbd"]}mm</text>

<!-- ── Koordinat orijini (sol üst köşe, doğru yönler) ── -->
<!-- x ekseni: sağa → -->
<line x1="{ML:.1f}" y1="{MT:.1f}" x2="{ML+28:.1f}" y2="{MT:.1f}"
      stroke="#94A3B8" stroke-width="1"/>
<polygon points="{ML+28:.1f},{MT:.1f} {ML+22:.1f},{MT-2.5:.1f} {ML+22:.1f},{MT+2.5:.1f}"
         fill="#94A3B8"/>
<text x="{ML+32:.1f}" y="{MT:.1f}" dominant-baseline="central"
      font-size="8" fill="#94A3B8">x</text>
<!-- y ekseni: aşağı ↓ -->
<line x1="{ML:.1f}" y1="{MT:.1f}" x2="{ML:.1f}" y2="{MT+28:.1f}"
      stroke="#94A3B8" stroke-width="1"/>
<polygon points="{ML:.1f},{MT+28:.1f} {ML-2.5:.1f},{MT+22:.1f} {ML+2.5:.1f},{MT+22:.1f}"
         fill="#94A3B8"/>
<text x="{ML:.1f}" y="{MT+34:.1f}" text-anchor="middle"
      font-size="8" fill="#94A3B8">y</text>
<!-- Orijin noktası -->
<circle cx="{ML:.1f}" cy="{MT:.1f}" r="2.5" fill="#94A3B8"/>

<!-- ── Başlık (alt) ── -->
<text x="{SVG_W/2:.1f}" y="{SVG_H-5:.1f}" text-anchor="middle"
      font-size="9" fill="#94A3B8" font-family="monospace"
>{r["mek"]} | CW:{r["cw_konum"]} | {r["hiz"]}m/s | {r["ray_isim"]}</text>
</svg>"""

    return svg, SVG_H

    # Kabin kenarları (mm cinsinden)
    kabin_sol  = r["ray_x_sol"] + r["ray_taban"]/2 + YATAKLAMA_TOPLAM/2
    kabin_ust  = r["on_bosluk"]
    kabin_sag  = kabin_sol + r["kbg"]
    kabin_alt  = kabin_ust + r["kbd"]

    kbx1 = sx(kabin_sol);  kby1 = sy(kabin_ust)
    kbx2 = sx(kabin_sag);  kby2 = sy(kabin_alt)
    kbw  = kbx2 - kbx1;    kbh  = kby2 - kby1

    # Ray px
    rsx  = sx(r["ray_x_sol"]); rsy  = sy(r["ray_y"])
    rdx  = sx(r["ray_x_sag"]); rdy  = sy(r["ray_y"])
    rr   = max(5, px(15))

    # CW
    cw_svg = ""
    if r["cw_konum"] == "Yandan" and r["cw_ust"] is not None:
        cx1 = sx(kyg - CW_DUVAR_BOSLUGU - CW_X_BOYU)
        cx2 = sx(kyg - CW_DUVAR_BOSLUGU)
        cy1 = sy(r["cw_ust"]); cy2 = sy(r["cw_alt"])
        cw_cx = (cx1+cx2)/2; cw_cy = (cy1+cy2)/2
        cw_svg = f"""
  <rect x="{cx1:.1f}" y="{cy1:.1f}" width="{cx2-cx1:.1f}" height="{cy2-cy1:.1f}"
        fill="#FEE2E2" stroke="#DC2626" stroke-width="1.5"/>
  <text x="{cw_cx:.1f}" y="{cw_cy:.1f}" text-anchor="middle" dominant-baseline="central"
        font-size="11" font-weight="bold" fill="#DC2626">CW</text>
  <line x1="{cw_cx:.1f}" y1="{cy1:.1f}" x2="{cw_cx:.1f}" y2="{cy2:.1f}"
        stroke="#DC2626" stroke-width="0.5" stroke-dasharray="3 2"/>"""
    elif r["cw_konum"] == "Arkadan":
        # Arkadan CW: genişlik 1380 mm (CW_Y_BOYU), derinlik 150 mm (CW_X_BOYU)
        cw_w = CW_Y_BOYU
        cw_h = CW_X_BOYU
        cx1 = sx(kyg/2 - cw_w/2); cx2 = sx(kyg/2 + cw_w/2)
        cy1 = sy(kyd - ARKADAN_CW_PAYI + (ARKADAN_CW_PAYI - cw_h)/2); cy2 = cy1 + px(cw_h)
        cw_cx=(cx1+cx2)/2; cw_cy=(cy1+cy2)/2
        cw_svg = f"""
  <rect x="{cx1:.1f}" y="{cy1:.1f}" width="{cx2-cx1:.1f}" height="{cy2-cy1:.1f}"
        fill="#FEE2E2" stroke="#DC2626" stroke-width="1.5"/>
  <text x="{cw_cx:.1f}" y="{cw_cy:.1f}" text-anchor="middle" dominant-baseline="central"
        font-size="11" font-weight="bold" fill="#DC2626">CW</text>"""

    # Tarama çizgileri (kabin içi)
    tarama = ""
    adim = max(12, px(100))
    n = int((kbw + kbh) / adim) + 4
    for i in range(-2, n):
        x1t = kbx1 + i*adim; y1t = kby1
        x2t = kbx1;           y2t = kby1 + i*adim
        tarama += (f'<line x1="{x1t:.1f}" y1="{y1t:.1f}" '
                   f'x2="{x2t:.1f}" y2="{y2t:.1f}" '
                   f'stroke="#94A3B8" stroke-width="0.4" clip-path="url(#{clip_id})"/>')

    # Mekanizma kutu (kapı tarafı)
    mek_h = px(r["on_bosluk"])
    mek_svg = ""
    if mek_h > 4:
        mek_svg = f"""
  <rect x="{kbx1:.1f}" y="{MARGIN:.1f}" width="{kbw:.1f}" height="{mek_h:.1f}"
        fill="#DBEAFE" stroke="#3B82F6" stroke-width="0.8" stroke-dasharray="4 2"/>
  <text x="{(kbx1+kbx2)/2:.1f}" y="{MARGIN + mek_h/2:.1f}"
        text-anchor="middle" dominant-baseline="central"
        font-size="9" fill="#1D4ED8">{r["mek"]}</text>"""

    svg = f"""<svg width="100%" viewBox="0 0 {SVG_W} {SVG_H}"
     xmlns="http://www.w3.org/2000/svg">
<defs>
  <clipPath id="{clip_id}">
    <rect x="{kbx1:.1f}" y="{kby1:.1f}" width="{kbw:.1f}" height="{kbh:.1f}"/>
  </clipPath>
</defs>

<!-- Kuyu arka plan -->
<rect x="{MARGIN}" y="{MARGIN}" width="{kw:.1f}" height="{kh:.1f}"
      fill="#F1F5F9" stroke="#1E293B" stroke-width="3"/>

<!-- Kabin arka plan -->
<rect x="{kbx1:.1f}" y="{kby1:.1f}" width="{kbw:.1f}" height="{kbh:.1f}" fill="white"/>
{tarama}

<!-- Kabin çerçeve -->
<rect x="{kbx1:.1f}" y="{kby1:.1f}" width="{kbw:.1f}" height="{kbh:.1f}"
      fill="none" stroke="#1E293B" stroke-width="1.8"/>

<!-- Kabin etiketi -->
<text x="{(kbx1+kbx2)/2:.1f}" y="{(kby1+kby2)/2:.1f}"
      text-anchor="middle" dominant-baseline="central"
      font-size="14" font-weight="600" fill="#334155">kabin</text>
<text x="{(kbx1+kbx2)/2:.1f}" y="{(kby1+kby2)/2+16:.1f}"
      text-anchor="middle" dominant-baseline="central"
      font-size="11" fill="#64748B">{r["kbg"]}×{r["kbd"]} mm</text>

<!-- Mekanizma alanı -->
{mek_svg}

<!-- CW -->
{cw_svg}

<!-- Ana raylar -->
<circle cx="{rsx:.1f}" cy="{rsy:.1f}" r="{rr:.1f}"
        fill="white" stroke="#1D4ED8" stroke-width="2"/>
<circle cx="{rsx:.1f}" cy="{rsy:.1f}" r="3" fill="#1D4ED8"/>
<circle cx="{rdx:.1f}" cy="{rdy:.1f}" r="{rr:.1f}"
        fill="white" stroke="#1D4ED8" stroke-width="2"/>
<circle cx="{rdx:.1f}" cy="{rdy:.1f}" r="3" fill="#1D4ED8"/>

<!-- Ray ekseni (kabin ağırlık merkezi hizası) -->
<line x1="{MARGIN:.1f}" y1="{rsy:.1f}" x2="{MARGIN+kw:.1f}" y2="{rsy:.1f}"
      stroke="#2563EB" stroke-width="1.0" stroke-dasharray="10 4" opacity="0.75"/>
<text x="{MARGIN+4:.1f}" y="{rsy-4:.1f}" font-size="9" fill="#2563EB">ağırlık merkezi</text>

<!-- ── ÖLÇÜLER ── -->
<!-- KyG -->
<line x1="{MARGIN:.1f}" y1="{MARGIN-20:.1f}" x2="{MARGIN+kw:.1f}" y2="{MARGIN-20:.1f}"
      stroke="#475569" stroke-width="0.8"/>
<line x1="{MARGIN:.1f}" y1="{MARGIN-26:.1f}" x2="{MARGIN:.1f}" y2="{MARGIN-14:.1f}"
      stroke="#475569" stroke-width="0.8"/>
<line x1="{MARGIN+kw:.1f}" y1="{MARGIN-26:.1f}" x2="{MARGIN+kw:.1f}" y2="{MARGIN-14:.1f}"
      stroke="#475569" stroke-width="0.8"/>
<text x="{MARGIN+kw/2:.1f}" y="{MARGIN-30:.1f}" text-anchor="middle"
      font-size="11" fill="#475569">KyG = {kyg} mm</text>

<!-- KyD -->
<line x1="{MARGIN+kw+20:.1f}" y1="{MARGIN:.1f}" x2="{MARGIN+kw+20:.1f}" y2="{MARGIN+kh:.1f}"
      stroke="#475569" stroke-width="0.8"/>
<line x1="{MARGIN+kw+14:.1f}" y1="{MARGIN:.1f}" x2="{MARGIN+kw+26:.1f}" y2="{MARGIN:.1f}"
      stroke="#475569" stroke-width="0.8"/>
<line x1="{MARGIN+kw+14:.1f}" y1="{MARGIN+kh:.1f}" x2="{MARGIN+kw+26:.1f}" y2="{MARGIN+kh:.1f}"
      stroke="#475569" stroke-width="0.8"/>
<text x="{MARGIN+kw+30:.1f}" y="{MARGIN+kh/2:.1f}" text-anchor="start"
      dominant-baseline="central" font-size="11" fill="#475569">KyD = {kyd} mm</text>

<!-- KbG -->
<line x1="{kbx1:.1f}" y1="{kby2+16:.1f}" x2="{kbx2:.1f}" y2="{kby2+16:.1f}"
      stroke="#059669" stroke-width="0.8"/>
<line x1="{kbx1:.1f}" y1="{kby2+10:.1f}" x2="{kbx1:.1f}" y2="{kby2+22:.1f}"
      stroke="#059669" stroke-width="0.8"/>
<line x1="{kbx2:.1f}" y1="{kby2+10:.1f}" x2="{kbx2:.1f}" y2="{kby2+22:.1f}"
      stroke="#059669" stroke-width="0.8"/>
<text x="{(kbx1+kbx2)/2:.1f}" y="{kby2+34:.1f}" text-anchor="middle"
      font-size="11" fill="#059669">KbG = {r["kbg"]} mm</text>

<!-- KbD -->
<line x1="{kbx1-16:.1f}" y1="{kby1:.1f}" x2="{kbx1-16:.1f}" y2="{kby2:.1f}"
      stroke="#059669" stroke-width="0.8"/>
<line x1="{kbx1-22:.1f}" y1="{kby1:.1f}" x2="{kbx1-10:.1f}" y2="{kby1:.1f}"
      stroke="#059669" stroke-width="0.8"/>
<line x1="{kbx1-22:.1f}" y1="{kby2:.1f}" x2="{kbx1-10:.1f}" y2="{kby2:.1f}"
      stroke="#059669" stroke-width="0.8"/>
<text x="{kbx1-26:.1f}" y="{(kby1+kby2)/2:.1f}" text-anchor="middle"
      dominant-baseline="central" font-size="11" fill="#059669"
      transform="rotate(-90,{kbx1-26:.1f},{(kby1+kby2)/2:.1f})">KbD = {r["kbd"]} mm</text>

<!-- Eksen etiketleri -->
<text x="{MARGIN+4:.1f}" y="{MARGIN-4:.1f}" font-size="9" fill="#94A3B8">x →</text>
<text x="{MARGIN-4:.1f}" y="{MARGIN+16:.1f}" font-size="9" fill="#94A3B8"
      transform="rotate(-90,{MARGIN-4:.1f},{MARGIN+16:.1f})">y ↓</text>
</svg>"""

    # st.markdown ile render için doğrudan svg string'i dönüyoruz
    return svg, SVG_H

def kapi_mekanizmasi_svg(mek_adi, kbg, ll, tmg):
    """
    Kabin genişliğine (kbg) orantılı olarak, şematik kapı mekanizması çizer.
    Sadece kapalı durumdaki panelleri gösterir.
    """
    SVG_W = 640
    SVG_H = 180
    MARGIN = 20
    
    olcek = (SVG_W - 2 * MARGIN) / kbg
    def px(mm): return mm * olcek
    
    # Kasa
    kabin_w_px = px(kbg)
    kabin_x = MARGIN + (SVG_W - 2*MARGIN - kabin_w_px)/2
    kasa_w_px = px(tmg)
    kasa_x = kabin_x + (kabin_w_px - kasa_w_px)/2
    
    svg_kasa = f"""
    <!-- Kasa / Kılavuz -->
    <rect x="{kasa_x:.1f}" y="40" width="{kasa_w_px:.1f}" height="70" fill="#F8FAFC" stroke="#94A3B8" stroke-width="1.5"/>
    <line x1="{kasa_x:.1f}" y1="75" x2="{kasa_x + kasa_w_px:.1f}" y2="75" stroke="#CBD5E1" stroke-width="1" stroke-dasharray="4 2"/>
    <text x="{SVG_W/2:.1f}" y="20" text-anchor="middle" font-size="14" font-weight="bold" fill="#1E293B">{mek_adi} (LL: {ll} mm, TMG: {tmg} mm)</text>
    <text x="{SVG_W/2:.1f}" y="135" text-anchor="middle" font-size="12" fill="#64748B">Kabin Genişliği (KbG): {kbg} mm</text>
    """
    
    panel_svg = ""
    panel_y = 48
    panel_h = 10
    panel_bosluk = 4
    
    merkez_x = SVG_W / 2
    giris_w_px = px(ll)
    
    if mek_adi == "Merkezi 2 panel":
        p_w = giris_w_px / 2 + 5
        panel_svg += f'<rect x="{merkez_x - p_w:.1f}" y="{panel_y:.1f}" width="{p_w:.1f}" height="{panel_h:.1f}" fill="#E2E8F0" stroke="#475569" stroke-width="1"/>'
        panel_svg += f'<rect x="{merkez_x:.1f}" y="{panel_y:.1f}" width="{p_w:.1f}" height="{panel_h:.1f}" fill="#E2E8F0" stroke="#475569" stroke-width="1"/>'
    
    elif mek_adi == "Merkezi 4 panel":
        p_w = giris_w_px / 4 + 5
        panel_svg += f'<rect x="{merkez_x - p_w:.1f}" y="{panel_y:.1f}" width="{p_w:.1f}" height="{panel_h:.1f}" fill="#E2E8F0" stroke="#475569" stroke-width="1"/>'
        panel_svg += f'<rect x="{merkez_x:.1f}" y="{panel_y:.1f}" width="{p_w:.1f}" height="{panel_h:.1f}" fill="#E2E8F0" stroke="#475569" stroke-width="1"/>'
        panel_svg += f'<rect x="{merkez_x - 2*p_w + 2:.1f}" y="{panel_y + panel_h + panel_bosluk:.1f}" width="{p_w:.1f}" height="{panel_h:.1f}" fill="#E2E8F0" stroke="#475569" stroke-width="1"/>'
        panel_svg += f'<rect x="{merkez_x + p_w - 2:.1f}" y="{panel_y + panel_h + panel_bosluk:.1f}" width="{p_w:.1f}" height="{panel_h:.1f}" fill="#E2E8F0" stroke="#475569" stroke-width="1"/>'
        
    elif mek_adi == "Teleskopik 2 panel":
        p_w = giris_w_px / 2 + 5
        sol_baslangic = merkez_x - giris_w_px / 2
        panel_svg += f'<rect x="{sol_baslangic:.1f}" y="{panel_y:.1f}" width="{p_w:.1f}" height="{panel_h:.1f}" fill="#E2E8F0" stroke="#475569" stroke-width="1"/>'
        panel_svg += f'<rect x="{sol_baslangic + p_w - 2:.1f}" y="{panel_y + panel_h + panel_bosluk:.1f}" width="{p_w:.1f}" height="{panel_h:.1f}" fill="#E2E8F0" stroke="#475569" stroke-width="1"/>'

    elif mek_adi == "Teleskopik 3 panel":
        p_w = giris_w_px / 3 + 5
        sol_baslangic = merkez_x - giris_w_px / 2
        for i in range(3):
            panel_svg += f'<rect x="{sol_baslangic + i*(p_w-2):.1f}" y="{panel_y + i*(panel_h + panel_bosluk):.1f}" width="{p_w:.1f}" height="{panel_h:.1f}" fill="#E2E8F0" stroke="#475569" stroke-width="1"/>'

    elif mek_adi == "Teleskopik 4 panel":
        p_w = giris_w_px / 4 + 5
        sol_baslangic = merkez_x - giris_w_px / 2
        for i in range(4):
            panel_svg += f'<rect x="{sol_baslangic + i*(p_w-2):.1f}" y="{panel_y + i*(panel_h + panel_bosluk):.1f}" width="{p_w:.1f}" height="{panel_h:.1f}" fill="#E2E8F0" stroke="#475569" stroke-width="1"/>'

    svg_html = f"""<svg width="100%" viewBox="0 0 {SVG_W} {SVG_H}" xmlns="http://www.w3.org/2000/svg">
{svg_kasa}
{panel_svg}
</svg>"""
    return svg_html, SVG_H

# ─────────────────────────────────────────────────────────────────
#  STREAMLIT ARAYÜZÜ
# ─────────────────────────────────────────────────────────────────
st.title("🛗 Asansör Sistem Seçici v2.0")
st.caption("EN 81-20/50 · 2014/33/EU · Ön değerlendirme aracı")

# ── Sidebar ──────────────────────────────────────────────────────
with st.sidebar:
    st.header("📐 Kuyu Ölçüleri")
    kyg = st.number_input("Kuyu Genişliği KyG (mm)", 800, 5000, 2000, 50)
    kyd = st.number_input("Kuyu Derinliği KyD (mm)", 800, 6000, 2200, 50)
    pit = st.number_input("Kuyu Dibi — Pit (mm)",    200, 3000, 1600, 50)
    kuyu_boy = st.number_input("Kuyu Toplam Boyu (mm)", 3000, 200000, 30000, 500)

    st.header("🏢 Proje")
    kat     = st.number_input("Kat Sayısı", 2, 150, 8, 1)
    kapasite= st.slider("Kapasite (kg)", 100, 5000, 800, 10)
    st.selectbox("Kullanım Amacı",
                 ["Konut","Ofis/Ticari","Hastane","Endüstriyel","Otel"])

    st.header("🎯 Tercihler")
    mr_sec  = st.selectbox("Makine Dairesi",
                ["Fark etmez","Makine dairesi yok (MRL)","Makine dairesi var (MR)"])
    st.select_slider("Bütçe", ["Ekonomik","Orta","Premium"], "Orta")
    deprem  = st.checkbox("Deprem Bölgesi (EN 81-77)")
    yangin  = st.checkbox("İtfaiyeci Asansörü (EN 81-72)")

mr_var = None
if "yok" in mr_sec:  mr_var = False
elif "var" in mr_sec: mr_var = True

# ── Hesapla ──────────────────────────────────────────────────────
seyir    = (kat - 1) * KAT_YUKSEKLIGI
overhead = kuyu_boy - pit - seyir

# Metrik satırı
c1,c2,c3,c4 = st.columns(4)
c1.metric("Seyir Yüksekliği", f"{seyir/1000:.1f} m")
c2.metric("Overhead (Hesaplanan)", f"{overhead} mm",
          delta="✓" if overhead > 0 else "✗ Yetersiz",
          delta_color="normal" if overhead > 0 else "inverse")
c3.metric("Pit", f"{pit} mm")

if overhead <= 0:
    st.error(f"Overhead negatif ({overhead} mm) — kuyu boyunu veya kat sayısını kontrol edin.")
    st.stop()

# Sistem filtrele
uygun = [s for s in SISTEMLER if
         s["kap_min"] <= kapasite <= s["kap_max"] and
         kat <= s["kat_max"] and
         pit >= s["pit_min"] and
         overhead >= s["oh_min"] and
         (mr_var is None or s["mr"] == mr_var)]

c4.metric("Uygun Sistem", len(uygun))

if not uygun:
    st.error("Girilen parametrelerle uyumlu sistem bulunamadı.")
    st.stop()

st.divider()

# ── Sistem sekmeleri ─────────────────────────────────────────────
tabs = st.tabs([s["ad"] for s in uygun])

for tab, sistem in zip(tabs, uygun):
    with tab:

        # Tüm kombinasyonları hesapla
        kombinasyonlar = tum_kombinasyonlari_hesapla(kyg, kyd, kapasite, sistem, seyir)

        if not kombinasyonlar:
            st.warning("Bu sistem için geçerli kombinasyon bulunamadı.")
            continue
        st.markdown("## 🏆 Önerilen Çözümler")

        ilk_uc = kombinasyonlar[:3]

        for sira, onerilen in enumerate(ilk_uc, start=1):

            emoji = {
                1: "🥇",
                2: "🥈",
                3: "🥉"
            }[sira]

            st.success(
                f"{emoji} #{sira} | "
                f"Puan: {onerilen['puan']} | "
                f"{onerilen['cw_konum']} CW | "
                f"{onerilen['mek']} | "
                f"LL={onerilen['ll']} mm | "
                f"KbG={onerilen['kbg']} mm | "
                f"KbD={onerilen['kbd']} mm | "
                f"{onerilen['ray_isim']}"
            )

        # ── Sonuç tablosu ────────────────────────────────────────
        st.markdown("#### 📋 Tüm Geçerli Kombinasyonlar")

        tablo = []
        for i, r in enumerate(kombinasyonlar):
            tablo.append({
                "#":           i+1,
                "CW Konum":    r["cw_konum"],
                "Mekanizma":   r["mek"],
                "Kapı (LL)":   f"{r['ll']} mm",
                "Hız (m/s)":   r["hiz"],
                "Ana Ray":     r["ray_isim"],
                "KbG (mm)":    r["kbg"],
                "KbD (mm)":    r["kbd"],
                "CW Durum":    r["cw_senaryo"],
                "Puan":        r["puan"],
            })

        st.dataframe(tablo, use_container_width=True, hide_index=True)

        # ── Kombinasyon seç & çizim ──────────────────────────────
        st.markdown("#### 📐 Üstten Görünüş Çizimi")

        secenekler = [
            f"#{i+1} | {r['cw_konum']} CW | {r['mek']} | Kapı LL={r['ll']}mm | {r['hiz']} m/s | "
            f"KbG={r['kbg']}mm KbD={r['kbd']}mm"
            for i, r in enumerate(kombinasyonlar)
        ]

        secim_idx = st.selectbox(
            "Görüntülenecek kombinasyonu seçin:",
            range(len(secenekler)),
            format_func=lambda i: secenekler[i],
            key=f"secim_{sistem['id']}"
        )

        r = kombinasyonlar[secim_idx]

        # CW mesajı
        if r["cw_konum"] == "Yandan":
            if r["cw_senaryo"] == "cakisiyor":
                st.info(f"ℹ️ {r['cw_mesaj']}")
            else:
                st.success(f"✅ {r['cw_mesaj']}")

        # SVG çizim — uid ile clipPath çakışmasını önle
        uid = f"{sistem['id']}_{secim_idx}"
        svg_html, svg_h = svg_ciz(r, kyg, kyd, uid=uid)
        svg_cleaned = svg_html.replace("\n", " ")
        st.markdown(f'<div align="center">{svg_cleaned}</div>', unsafe_allow_html=True)

        # Kapı mekanizması SVG'sini çizdir
        st.markdown("#### 🚪 Kapı Mekanizması — Üstten Görünüş")
        kapi_html, kapi_h = kapi_mekanizmasi_svg(r["mek"], r["kbg"], r["ll"], r["tmg"])
        kapi_cleaned = kapi_html.replace("\n", " ")
        st.markdown(f'<div align="center">{kapi_cleaned}</div>', unsafe_allow_html=True)

        # Özet kutucuklar
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Kabin Genişliği (KbG)", f"{r['kbg']} mm")
        col2.metric("Net Kapı (LL)", f"{r['ll']} mm")
        col3.metric("Ana Ray", r["ray_isim"])
        col4.metric("Hız", f"{r['hiz']} m/s")

        # ── Sistem detayları ─────────────────────────────────────
        with st.expander("ℹ️ Sistem Bilgileri"):
            ca, cb = st.columns(2)
            with ca:
                st.markdown("**✔ Avantajlar**")
                for av in sistem["avantajlar"]:
                    st.markdown(f"- {av}")
            with cb:
                st.markdown("**⚠ Dikkat**")
                for dez in sistem["dezavantajlar"]:
                    st.markdown(f"- {dez}")
            st.caption(f"Pit min: {sistem['pit_min']}mm | "
                      f"Overhead min: {sistem['oh_min']}mm | "
                      f"Maks kat: {sistem['kat_max']}")

# ── Notlar ───────────────────────────────────────────────────────
st.divider()
st.caption("⚠ Ön değerlendirme aracıdır. Kesin seçim için lisanslı mühendis onayı gerekir.")
if deprem: st.warning("⚠ Deprem bölgesi: EN 81-77 sismik gereksinimlerini inceleyin.")
if yangin: st.warning("⚠ İtfaiyeci asansörü: EN 81-72 kapsamında ayrı kuyu gerekir.")
