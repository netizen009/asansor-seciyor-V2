import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="Asansör Teknik Plan Seçici v3", page_icon="🛗", layout="wide")

# ─────────────────────────────────────────────────────────────────
#  SABİT DEĞERLER VE YENİ TEKNİK HESAP SABİTLERİ (Resim 0, 3'ten çıkarım)
# ─────────────────────────────────────────────────────────────────
KAT_YUKSEKLIGI     = 3000
KABIN_ARKA_BOSLUGU = 50
ARKADAN_CW_PAYI    = 300
CW_Y_BOYU          = 1380
CW_X_BOYU          = 150
CW_DUVAR_BOSLUGU   = 50
CW_CALISMA_BOSLUGU = 75
CW_B_MESAFE        = 300   # 50+150+100
UZAK_MONTE_MESAFE  = 310

# YENİ TEKNİK SABİTLER (HESAP İÇİN GEREKLİ):
PATEN_TEKNIK_GENISLIK = 140   # Resim 3'teki paten detayından (örnek değer)
PATEN_TEKNIK_DERINLIK = 120   # Paten kutu derinliği (örnek değer)
KABIN_PATEN_TOLERANS = 25     # Kabin kenarı ile paten kutusu arası tolerans (Resim 3: 25mm)
RAY_EKSEN_TOLERANS   = 5      # Paten merkezi ile ray ekseni arası tolerans (Resim 3'ten çıkarım)
# Kapı mekanizması derinlikleri (Resim 3: merkezi 2 panel için 170mm giriş derinliği)
KAPI_GIRIS_DERINLIK  = 170
# Effective Opening (EE) ve Clear Opening (PLW) arası fark (Örnek: EE = LL, PLW = LL + panel kapak payı, Resim 3: EE=740, PLW=1450)
EE_OFFSET = 0 # Şimdilik EE = LL varsayıyoruz.

# ─────────────────────────────────────────────────────────────────
#  TABLOLAR (Ray, Mekanizma, Sistem)
# ─────────────────────────────────────────────────────────────────
MEKANIZMA = {
    "Merkezi 2 panel":    {"on": 240, "derinlik": 170, "tmh_carpan": 2.0, "tmh_offset": 50},
    "Merkezi 4 panel":    {"on": 330, "derinlik": 210, "tmh_carpan": 1.5, "tmh_offset": 50},
    "Teleskopik 2 panel": {"on": 310, "derinlik": 180, "tmh_carpan": 1.5, "tmh_offset": 100},
    "Teleskopik 3 panel": {"on": 400, "derinlik": 220, "tmh_carpan": 1.33,"tmh_offset": 100},
    "Teleskopik 4 panel": {"on": 490, "derinlik": 250, "tmh_carpan": 1.25,"tmh_offset": 100},
}

