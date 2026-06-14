import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="Asansör Teknik Plan Seçici v3", page_icon="🛗", layout="wide")

# ─────────────────────────────────────────────────────────────────
#  SABİT DEĞERLER VE TEKNİK HESAP SABİTLERİ
# ─────────────────────────────────────────────────────────────────
KAT_YUKSEKLIGI     = 3000
KABIN_ARKA_BOSLUGU = 50
ARKADAN_CW_PAYI    = 300
CW_Y_BOYU          = 1380
CW_X_BOYU          = 150
CW_DUVAR_BOSLUGU   = 50
CW_CALISMA_BOSLUGU = 75
CW_B_MESAFE        = 300   
UZAK_MONTE_MESAFE  = 310

PATEN_TEKNIK_GENISLIK = 140   
PATEN_TEKNIK_DERINLIK = 120   
KABIN_PATEN_TOLERANS = 25     
RAY_EKSEN_TOLERANS   = 5      
KAPI_GIRIS_DERINLIK  = 170
EE_OFFSET = 0 

# ─────────────────────────────────────────────────────────────────
#  TABLOLAR
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
#  HESAPLAMA FONKSİYONLARI 
# ─────────────────────────────────────────────────────────────────

def ray_sec(kapasite, hiz):
    for r in ANA_RAY:
        if kapasite <= r["kap_max"] and hiz <= r["hiz_max"]:
            return r
    return ANA_RAY[-1]

def cw_yandan_karar_v2(kyg, kyd, on_bosluk, ray_y_car, dbg_car, ray_taban_car):
    cw_alt_k_y = kyd - CW_CALISMA_BOSLUGU
    cw_ust_k_y = cw_alt_k_y - CW_Y_BOYU

    ray_y_kutu_min = ray_y_car - (dbg_car / 2) - PATEN_TEKNIK_GENISLIK
    ray_y_kutu_max = ray_y_car + (dbg_car / 2) + PATEN_TEKNIK_GENISLIK

    y_cakisiyor = (cw_ust_k_y < ray_y_kutu_max) and (cw_alt_k_y > ray_y_kutu_min)

    cw_y_merkez = (cw_ust_k_y + cw_alt_k_y) / 2
    dbg_cw = CW_Y_BOYU - 100 
    cw_ray_x_kutu_min_to_wall = CW_DUVAR_BOSLUGU + RAY_EKSEN_TOLERANS 

    if y_cakisiyor:
        return {"gecerli": True, "senaryo": "cakisiyor",
                "cw_ust": cw_ust_k_y, "cw_alt": cw_alt_k_y,
                "dbg_cw": dbg_cw, "dbg_cw_x_min": cw_ray_x_kutu_min_to_wall,
                "mesaj": "Ray kabin ağırlıkla çakışıyor → teknik inceleme gerekli"}
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
            arka_bosluk = ARKADAN_CW_PAYI if cw_konum == "Arkadan" else KABIN_ARKA_BOSLUGU
            kbd = kyd - on_bosluk - arka_bosluk

            if kbd <= 400:   
                continue

            ray_y_car = on_bosluk + kbd / 2

            for hiz in sistem["hizlar"]:
                ray = ray_sec(kapasite, hiz)
                ray_taban = ray["taban"]

                ray_x_sol_eksen = (ray_taban / 2) + KABIN_PATEN_TOLERANS + (PATEN_TEKNIK_GENISLIK/2) + RAY_EKSEN_TOLERANS

                kullanilabilir_w = kyg 
                if cw_konum == "Yandan":
                    cw_payi_x = CW_DUVAR_BOSLUGU + CW_X_BOYU + KABIN_PATEN_TOLERANS + PATEN_TEKNIK_DERINLIK 
                    kullanilabilir_w -= cw_payi_x

                kbg_max = kullanilabilir_w - (ray_x_sol_eksen * 2) 
                kbg_max = round(kbg_max)

                if kbg_max <= 400:  
                    continue

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
                    if tmg + 100 <= kyg: 
                        gecerli_ll_ve_tmg.append((secilen_ll, tmg))
                        
                if not gecerli_ll_ve_tmg:
                    continue
                    
                gecerli_ll_ve_tmg.sort(key=lambda x: x[0], reverse=True)
                sinirli_ll_listesi = gecerli_ll_ve_tmg[:3]
                
                for secilen_ll, tmg in sinirli_ll_listesi:
                    plw = secilen_ll + EE_OFFSET
                    ee = secilen_ll 

                    dbg_kabin = kbg_max + (KABIN_PATEN_TOLERANS * 2) + RAY_EKSEN_TOLERANS * 2 
                    dbg_kabin = round(dbg_kabin)
                    
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
                        "ray":        ray, 
                        "kbg":        kbg_max,
                        "kbd":        kbd,
                        "ray_y":      ray_y_car, 
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
#  SVG ÜST GÖRÜNÜŞ (Teknik, Boyutlandırılmış)
# ─────────────────────────────────────────────────────────────────