ANA_RAY = [
    {"isim": "T50/A",  "taban": 50,  "kafa": 50,  "yukseklik": 50, "kap_max": 320,  "hiz_max": 1.0},
    {"isim": "T70/A",  "taban": 70,  "kafa": 65,  "yukseklik": 65, "kap_max": 630,  "hiz_max": 1.6},
    {"isim": "T89/B",  "taban": 89,  "kafa": 80,  "yukseklik": 80, "kap_max": 1000, "hiz_max": 2.5},
    {"isim": "T114/B", "taban": 114, "kafa": 90,  "yukseklik": 90, "kap_max": 2000, "hiz_max": 4.0},
    {"isim": "T127/B", "taban": 127, "kafa": 110, "yukseklik": 110,"kap_max": 5000, "hiz_max": 6.0},
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
#  HESAPLAMA FONKSİYONLARI (Geliştirilmiş Teknik Hesaplar)
# ─────────────────────────────────────────────────────────────────

def ray_sec(kapasite, hiz):
    for r in ANA_RAY:
        if kapasite <= r["kap_max"] and hiz <= r["hiz_max"]:
            return r
    return ANA_RAY[-1]

def cw_yandan_karar_v2(kyg, kyd, on_bosluk, ray_y_car, dbg_car, ray_taban_car):
    """
    Daha detaylı çakışma kontrolü ve DBG_CW hesabı.
    Döner: dict {... , 'dbg_cw': float, 'dbg_cw_x_min': float}
    """
    cw_alt_k_y = kyd - CW_CALISMA_BOSLUGU
    cw_ust_k_y = cw_alt_k_y - CW_Y_BOYU

    # Çakışma kontrolü: Ray kutusunun Y aralığı ile CW Y aralığı çakışıyor mu?
    # Resim 3'teki gibi, ray pateni kabin patenine göre daha dışarıda.
    ray_y_kutu_min = ray_y_car - (dbg_car / 2) - PATEN_TEKNIK_GENISLIK
    ray_y_kutu_max = ray_y_car + (dbg_car / 2) + PATEN_TEKNIK_GENISLIK

    y_cakisiyor = (cw_ust_k_y < ray_y_kutu_max) and (cw_alt_k_y > ray_y_kutu_min)

    # CW DBG hesabı (Resim 0 ve 3'teki gibi, CW ray eksenleri arası mesafe)
    # Varsayılan: CW'nin merkezi kuyu derinliğine göre ortalıdır.
    cw_y_merkez = (cw_ust_k_y + cw_alt_k_y) / 2
    # DBG_CW, CW'nin Y boyundan daha küçüktür (Resim 0'daki DBG ölçüsüne bak).
    dbg_cw = CW_Y_BOYU - 100 # Örnek: 1380 - 100 = 1280 (Resim 0 DBG)
    # CW ray kutusunun X'teki minimum konumu (kuyu sağ duvarından)
    cw_ray_x_kutu_min_to_wall = CW_DUVAR_BOSLUGU + RAY_EKSEN_TOLERANS # Duvar + Tolerans

    if y_cakisiyor:
        return {"gecerli": True, "senaryo": "cakisiyor",
                "cw_ust": cw_ust_k_y, "cw_alt": cw_alt_k_y,
                "dbg_cw": dbg_cw, "dbg_cw_x_min": cw_ray_x_kutu_min_to_wall,
                "mesaj": f"Ray kabin ağırlıkla çakışıyor → teknik inceleme gerekli"}
    else:
        return {"gecerli": True, "senaryo": "cakismiyor",
                "cw_ust": cw_ust_k_y, "cw_alt": cw_alt_k_y,
                "dbg_cw": dbg_cw, "dbg_cw_x_min": cw_ray_x_kutu_min_to_wall,
                "mesaj": "Ray çakışmıyor"}

def tum_kombinasyonlari_hesapla_v2(kyg, kyd, kapasite, sistem):
    sonuclar = []

    cw_konumlari = []
    if sistem["cw_yandan"]:   cw_konumlari.append("Yandan")
    if sistem["cw_arkadan"]:  cw_konumlari.append("Arkadan")

    for cw_konum in cw_konumlari:
        for mek_adi, mek in MEKANIZMA.items():
            on_bosluk = mek["on"]
            # Kabin arkadaki tolerans
            arka_bosluk = ARKADAN_CW_PAYI if cw_konum == "Arkadan" else KABIN_ARKA_BOSLUGU
            kbd = kyd - on_bosluk - arka_bosluk

            if kbd <= 400:   # minimum kabin derinliği
                continue

            # Kabin ağırlık merkezi (kuyu koordinatında)
            ray_y_car = on_bosluk + kbd / 2

            for hiz in sistem["hizlar"]:
                ray = ray_sec(kapasite, hiz)
                ray_taban = ray["taban"]

                # DBG_KABIN hesabı (Resim 3: Kabin Genişliği + 2x Tolerans)
                # Kuyu genişliği sınırlayıcı. Ray kutuları ve toleranslar çıkarılır.
                # Kuyu Sol Duvar -> Paten Kutusu Sol -> Kabin Sol -> Kabin Sağ -> Paten Kutusu Sağ -> Kuyu Sağ Duvar
                # (Duvar + Tolerans + Tolerans) + KbG + (Tolerans + Tolerans + CW/Duvar)
                
                # Minimum sol kenardan ray eksenine (Duvar + Tolerans + Paten/2 + Eksen/2)
                ray_x_sol_eksen = (ray_taban / 2) + KABIN_PATEN_TOLERANS + (PATEN_TEKNIK_GENISLIK/2) + RAY_EKSEN_TOLERANS

                # Kuyu genişliği sınırlamasına göre maksimum KbG
                kullanilabilir_w = kyg # Şimdilik CW tarafı hariç hesap
                if cw_konum == "Yandan":
                    # Kuyu sağından CW ve ray kutuları payı
                    # (Resim 3: CW_X + Toleranslar + Paten)
                    cw_payi_x = CW_DUVAR_BOSLUGU + CW_X_BOYU + KABIN_PATEN_TOLERANS + PATEN_TEKNIK_DERINLIK # Örnek hesap
                    kullanilabilir_w -= cw_payi_x

                # Maksimum KbG
                kbg_max = kullanilabilir_w - (ray_x_sol_eksen * 2) # Sol ve sağ toleranslar
                kbg_max = round(kbg_max)

                if kbg_max <= 400:  # minimum kabin genişliği
                    continue

                # Kapı (LL) ve Mekanizma Genişliği (TMG) Hesabı
                max_ll = kbg_max - 200
                if "3 panel" in mek_adi or "4 panel" in mek_adi:
                    uygun_ll_listesi = [ll for ll in [800, 900, 1000, 1100, 1200] if ll <= max_ll]
                else:
                    uygun_ll_listesi = [ll for ll in [700, 800, 900, 1000, 1100, 1200] if ll <= max_ll]
                
                if not uygun_ll_listesi:
                    continue
                    
                gecerli_ll_ve_tmg = []
                for secilen_ll in uygun_ll_listesi:
                    tmg = (secilen_ll * mek["tmh_carpan"]) + mek["tmh_offset"]
                    
                    # TMG kuyuya sığıyor mu? (mekanizmanın giriş derinliğine de bakmak lazım)
                    if tmg + 100 <= kyg: # TMG kuyu genişliğine sığıyor mu toleransla
                        gecerli_ll_ve_tmg.append((secilen_ll, tmg))
                        
                if not gecerli_ll_ve_tmg:
                    continue
                    
                # En büyükten başlayarak 3 adede kadar al
                gecerli_ll_ve_tmg.sort(key=lambda x: x[0], reverse=True)
                sinirli_ll_listesi = gecerli_ll_ve_tmg[:3]
                
                for secilen_ll, tmg in sinirli_ll_listesi:
                    # Clear Opening (PLW) (Örnek: PLW = LL + bir miktar kapak payı, Resim 3: LL=DW=900, EE=EE=740, PLW=SW=1450)
                    plw = secilen_ll + EE_OFFSET
                    ee = secilen_ll # Şimdilik EE = LL

                    # Teknik Hesaplar: DBG_KABIN, DBG_CW (Yandan ise)
                    dbg_kabin = kbg_max + (KABIN_PATEN_TOLERANS * 2) + RAY_EKSEN_TOLERANS * 2 # Örnek DBG hesabı
                    dbg_kabin = round(dbg_kabin)
                    
                    # CW teknik kararı
                    cw_karar = {}
                    if cw_konum == "Yandan":
                         cw_karar = cw_yandan_karar_v2(kyg, kyd, on_bosluk, ray_y_car, dbg_kabin, ray["taban"])
                         if not cw_karar["gecerli"]:
                             continue
                    else:
                        cw_karar = {"senaryo": "—", "mesaj": "Arkadan CW", "dbg_cw": None, "dbg_cw_x_min": None}

                    sonuclar.append({
                        "cw_konum":   cw_konum,
                        "mek":        mek_adi,
                        "hiz":        hiz,
                        "ray_isim":   ray["isim"],
                        "ray":        ray, # Tam ray objesi
                        "kbg":        kbg_max,
                        "kbd":        kbd,
                        "ray_y":      ray_y_car, # Kabin ray ekseni (Y'de kuyu merkezine göre)
                        "cw_info":    cw_karar,
                        "on_bosluk":  on_bosluk,
                        "ll":         secilen_ll,
                        "tmg":        tmg,
                        "ee":         ee,
                        "plw":        plw,
                        "dbg_car":    dbg_kabin,
                    })

    return sonuclar

# ─────────────────────────────────────────────────────────────────
#  SVG ÜST GÖRÜNÜŞ (Geliştirilmiş, Teknik, Dimensioned)
# ─────────────────────────────────────────────────────────────────

def svg_ciz_v3(r, kyg, kyd, uid="0"):
    """
    Örnek Resim 3'ü taklit eden, teknik, dimensioned üst görünüş.
    Component bazlı helper fonksiyonlar kullanır.
    """
    clip_id = f"cb_{uid}"
    SVG_W   = 1000 # Daha geniş, dimensionlar için
    MARGIN  = 80 # Daha fazla pay
    D_STYLE_TEXT_FILL = "#475569" # Dimension text color
    D_STYLE_LINE_STROKE = "#475569" # Dimension line color
    D_STYLE_TICK_SIZE = 6 # Dimension tick size
    
    olcek = min(
        (SVG_W - MARGIN * 2) / kyg,
        (SVG_W - MARGIN * 2) / kyd
    )

    def px(mm): return mm * olcek
    def sx(mm): return MARGIN + px(mm)   # kuyu koordinatından svg x'e
    def sy(mm): return MARGIN + px(mm)   # kuyu koordinatından svg y'ye

    kw = px(kyg)
    kh = px(kyd)
    SVG_H = int(kh + MARGIN * 2 + 50)

    kabin_w = px(r["kbg"])
    kabin_h = px(r["kbd"])
    
    # Kabin sol üst köşesi (X,Y)
    kb_x = sx(kyg / 2 - r["kbg"] / 2)
    if r["cw_konum"] == "Yandan":
        # Yandan CW varsa, kabin sola itilir
        ray_x_left_to_wall = r["ray"]["taban"]/2 + KABIN_PATEN_TOLERANS + PATEN_TEKNIK_GENISLIK/2 + RAY_EKSEN_TOLERANS
        kb_x = sx(ray_x_left_to_wall + KABIN_PATEN_TOLERANS + RAY_EKSEN_TOLERANS)
        
    kb_y = sy(r["on_bosluk"])

    # 1. HELPER: Draw Hoistway
    hoistway_svg = draw_hoistway(sx(0), sy(0), kw, kh, stroke_width=2.5)

    # 2. HELPER: Draw Car Assembly (Car, Guides)
    car_svg = draw_car_assembly(kb_x, kb_y, kabin_w, kabin_h, r["kbg"], r["kbd"], clip_id)

    # 3. HELPER: Draw Main Rails (Cross-section detailed)
    # Kabin ray eksenleri
    ray_x_sol = kb_x - px(KABIN_PATEN_TOLERANS + RAY_EKSEN_TOLERANS)
    ray_x_sag = ray_x_sol + px(r["dbg_car"])
    ray_y = sy(r["ray_y"]) # Kuyu coordinate, but we are in sx/sy space, need to be absolute

    rails_svg = draw_detailed_rails(ray_x_sol, ray_y, r["ray"]["kafa"], r["ray"]["taban"])
    rails_svg += draw_detailed_rails(ray_x_sag, ray_y, r["ray"]["kafa"], r["ray"]["taban"])
    
    # Guide lines (DBG_KABIN, Kabin merkezi)
    guide_lines_svg = f"""
  <line x1="{ray_x_sol:.1f}" y1="{sy(0):.1f}" x2="{ray_x_sag:.1f}" y2="{sy(0):.1f}" stroke="{D_STYLE_LINE_STROKE}" stroke-width="0.5" stroke-dasharray="10 4" opacity="0.5"/>
  <line x1="{kb_x + kabin_w/2:.1f}" y1="{sy(0):.1f}" x2="{kb_x + kabin_w/2:.1f}" y2="{sy(kyd):.1f}" stroke="{D_STYLE_LINE_STROKE}" stroke-width="0.5" stroke-dasharray="10 4" opacity="0.5"/>
"""

    # 4. HELPER: Draw Counterweight (if Yandan, detailed)
    cw_svg = ""
    if r["cw_konum"] == "Yandan":
        # CW merkezi kuyu merkezine göre
        cw_ray_x_sol_eksen = (kyg - CW_DUVAR_BOSLUGU) - (CW_X_BOYU / 2) # X merkezi toleranssız
        # Resim 0 ve 3'teki gibi, CW ray eksenleri arası mesafe (DBG_CW)
        dbg_cw = CW_Y_BOYU - 100 # Örnek DBG
        cw_ray_y_eksen_sol = r["cw_info"]["cw_ust"] + (CW_Y_BOYU - dbg_cw)/2 # Örnek Y merkezi
        
        # Draw CW body and rails
        cw_svg = draw_counterweight_assembly_v3(
            sx(cw_ray_x_sol_eksen), 
            sy(r["cw_info"]["cw_ust"] + CW_Y_BOYU/2),
            px(dbg_cw),
            px(CW_X_BOYU), 
            px(CW_Y_BOYU),
            r["ray"]["kafa"],
            r["ray"]["taban"]
        )
    elif r["cw_konum"] == "Arkadan":
        # Arkadan CW: daha geniş (CW_Y_BOYU), daha sığ (CW_X_BOYU)
        # Merkezi kuyu genişliğine göre ortalı
        # Merkezi kuyu derinliğine göre arkadan boslukta
        cw_svg = draw_counterweight_assembly_v3(
            sx(kyg / 2), 
            sy(kyd - (ARKADAN_CW_PAYI - CW_X_BOYU)/2 - CW_CALISMA_BOSLUGU), # Örnek Y merkezi
            px(CW_Y_BOYU - 100), # Örnek DBG
            px(CW_Y_BOYU),
            px(CW_X_BOYU), 
            r["ray"]["kafa"],
            r["ray"]["taban"],
            vertical=False # Arkadan CW yataydır
        )

    # 5. HELPER: Draw Door Mechanism (integrated detailed)
    door_svg = draw_door_mechanism_integrated_v3(
        kb_x + kabin_w/2, 
        kb_y, 
        kabin_w, 
        px(r["on_bosluk"]), 
        r["mek"], 
        r["kbg"], 
        r["ll"], 
        r["ee"], 
        r["plw"]
    )

    # 6. HELPER: Draw Dimension Lines (Geliştirilmiş, tick marklı)
    # Hoistway (SW/SD)
    dim_shaft_w = draw_dimension_line_tick(sx(0), sy(0), sx(kyg), sy(0), px(-60), f"SW = {kyg}", D_STYLE_TEXT_FILL, D_STYLE_LINE_STROKE, tick_size=D_STYLE_TICK_SIZE)
    dim_shaft_d = draw_dimension_line_tick(sx(kyg), sy(0), sx(kyg), sy(kyd), px(60), f"SD = {kyd}", D_STYLE_TEXT_FILL, D_STYLE_LINE_STROKE, tick_size=D_STYLE_TICK_SIZE)
    
    # Car (KbG/KbD)
    dim_car_w = draw_dimension_line_tick(kb_x, kb_y + kabin_h, kb_x + kabin_w, kb_y + kabin_h, px(60), f"KbG = {r['kbg']}", "#059669", "#059669", tick_size=D_STYLE_TICK_SIZE)
    dim_car_d = draw_dimension_line_tick(kb_x, kb_y, kb_x, kb_y + kabin_h, px(-60), f"KbD = {r['kbd']}", "#059669", "#059669", tick_size=D_STYLE_TICK_SIZE)

    # DBG (Car / CW if Yandan)
    dim_dbg_car = draw_dimension_line_tick(ray_x_sol, ray_y -px(50), ray_x_sag, ray_y - px(50), 0, f"DBG_K = {r['dbg_car']}", "#2563EB", "#2563EB", tick_size=D_STYLE_TICK_SIZE)
    
    # Clear Opening (PLW / EE) (Resim 3: PLW = SW gibi, EE = effective opening)
    dim_ee = draw_dimension_line_tick(kb_x + kabin_w/2 - px(r['ee'])/2, kb_y - px(r['on_bosluk']), kb_x + kabin_w/2 + px(r['ee'])/2, kb_y - px(r['on_bosluk']), px(-100), f"EE = {r['ee']}", D_STYLE_TEXT_FILL, D_STYLE_LINE_STROKE, tick_size=D_STYLE_TICK_SIZE)

    # Hoistway Sol ve Sağ Toleranslar (Resim 3: 470, 490)
    dim_side_L = draw_dimension_line_tick(sx(0), sy(r['ray_y']), ray_x_sol - px(PATEN_TEKNIK_GENISLIK/2 + RAY_EKSEN_TOLERANS), sy(r['ray_y']), px(-120), f"{round( (ray_x_sol - sx(0) - px(PATEN_TEKNIK_GENISLIK/2 + RAY_EKSEN_TOLERANS) ) / olcek)}", D_STYLE_TEXT_FILL, D_STYLE_LINE_STROKE, tick_size=D_STYLE_TICK_SIZE)

    svg = f"""<svg width="100%" viewBox="0 0 {SVG_W} {SVG_H}" xmlns="http://www.w3.org/2000/svg">
<defs>
  <clipPath id="{clip_id}">
    <rect x="{kb_x:.1f}" y="{kb_y:.1f}" width="{kabin_w:.1f}" height="{kabin_h:.1f}"/>
  </clipPath>
</defs>

{hoistway_svg}

{guide_lines_svg}

{car_svg}
{door_svg}

{cw_svg}

{rails_svg}

{dim_shaft_w}
{dim_shaft_d}
{dim_car_w}
{dim_car_d}
{dim_ee}
{dim_dbg_car}
{dim_side_L}

</svg>"""

    return svg, SVG_H

# ─────────────────────────────────────────────────────────────────
#  SVG HELPER FONKSİYONLARI (Teknik Detaylar ve Dimensions)
# ─────────────────────────────────────────────────────────────────

def draw_hoistway(x, y, w, h, stroke_width=2.0, fill="#F1F5F9", stroke="#1E293B"):
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'

def draw_car_assembly(x, y, w, h, mm_w, mm_h, clip_id, fill="white", stroke="#1E293B"):
    """Kabin gövdesi ve patenlerini çizer."""
    # Tarama çizgileri (kabin içi)
    tarama = ""
    adim = max(15, w/10) # KbG'ye orantılı adımlama
    n = int((w + h) / adim) + 4
    for i in range(-2, n):
        x1t = x + i*adim; y1t = y
        x2t = x;           y2t = y + i*adim
        tarama += (f'<line x1="{x1t:.1f}" y1="{y1t:.1f}" x2="{x2t:.1f}" y2="{y2t:.1f}" stroke="#94A3B8" stroke-width="0.3" clip-path="url(#{clip_id})"/>')

    # Kabin paten kutuları (Resim 3: her bir rayın yanında bir kutu)
    # Örnek paten kutusu boyutu (toleranslara orantılı)
    paten_w = PATEN_TEKNIK_GENISLIK * (w / mm_w) 
    paten_h = PATEN_TEKNIK_DERINLIK * (h / mm_h) 
    
    # Paten merkezi, tolerans ve eksen toleransından hesaplanır
    # Sol paten
    paten_L_x = x - paten_w - (KABIN_PATEN_TOLERANS * (w / mm_w))
    # Sağ paten
    paten_R_x = x + w + (KABIN_PATEN_TOLERANS * (w / mm_w))
    
    # Paten Y merkezi (Resim 3: paten kutusu kabin derinliğine göre daha geride)
    # Eksen toleransına bakarak hesap
    paten_y = y + h/2 - (paten_h/2) # Paten merkezi Y'de ortalı (Resim 3'ten çıkarım)

    paten_svg = f"""
  <rect x="{paten_L_x:.1f}" y="{paten_y:.1f}" width="{paten_w:.1f}" height="{paten_h:.1f}" fill="#E2E8F0" stroke="{stroke}" stroke-width="0.8"/>
  <rect x="{paten_R_x:.1f}" y="{paten_y:.1f}" width="{paten_w:.1f}" height="{paten_h:.1f}" fill="#E2E8F0" stroke="{stroke}" stroke-width="0.8"/>
"""

    return f"""
<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"/>
{tarama}
<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="none" stroke="{stroke}" stroke-width="1.8"/>
{paten_svg}
<text x="{x + w/2:.1f}" y="{y + h/2:.1f}" text-anchor="middle" dominant-baseline="central" font-size="14" font-weight="600" fill="#334155">Kabin</text>
<text x="{x + w/2:.1f}" y="{y + h/2 + 16:.1f}" text-anchor="middle" dominant-baseline="central" font-size="11" fill="#64748B">{mm_w}×{mm_h} mm</text>
"""

def draw_detailed_rails(x, y, kafa_mm, taban_mm, yukseklik_mm=80, stroke="#1D4ED8", fill="white"):
    """Rayın teknik kesitini çizer (circle değil). x,y: Eksen."""
    olcek_r = PATEN_TEKNIK_GENISLIK / 140 # Örnek paten toleransına göre ray ölçeği
    kafa_w = kafa_mm * olcek_r
    taban_w = taban_mm * olcek_r
    yuk_h = yukseklik_mm * olcek_r
    
    return f"""
  <line x1="{x - taban_w/2:.1f}" y1="{y:.1f}" x2="{x + taban_w/2:.1f}" y2="{y:.1f}" stroke="{stroke}" stroke-width="2.5"/>
  <line x1="{x:.1f}" y1="{y:.1f}" x2="{x:.1f}" y2="{y - yuk_h:.1f}" stroke="{stroke}" stroke-width="2.5"/>
  <rect x="{x - kafa_w/2:.1f}" y="{y - yuk_h - kafa_w/2:.1f}" width="{kafa_w:.1f}" height="{kafa_w:.1f}" fill="{stroke}" stroke="none"/>
"""

def draw_counterweight_assembly_v3(cw_ray_x_sol_eksen_px, cw_y_merkez_px, dbg_cw_px, taban_cw_w_px, taban_cw_h_px, kafa_mm, taban_mm, vertical=True, fill="#FEE2E2", stroke="#DC2626"):
    """
    Detailed CW assembly: Body, weights, and detailed rails.
    x,y_merkez: CW ray eksenleri merkezi. dbg_cw: Eksenler arası mesafe. taban_cw_w, taban_cw_h: CW taban boyutu. vertical: Yandan CW dikey durur.
    """
    
    # CW Body and Rails based on verticality
    body_svg = ""
    rails_svg = ""
    
    if vertical:
        # CW Body is vertical (for Yandan CW)
        body_svg = f"""
  <rect x="{cw_ray_x_sol_eksen_px - taban_cw_w_px/2:.1f}" y="{cw_y_merkez_px - taban_cw_h_px/2:.1f}" width="{taban_cw_w_px:.1f}" height="{taban_cw_h_px:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>
  <text x="{cw_ray_x_sol_eksen_px:.1f}" y="{cw_y_merkez_px:.1f}" text-anchor="middle" dominant-baseline="central" font-size="11" font-weight="bold" fill="{stroke}">CW</text>
  <line x1="{cw_ray_x_sol_eksen_px:.1f}" y1="{cw_y_merkez_px - taban_cw_h_px/2:.1f}" x2="{cw_ray_x_sol_eksen_px:.1f}" y2="{cw_y_merkez_px + taban_cw_h_px/2:.1f}" stroke="{stroke}" stroke-width="0.5" stroke-dasharray="3 2"/>
"""
        # CW rails based on DBG_CW and body centre
        rails_svg = draw_detailed_rails(cw_ray_x_sol_eksen_px, cw_y_merkez_px - dbg_cw_px/2, kafa_mm, taban_mm, yukseklik_mm=50, stroke=stroke)
        rails_svg += draw_detailed_rails(cw_ray_x_sol_eksen_px, cw_y_merkez_px + dbg_cw_px/2, kafa_mm, taban_mm, yukseklik_mm=50, stroke=stroke)

    else:
        # CW Body is horizontal (for Arkadan CW)
        body_svg = f"""
  <rect x="{cw_ray_x_sol_eksen_px - taban_cw_h_px/2:.1f}" y="{cw_y_merkez_px - taban_cw_w_px/2:.1f}" width="{taban_cw_h_px:.1f}" height="{taban_cw_w_px:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>
  <text x="{cw_ray_x_sol_eksen_px:.1f}" y="{cw_y_merkez_px:.1f}" text-anchor="middle" dominant-baseline="central" font-size="11" font-weight="bold" fill="{stroke}">CW</text>
"""
        # CW rails based on DBG_CW (X ekseninde fark) and body centre
        rails_svg = draw_detailed_rails(cw_ray_x_sol_eksen_px - dbg_cw_px/2, cw_y_merkez_px, kafa_mm, taban_mm, yukseklik_mm=50, stroke=stroke)
        rails_svg += draw_detailed_rails(cw_ray_x_sol_eksen_px + dbg_cw_px/2, cw_y_merkez_px, kafa_mm, taban_mm, yukseklik_mm=50, stroke=stroke)

    return f"""
{body_svg}
{rails_svg}
"""

def draw_door_mechanism_integrated_v3(car_w_px_centre, car_y_px, car_w_px, on_bosluk_px, mek_adi, kbg, ll, ee, plw, stroke="#3B82F6", fill="#DBEAFE"):
    """Kabin gövdesine entegre, detaylı kapı mekanizmasını çizer (Resim 3: Teleskopik 2 panel gibi)."""
    
    # Mechanism and Door Panel svg
    mek_svg = ""
    panel_svg = ""
    
    # 1. HELPER: Draw Panel Mechanism Box
    mek_svg = draw_hoistway(
        car_w_px_centre - car_w_px/2, 
        car_y_px - on_bosluk_px, 
        car_w_px, 
        on_bosluk_px, 
        stroke_width=0.8, fill=fill, stroke=stroke)
    mek_svg += f'<text x="{car_w_px_centre:.1f}" y="{car_y_px - on_bosluk_px/2:.1f}" text-anchor="middle" dominant-baseline="central" font-size="9" fill="#1D4ED8">{mek_adi}</text>'

    # 2. HELPER: Draw Door Panels and Entrance Opening (EE / PLW)
    ee_px = car_w_px * (ee / kbg) 
    plw_px = car_w_px * (plw / kbg)
    panel_y = car_y_px - on_bosluk_px + px(KAPI_GIRIS_DERINLIK) - px(10) # Örnek Y konumu mekanizma kutusu içinde
    
    # Entrance/Effective Opening Lines (Resim 3: EE toleransı)
    ee_start_px = car_w_px_centre - ee_px/2
    ee_end_px = car_w_px_centre + ee_px/2

    panel_svg = f"""
  <line x1="{ee_start_px:.1f}" y1="{panel_y - px(10):.1f}" x2="{ee_start_px:.1f}" y2="{panel_y + px(10):.1f}" stroke="#CBD5E1" stroke-width="1.0" stroke-dasharray="4 2"/>
  <line x1="{ee_end_px:.1f}" y1="{panel_y - px(10):.1f}" x2="{ee_end_px:.1f}" y2="{panel_y + px(10):.1f}" stroke="#CBD5E1" stroke-width="1.0" stroke-dasharray="4 2"/>
"""

    if mek_adi == "Merkezi 2 panel":
        # Merkezi 2 panel: 2 panel ortada çakışır
        panel_w = ee_px / 2 + px(5) # Panel genişliği overlappingtoleransıyla
        panel_svg += f'<rect x="{car_w_px_centre - panel_w:.1f}" y="{panel_y:.1f}" width="{panel_w:.1f}" height="{px(10):.1f}" fill="#E2E8F0" stroke="#475569" stroke-width="1"/>'
        panel_svg += f'<rect x="{car_w_px_centre:.1f}" y="{panel_y:.1f}" width="{panel_w:.1f}" height="{px(10):.1f}" fill="#E2E8F0" stroke="#475569" stroke-width="1"/>'

    elif mek_adi == "Teleskopik 2 panel":
        # Teleskopik 2 panel (Resim 3 taklidi): 2 panel bir kenarda çakışır, ee_px'den daha geniştirler
        # Paneller plw_px toleransından hesaplanır
        panel_w = ee_px / 2 + px(10) # Panel genişliği toleransla
        sol_baslangic = car_w_px_centre - plw_px / 2
        # Sol kenarda çakışan 2 panel
        panel_svg += f'<rect x="{sol_baslangic:.1f}" y="{panel_y:.1f}" width="{panel_w:.1f}" height="{px(10):.1f}" fill="#E2E8F0" stroke="#475569" stroke-width="1"/>'
        panel_svg += f'<rect x="{sol_baslangic + panel_w - px(2):.1f}" y="{panel_y + px(10) + px(4):.1f}" width="{panel_w:.1f}" height="{px(10):.1f}" fill="#E2E8F0" stroke="#475569" stroke-width="1"/>'

    else:
        # Şimdilik diğerleri basit tarama
        panel_svg += f'<line x1="{ee_start_px:.1f}" y1="{panel_y:.1f}" x2="{ee_end_px:.1f}" y2="{panel_y:.1f}" stroke="#DC2626" stroke-width="2.0" stroke-dasharray="5 5" opacity="0.5"/>'

    return f"""
{mek_svg}
{panel_svg}
"""

def draw_dimension_line_tick(x1, y1, x2, y2, offset, label, text_fill, stroke, horizontal=True, tick_size=6):
    """Geliştirilmiş, tick marklı (arrows değil) dimension line."""
    
    # Dimension line points based on offset and direction
    lx1 = x1; ly1 = y1
    lx2 = x2; ly2 = y2
    if offset != 0:
        if horizontal:
            ly1 += offset; ly2 += offset
        else:
            lx1 += offset; lx2 += offset
            
    # Tick mark points (tick mark size is fixed in px)
    tick1_start = (lx1 - tick_size/2, ly1 + tick_size/2) if horizontal else (lx1 - tick_size/2, ly1 - tick_size/2)
    tick1_end = (lx1 + tick_size/2, ly1 - tick_size/2) if horizontal else (lx1 + tick_size/2, ly1 + tick_size/2)
    
    tick2_start = (lx2 - tick_size/2, ly2 + tick_size/2) if horizontal else (lx2 - tick_size/2, ly2 - tick_size/2)
    tick2_end = (lx2 + tick_size/2, ly2 - tick_size/2) if horizontal else (lx2 + tick_size/2, ly2 + tick_size/2)

    return f"""
  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{lx1:.1f}" y2="{ly1:.1f}" stroke="{stroke}" stroke-width="0.5" opacity="0.5"/>
  <line x1="{x2:.1f}" y1="{y2:.1f}" x2="{lx2:.1f}" y2="{ly2:.1f}" stroke="{stroke}" stroke-width="0.5" opacity="0.5"/>
  <line x1="{lx1:.1f}" y1="{ly1:.1f}" x2="{lx2:.1f}" y2="{ly2:.1f}" stroke="{stroke}" stroke-width="0.8"/>
  <line x1="{tick1_start[0]:.1f}" y1="{tick1_start[1]:.1f}" x2="{tick1_end[0]:.1f}" y2="{tick1_end[1]:.1f}" stroke="{stroke}" stroke-width="0.8"/>
  <line x1="{tick2_start[0]:.1f}" y1="{tick2_start[1]:.1f}" x2="{tick2_end[0]:.1f}" y2="{tick2_end[1]:.1f}" stroke="{stroke}" stroke-width="0.8"/>
  <text x="{(lx1+lx2)/2:.1f}" y="{(ly1+ly2)/2:.1f}" text-anchor="middle" dominant-baseline="central" font-size="11" fill="{text_fill}" transform="rotate({-90 if not horizontal else 0}, {(lx1+lx2)/2:.1f}, {(ly1+ly2)/2:.1f})">{label}</text>
"""

# ─────────────────────────────────────────────────────────────────
#  MAIN STREAMLIT UI (Geliştirilmiş, Teknik Metrics)
# ─────────────────────────────────────────────────────────────────
st.title("🛗 Asansör Teknik Plan Seçici v3.0")
st.caption("EN 81-20/50 · 2014/33/EU · Ön değerlendirme ve Teknik Plan aracı")

# ── Sidebar (Kuyu ve Proje Parametreleri) ─────────────────────────
with st.sidebar:
    st.header("📐 Kuyu Ölçüleri (Shaft)")
    kyg = st.number_input("Kuyu Genişliği KyG-SW (mm)", 800, 5000, 2000, 50)
    kyd = st.number_input("Kuyu Derinliği KyD-SD (mm)", 800, 6000, 2200, 50)
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

# ── Hesapla (Hesaplanan ve Kontrol Edilen Parametreler) ────────────
seyir    = (kat - 1) * KAT_YUKSEKLIGI
overhead = kuyu_boy - pit - seyir

# Metrik satırı (Geliştirilmiş, Teknik Kısaltmalar)
c1,c2,c3,c4 = st.columns(4)
c1.metric("Seyir Yüksekliği", f"{seyir/1000:.1f} m")
c2.metric("Overhead (Hesp.)", f"{overhead} mm",
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

# ── Sistem sekmeleri (Hesaplanan Kombinasyonlar) ─────────────────
tabs = st.tabs([s["ad"] for s in uygun])

for tab, sistem in zip(tabs, uygun):
    with tab:

        # Tüm kombinasyonları hesapla (Geliştirilmiş V2)
        kombinasyonlar = tum_kombinasyonlari_hesapla_v2(kyg, kyd, kapasite, sistem)

        if not kombinasyonlar:
            st.warning("Bu sistem için geçerli kombinasyon bulunamadı.")
            continue

        # ── Sonuç tablosu ────────────────────────────────────────
        st.markdown("#### 📋 Tüm Geçerli Teknik Kombinasyonlar")

        tablo = []
        for i, r in enumerate(kombinasyonlar):
            tablo.append({
                "#":           i+1,
                "CW":          r["cw_konum"],
                "Mekanizma":   r["mek"],
                "Kapı-DW (mm)":f"{r['ll']}",
                "EE (mm)":     f"{r['ee']}",
                "PLW (mm)":    f"{r['plw']}",
                "Hız (m/s)":   r["hiz"],
                "Ana Ray":     r["ray_isim"],
                "KbG-W (mm)":  r["kbg"],
                "KbD-D (mm)":  r["kbd"],
                "DBG_K (mm)":  r["dbg_car"],
                "CW Durum":    r["cw_info"]["senaryo"],
            })

        st.dataframe(tablo, use_container_width=True, hide_index=True)

        # ── Kombinasyon seç & çizim ──────────────────────────────
        st.markdown("#### 📐 Teknik Üst Görünüş Çizimi (Dimensioned Plan)")

        secenekler = [
            f"#{i+1} | {r['cw_konum']} CW | {r['mek']} | DW={r['ll']}mm EE={r['ee']}mm | "
            f"KbG={r['kbg']}mm KbD={r['kbd']}mm DBG_K={r['dbg_car']}mm"
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
            if r["cw_info"]["senaryo"] == "cakisiyor":
                st.info(f"ℹ️ {r['cw_info']['mesaj']}")
            else:
                st.success(f"✅ {r['cw_info']['mesaj']}")

        # SVG çizim (Geliştirilmiş V3)
        uid = f"{sistem['id']}_{secim_idx}"
        svg_html, svg_h = svg_ciz_v3(r, kyg, kyd, uid=uid)
        svg_cleaned = svg_html.replace("\n", " ")
        st.markdown(f'<div align="center">{svg_cleaned}</div>', unsafe_allow_html=True)

        # Teknik Metrics Satırı (Özet Teknik Bilgi)
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Kabin-W (KbG)", f"{r['kbg']} mm")
        col2.metric("Kabin-D (KbD)", f"{r['kbd']} mm")
        col3.metric("DBG_KABIN (K)", f"{r['dbg_car']} mm")
        col4.metric("Giriş EE", f"{r['ee']} mm")
        col5.metric("PLW Tolerans", f"{r['plw']} mm")

        # ── Sistem detayları (Avantajlar/Dezavantajlar) ─────────────
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
            st.caption(f"Pit min: {sistem['pit_min']}mm | Overhead min: {sistem['oh_min']}mm | Maks kat: {sistem['kat_max']}")

# ── Notlar ───────────────────────────────────────────────────────
st.divider()
st.caption("⚠ Ön değerlendirme ve Teknik Plan aracıdır. Kesin seçim için lisanslı mühendis onayı gerekir.")
if deprem: st.warning("⚠ Deprem bölgesi: EN 81-77 sismik gereksinimlerini inceleyin.")
if yangin: st.warning("⚠ İtfaiyeci asansörü: EN 81-72 kapsamında ayrı kuyu gerekir.")