def svg_ciz_v3(r, kyg, kyd, uid="0"):
    clip_id = f"cb_{uid}"
    SVG_W   = 1000 
    MARGIN  = 80 
    D_STYLE_TEXT_FILL = "#475569" 
    D_STYLE_LINE_STROKE = "#475569" 
    D_STYLE_TICK_SIZE = 6 
    
    olcek = min((SVG_W - MARGIN * 2) / kyg, (SVG_W - MARGIN * 2) / kyd)

    def px(mm): return mm * olcek
    def sx(mm): return MARGIN + px(mm)   
    def sy(mm): return MARGIN + px(mm)   

    kw = px(kyg)
    kh = px(kyd)
    SVG_H = int(kh + MARGIN * 2 + 50)

    kabin_w = px(r["kbg"])
    kabin_h = px(r["kbd"])
    
    kb_x = sx(kyg / 2 - r["kbg"] / 2)
    if r["cw_konum"] == "Yandan":
        ray_x_left_to_wall = r["ray"]["taban"]/2 + KABIN_PATEN_TOLERANS + PATEN_TEKNIK_GENISLIK/2 + RAY_EKSEN_TOLERANS
        kb_x = sx(ray_x_left_to_wall + KABIN_PATEN_TOLERANS + RAY_EKSEN_TOLERANS)
        
    kb_y = sy(r["on_bosluk"])

    hoistway_svg = draw_hoistway(sx(0), sy(0), kw, kh, stroke_width=2.5)
    car_svg = draw_car_assembly(kb_x, kb_y, kabin_w, kabin_h, r["kbg"], r["kbd"], clip_id)

    ray_x_sol = kb_x - px(KABIN_PATEN_TOLERANS + RAY_EKSEN_TOLERANS)
    ray_x_sag = ray_x_sol + px(r["dbg_car"])
    ray_y = sy(r["ray_y"]) 

    rails_svg = draw_detailed_rails(ray_x_sol, ray_y, r["ray"]["kafa"], r["ray"]["taban"])
    rails_svg += draw_detailed_rails(ray_x_sag, ray_y, r["ray"]["kafa"], r["ray"]["taban"])
    
    guide_lines_svg = f"""
  <line x1="{ray_x_sol:.1f}" y1="{sy(0):.1f}" x2="{ray_x_sag:.1f}" y2="{sy(0):.1f}" stroke="{D_STYLE_LINE_STROKE}" stroke-width="0.5" stroke-dasharray="10 4" opacity="0.5"/>
  <line x1="{kb_x + kabin_w/2:.1f}" y1="{sy(0):.1f}" x2="{kb_x + kabin_w/2:.1f}" y2="{sy(kyd):.1f}" stroke="{D_STYLE_LINE_STROKE}" stroke-width="0.5" stroke-dasharray="10 4" opacity="0.5"/>
"""

    cw_svg = ""
    if r["cw_konum"] == "Yandan":
        cw_ray_x_sol_eksen = (kyg - CW_DUVAR_BOSLUGU) - (CW_X_BOYU / 2) 
        dbg_cw = CW_Y_BOYU - 100 
        
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
        cw_svg = draw_counterweight_assembly_v3(
            sx(kyg / 2), 
            sy(kyd - (ARKADAN_CW_PAYI - CW_X_BOYU)/2 - CW_CALISMA_BOSLUGU), 
            px(CW_Y_BOYU - 100), 
            px(CW_Y_BOYU),
            px(CW_X_BOYU), 
            r["ray"]["kafa"],
            r["ray"]["taban"],
            vertical=False 
        )

    door_svg = draw_door_mechanism_integrated_v3(
        kb_x + kabin_w/2, kb_y, kabin_w, px(r["on_bosluk"]), 
        r["mek"], r["kbg"], r["ll"], r["ee"], r["plw"]
    )

    dim_shaft_w = draw_dimension_line_tick(sx(0), sy(0), sx(kyg), sy(0), px(-60), f"SW = {kyg}", D_STYLE_TEXT_FILL, D_STYLE_LINE_STROKE, tick_size=D_STYLE_TICK_SIZE)
    dim_shaft_d = draw_dimension_line_tick(sx(kyg), sy(0), sx(kyg), sy(kyd), px(60), f"SD = {kyd}", D_STYLE_TEXT_FILL, D_STYLE_LINE_STROKE, tick_size=D_STYLE_TICK_SIZE)
    dim_car_w = draw_dimension_line_tick(kb_x, kb_y + kabin_h, kb_x + kabin_w, kb_y + kabin_h, px(60), f"KbG = {r['kbg']}", "#059669", "#059669", tick_size=D_STYLE_TICK_SIZE)
    dim_car_d = draw_dimension_line_tick(kb_x, kb_y, kb_x, kb_y + kabin_h, px(-60), f"KbD = {r['kbd']}", "#059669", "#059669", tick_size=D_STYLE_TICK_SIZE)
    dim_dbg_car = draw_dimension_line_tick(ray_x_sol, ray_y -px(50), ray_x_sag, ray_y - px(50), 0, f"DBG_K = {r['dbg_car']}", "#2563EB", "#2563EB", tick_size=D_STYLE_TICK_SIZE)
    dim_ee = draw_dimension_line_tick(kb_x + kabin_w/2 - px(r['ee'])/2, kb_y - px(r['on_bosluk']), kb_x + kabin_w/2 + px(r['ee'])/2, kb_y - px(r['on_bosluk']), px(-100), f"EE = {r['ee']}", D_STYLE_TEXT_FILL, D_STYLE_LINE_STROKE, tick_size=D_STYLE_TICK_SIZE)
    
    hesaplanan_L = round((ray_x_sol - sx(0) - px(PATEN_TEKNIK_GENISLIK/2 + RAY_EKSEN_TOLERANS)) / olcek)
    dim_side_L = draw_dimension_line_tick(sx(0), sy(r['ray_y']), ray_x_sol - px(PATEN_TEKNIK_GENISLIK/2 + RAY_EKSEN_TOLERANS), sy(r['ray_y']), px(-120), f"{hesaplanan_L}", D_STYLE_TEXT_FILL, D_STYLE_LINE_STROKE, tick_size=D_STYLE_TICK_SIZE)

    svg = f"""<svg width="100%" viewBox="0 0 {SVG_W} {SVG_H}" xmlns="http://www.w3.org/2000/svg">
<defs><clipPath id="{clip_id}"><rect x="{kb_x:.1f}" y="{kb_y:.1f}" width="{kabin_w:.1f}" height="{kabin_h:.1f}"/></clipPath></defs>
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
#  SVG HELPER FONKSİYONLARI 
# ─────────────────────────────────────────────────────────────────

def draw_hoistway(x, y, w, h, stroke_width=2.0, fill="#F1F5F9", stroke="#1E293B"):
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'

def draw_car_assembly(x, y, w, h, mm_w, mm_h, clip_id, fill="white", stroke="#1E293B"):
    tarama = ""
    adim = max(15, w/10) 
    n = int((w + h) / adim) + 4
    for i in range(-2, n):
        tarama += f'<line x1="{x + i*adim:.1f}" y1="{y:.1f}" x2="{x:.1f}" y2="{y + i*adim:.1f}" stroke="#94A3B8" stroke-width="0.3" clip-path="url(#{clip_id})"/>'

    paten_w = PATEN_TEKNIK_GENISLIK * (w / mm_w) 
    paten_h = PATEN_TEKNIK_DERINLIK * (h / mm_h) 
    paten_L_x = x - paten_w - (KABIN_PATEN_TOLERANS * (w / mm_w))
    paten_R_x = x + w + (KABIN_PATEN_TOLERANS * (w / mm_w))
    paten_y = y + h/2 - (paten_h/2) 

    paten_svg = f"""<rect x="{paten_L_x:.1f}" y="{paten_y:.1f}" width="{paten_w:.1f}" height="{paten_h:.1f}" fill="#E2E8F0" stroke="{stroke}" stroke-width="0.8"/>
                    <rect x="{paten_R_x:.1f}" y="{paten_y:.1f}" width="{paten_w:.1f}" height="{paten_h:.1f}" fill="#E2E8F0" stroke="{stroke}" stroke-width="0.8"/>"""

    return f"""<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"/>{tarama}
               <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="none" stroke="{stroke}" stroke-width="1.8"/>{paten_svg}
               <text x="{x + w/2:.1f}" y="{y + h/2:.1f}" text-anchor="middle" dominant-baseline="central" font-size="14" font-weight="600" fill="#334155">Kabin</text>
               <text x="{x + w/2:.1f}" y="{y + h/2 + 16:.1f}" text-anchor="middle" dominant-baseline="central" font-size="11" fill="#64748B">{mm_w}×{mm_h} mm</text>"""

def draw_detailed_rails(x, y, kafa_mm, taban_mm, yukseklik_mm=80, stroke="#1D4ED8", fill="white"):
    olcek_r = PATEN_TEKNIK_GENISLIK / 140 
    kafa_w = kafa_mm * olcek_r
    taban_w = taban_mm * olcek_r
    yuk_h = yukseklik_mm * olcek_r
    
    return f"""<line x1="{x - taban_w/2:.1f}" y1="{y:.1f}" x2="{x + taban_w/2:.1f}" y2="{y:.1f}" stroke="{stroke}" stroke-width="2.5"/>
               <line x1="{x:.1f}" y1="{y:.1f}" x2="{x:.1f}" y2="{y - yuk_h:.1f}" stroke="{stroke}" stroke-width="2.5"/>
               <rect x="{x - kafa_w/2:.1f}" y="{y - yuk_h - kafa_w/2:.1f}" width="{kafa_w:.1f}" height="{kafa_w:.1f}" fill="{stroke}" stroke="none"/>"""

def draw_counterweight_assembly_v3(cw_ray_x_sol_eksen_px, cw_y_merkez_px, dbg_cw_px, taban_cw_w_px, taban_cw_h_px, kafa_mm, taban_mm, vertical=True, fill="#FEE2E2", stroke="#DC2626"):
    body_svg = ""
    rails_svg = ""
    
    if vertical:
        body_svg = f"""<rect x="{cw_ray_x_sol_eksen_px - taban_cw_w_px/2:.1f}" y="{cw_y_merkez_px - taban_cw_h_px/2:.1f}" width="{taban_cw_w_px:.1f}" height="{taban_cw_h_px:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>
                       <text x="{cw_ray_x_sol_eksen_px:.1f}" y="{cw_y_merkez_px:.1f}" text-anchor="middle" dominant-baseline="central" font-size="11" font-weight="bold" fill="{stroke}">CW</text>
                       <line x1="{cw_ray_x_sol_eksen_px:.1f}" y1="{cw_y_merkez_px - taban_cw_h_px/2:.1f}" x2="{cw_ray_x_sol_eksen_px:.1f}" y2="{cw_y_merkez_px + taban_cw_h_px/2:.1f}" stroke="{stroke}" stroke-width="0.5" stroke-dasharray="3 2"/>"""
        rails_svg = draw_detailed_rails(cw_ray_x_sol_eksen_px, cw_y_merkez_px - dbg_cw_px/2, kafa_mm, taban_mm, yukseklik_mm=50, stroke=stroke)
        rails_svg += draw_detailed_rails(cw_ray_x_sol_eksen_px, cw_y_merkez_px + dbg_cw_px/2, kafa_mm, taban_mm, yukseklik_mm=50, stroke=stroke)
    else:
        body_svg = f"""<rect x="{cw_ray_x_sol_eksen_px - taban_cw_h_px/2:.1f}" y="{cw_y_merkez_px - taban_cw_w_px/2:.1f}" width="{taban_cw_h_px:.1f}" height="{taban_cw_w_px:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>
                       <text x="{cw_ray_x_sol_eksen_px:.1f}" y="{cw_y_merkez_px:.1f}" text-anchor="middle" dominant-baseline="central" font-size="11" font-weight="bold" fill="{stroke}">CW</text>"""
        rails_svg = draw_detailed_rails(cw_ray_x_sol_eksen_px - dbg_cw_px/2, cw_y_merkez_px, kafa_mm, taban_mm, yukseklik_mm=50, stroke=stroke)
        rails_svg += draw_detailed_rails(cw_ray_x_sol_eksen_px + dbg_cw_px/2, cw_y_merkez_px, kafa_mm, taban_mm, yukseklik_mm=50, stroke=stroke)

    return body_svg + rails_svg

def draw_door_mechanism_integrated_v3(car_w_px_centre, car_y_px, car_w_px, on_bosluk_px, mek_adi, kbg, ll, ee, plw, stroke="#3B82F6", fill="#DBEAFE"):
    mek_svg = draw_hoistway(car_w_px_centre - car_w_px/2, car_y_px - on_bosluk_px, car_w_px, on_bosluk_px, stroke_width=0.8, fill=fill, stroke=stroke)
    mek_svg += f'<text x="{car_w_px_centre:.1f}" y="{car_y_px - on_bosluk_px/2:.1f}" text-anchor="middle" dominant-baseline="central" font-size="9" fill="#1D4ED8">{mek_adi}</text>'

    ee_px = car_w_px * (ee / kbg) 
    plw_px = car_w_px * (plw / kbg)
    panel_y = car_y_px - on_bosluk_px + (170 * (car_w_px/kbg)) - 10 
    
    ee_start_px = car_w_px_centre - ee_px/2
    ee_end_px = car_w_px_centre + ee_px/2

    panel_svg = f"""<line x1="{ee_start_px:.1f}" y1="{panel_y - 10:.1f}" x2="{ee_start_px:.1f}" y2="{panel_y + 10:.1f}" stroke="#CBD5E1" stroke-width="1.0" stroke-dasharray="4 2"/>
                    <line x1="{ee_end_px:.1f}" y1="{panel_y - 10:.1f}" x2="{ee_end_px:.1f}" y2="{panel_y + 10:.1f}" stroke="#CBD5E1" stroke-width="1.0" stroke-dasharray="4 2"/>"""

    if mek_adi == "Merkezi 2 panel":
        panel_w = ee_px / 2 + 5 
        panel_svg += f'<rect x="{car_w_px_centre - panel_w:.1f}" y="{panel_y:.1f}" width="{panel_w:.1f}" height="10" fill="#E2E8F0" stroke="#475569" stroke-width="1"/>'
        panel_svg += f'<rect x="{car_w_px_centre:.1f}" y="{panel_y:.1f}" width="{panel_w:.1f}" height="10" fill="#E2E8F0" stroke="#475569" stroke-width="1"/>'
    elif mek_adi == "Teleskopik 2 panel":
        panel_w = ee_px / 2 + 10 
        sol_baslangic = car_w_px_centre - plw_px / 2
        panel_svg += f'<rect x="{sol_baslangic:.1f}" y="{panel_y:.1f}" width="{panel_w:.1f}" height="10" fill="#E2E8F0" stroke="#475569" stroke-width="1"/>'
        panel_svg += f'<rect x="{sol_baslangic + panel_w - 2:.1f}" y="{panel_y + 14:.1f}" width="{panel_w:.1f}" height="10" fill="#E2E8F0" stroke="#475569" stroke-width="1"/>'
    else:
        panel_svg += f'<line x1="{ee_start_px:.1f}" y1="{panel_y:.1f}" x2="{ee_end_px:.1f}" y2="{panel_y:.1f}" stroke="#DC2626" stroke-width="2.0" stroke-dasharray="5 5" opacity="0.5"/>'

    return mek_svg + panel_svg

def draw_dimension_line_tick(x1, y1, x2, y2, offset, label, text_fill, stroke, horizontal=True, tick_size=6):
    lx1 = x1; ly1 = y1
    lx2 = x2; ly2 = y2
    if offset != 0:
        if horizontal:
            ly1 += offset; ly2 += offset
        else:
            lx1 += offset; lx2 += offset
            
    tick1_start = (lx1 - tick_size/2, ly1 + tick_size/2) if horizontal else (lx1 - tick_size/2, ly1 - tick_size/2)
    tick1_end = (lx1 + tick_size/2, ly1 - tick_size/2) if horizontal else (lx1 + tick_size/2, ly1 + tick_size/2)
    tick2_start = (lx2 - tick_size/2, ly2 + tick_size/2) if horizontal else (lx2 - tick_size/2, ly2 - tick_size/2)
    tick2_end = (lx2 + tick_size/2, ly2 - tick_size/2) if horizontal else (lx2 + tick_size/2, ly2 + tick_size/2)

    return f"""<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{lx1:.1f}" y2="{ly1:.1f}" stroke="{stroke}" stroke-width="0.5" opacity="0.5"/>
               <line x1="{x2:.1f}" y1="{y2:.1f}" x2="{lx2:.1f}" y2="{ly2:.1f}" stroke="{stroke}" stroke-width="0.5" opacity="0.5"/>
               <line x1="{lx1:.1f}" y1="{ly1:.1f}" x2="{lx2:.1f}" y2="{ly2:.1f}" stroke="{stroke}" stroke-width="0.8"/>
               <line x1="{tick1_start[0]:.1f}" y1="{tick1_start[1]:.1f}" x2="{tick1_end[0]:.1f}" y2="{tick1_end[1]:.1f}" stroke="{stroke}" stroke-width="0.8"/>
               <line x1="{tick2_start[0]:.1f}" y1="{tick2_start[1]:.1f}" x2="{tick2_end[0]:.1f}" y2="{tick2_end[1]:.1f}" stroke="{stroke}" stroke-width="0.8"/>
               <text x="{(lx1+lx2)/2:.1f}" y="{(ly1+ly2)/2:.1f}" text-anchor="middle" dominant-baseline="central" font-size="11" fill="{text_fill}" transform="rotate({-90 if not horizontal else 0}, {(lx1+lx2)/2:.1f}, {(ly1+ly2)/2:.1f})">{label}</text>"""

# ─────────────────────────────────────────────────────────────────
#  MAIN STREAMLIT UI
# ─────────────────────────────────────────────────────────────────
st.title("🛗 Asansör Teknik Plan Seçici v3.0")
st.caption("EN 81-20/50 · 2014/33/EU · Ön değerlendirme ve Teknik Plan aracı")

with st.sidebar:
    st.header("📐 Kuyu Ölçüleri (Shaft)")
    kyg = st.number_input("Kuyu Genişliği KyG-SW (mm)", 800, 5000, 2000, 50)
    kyd = st.number_input("Kuyu Derinliği KyD-SD (mm)", 800, 6000, 2200, 50)
    pit = st.number_input("Kuyu Dibi — Pit (mm)",    200, 3000, 1600, 50)
    kuyu_boy = st.number_input("Kuyu Toplam Boyu (mm)", 3000, 200000, 30000, 500)

    st.header("🏢 Proje")
    kat     = st.number_input("Kat Sayısı", 2, 150, 8, 1)
    kapasite= st.slider("Kapasite (kg)", 100, 5000, 800, 10)
    st.selectbox("Kullanım Amacı", ["Konut","Ofis/Ticari","Hastane","Endüstriyel","Otel"])

    st.header("🎯 Tercihler")
    mr_sec  = st.selectbox("Makine Dairesi", ["Fark etmez","Makine dairesi yok (MRL)","Makine dairesi var (MR)"])
    st.select_slider("Bütçe", ["Ekonomik","Orta","Premium"], "Orta")
    deprem  = st.checkbox("Deprem Bölgesi (EN 81-77)")
    yangin  = st.checkbox("İtfaiyeci Asansörü (EN 81-72)")

mr_var = False if "yok" in mr_sec else (True if "var" in mr_sec else None)
seyir    = (kat - 1) * KAT_YUKSEKLIGI
overhead = kuyu_boy - pit - seyir

c1,c2,c3,c4 = st.columns(4)
c1.metric("Seyir Yüksekliği", f"{seyir/1000:.1f} m")
c2.metric("Overhead", f"{overhead} mm", delta="✓" if overhead > 0 else "✗", delta_color="normal" if overhead > 0 else "inverse")
c3.metric("Pit", f"{pit} mm")

if overhead <= 0:
    st.error("Overhead negatif — kuyu boyunu veya kat sayısını kontrol edin.")
    st.stop()

uygun = [s for s in SISTEMLER if s["kap_min"] <= kapasite <= s["kap_max"] and kat <= s["kat_max"] and pit >= s["pit_min"] and overhead >= s["oh_min"] and (mr_var is None or s["mr"] == mr_var)]
c4.metric("Uygun Sistem", len(uygun))

if not uygun:
    st.error("Uygun sistem bulunamadı.")
    st.stop()

st.divider()

tabs = st.tabs([s["ad"] for s in uygun])

for tab, sistem in zip(tabs, uygun):
    with tab:
        kombinasyonlar = tum_kombinasyonlari_hesapla_v2(kyg, kyd, kapasite, sistem)
        if not kombinasyonlar:
            st.warning("Geçerli kombinasyon bulunamadı.")
            continue

        st.markdown("#### 📋 Tüm Geçerli Teknik Kombinasyonlar")
        
        tablo_verisi = [{"#": i+1, "CW": r["cw_konum"], "Mekanizma": r["mek"], "DW(mm)": r['ll'], "EE(mm)": r['ee'], "PLW(mm)": r['plw'], "Hız": r["hiz"], "Ray": r["ray_isim"], "KbG": r["kbg"], "KbD": r["kbd"], "DBG_K": r["dbg_car"]} for i, r in enumerate(kombinasyonlar)]
        
        # Hata vermemesi adına dataframe güncellendi
        st.dataframe(tablo_verisi, use_container_width=True)

        st.markdown("#### 📐 Teknik Üst Görünüş Çizimi")
        secenekler = [f"#{i+1} | {r['cw_konum']} CW | {r['mek']} | DW={r['ll']} | KbG={r['kbg']} KbD={r['kbd']}" for i, r in enumerate(kombinasyonlar)]
        secim_idx = st.selectbox("Görüntülenecek kombinasyon:", range(len(secenekler)), format_func=lambda i: secenekler[i], key=f"sec_{sistem['id']}")
        
        r = kombinasyonlar[secim_idx]

        if r["cw_konum"] == "Yandan":
            if r["cw_info"]["senaryo"] == "cakisiyor": st.info(f"ℹ️ {r['cw_info']['mesaj']}")
            else: st.success(f"✅ {r['cw_info']['mesaj']}")

        svg_html, _ = svg_ciz_v3(r, kyg, kyd, uid=f"{sistem['id']}_{secim_idx}")
        st.markdown(f'<div align="center">{svg_html.replace(chr(10), "")}</div>', unsafe_allow_html=True)

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Kabin-W (KbG)", f"{r['kbg']} mm")
        col2.metric("Kabin-D (KbD)", f"{r['kbd']} mm")
        col3.metric("DBG_KABIN (K)", f"{r['dbg_car']} mm")
        col4.metric("Giriş EE", f"{r['ee']} mm")
        col5.metric("PLW Tolerans", f"{r['plw']} mm")

st.divider()
st.caption("⚠ Ön değerlendirme aracıdır. Kesin seçim için lisanslı mühendis onayı gerekir.")
