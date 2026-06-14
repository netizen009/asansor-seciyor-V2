#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Asansör Sistem Seçici
=====================
Kuyu koşulları ve teknik gereksinimlere göre
uygun asansör konfigürasyonlarını öneren interaktif program.
"""

import sys
import os
from colorama import init, Fore, Style, Back

init(autoreset=True)

# ─────────────────────────────────────────────
#  RENK KISAYOLLARI
# ─────────────────────────────────────────────
C  = Fore.CYAN
G  = Fore.GREEN
Y  = Fore.YELLOW
R  = Fore.RED
M  = Fore.MAGENTA
W  = Fore.WHITE
B  = Style.BRIGHT
D  = Style.DIM
RS = Style.RESET_ALL

# ─────────────────────────────────────────────
#  ASANSÖr VERİTABANI
#  Her giriş: {id, ad, kisa_ad, parametreler, avantajlar, dezavantajlar, tipik_kullanim}
# ─────────────────────────────────────────────
ASANSOR_DB = [
    {
        "id": "MR_GR_11_UP",
        "ad": "Makine Daireli · Dişlili · 1:1 · Üstten Palanga",
        "kisa": "MR Dişlili 1:1",
        "hiz_max": 2.5,
        "kapasite_max": 2000,
        "kapasite_min": 200,
        "kat_max": 20,
        "mr": True,
        "mrl": False,
        "disli": True,
        "dishisiz": False,
        "oran_11": True,
        "oran_21": False,
        "ustten": True,
        "alttan": False,
        "cw_yan": True,
        "cw_arka": True,
        "pit_min": 1200,     # mm - kuyu dibi boşluğu
        "overhead_min": 3600, # mm - kuyu üst boşluk
        "mrdairesi": True,
        "avantajlar": [
            "Düşük ilk maliyet",
            "Yaygın yedek parça bulunabilirliği",
            "Basit mekanik yapı",
            "Geniş kapasite aralığı",
        ],
        "dezavantajlar": [
            "Makine dairesi gerektirir (+15–25 m²)",
            "Yağ ve bakım yoğun",
            "Düşük enerji verimliliği",
            "Hız sınırlı (≤2,5 m/s)",
        ],
        "tipik": "Orta katlı konut, alışveriş merkezi, hastane (orta trafik)",
    },
    {
        "id": "MR_GR_21_UP",
        "ad": "Makine Daireli · Dişlili · 2:1 · Üstten Palanga",
        "kisa": "MR Dişlili 2:1",
        "hiz_max": 1.6,
        "kapasite_max": 5000,
        "kapasite_min": 500,
        "kat_max": 15,
        "mr": True,
        "mrl": False,
        "disli": True,
        "dishisiz": False,
        "oran_11": False,
        "oran_21": True,
        "ustten": True,
        "alttan": False,
        "cw_yan": True,
        "cw_arka": True,
        "pit_min": 1400,
        "overhead_min": 4200,
        "mrdairesi": True,
        "avantajlar": [
            "Yüksek yük kapasitesi (≤5.000 kg)",
            "Daha küçük motor gücü yeterli",
            "Endüstriyel/kargo uygulamaları için ideal",
        ],
        "dezavantajlar": [
            "Makine dairesi gerektirir",
            "Daha yüksek overhead boşluğu",
            "Karmaşık halat düzeni",
            "Hız düşük (≤1,6 m/s)",
        ],
        "tipik": "Yük asansörü, büyük alışveriş merkezi servis asansörü, hastane yatak asansörü",
    },
    {
        "id": "MR_GL_11_UP",
        "ad": "Makine Daireli · Dişlisiz · 1:1 · Üstten Palanga",
        "kisa": "MR Dişlisiz 1:1",
        "hiz_max": 10.0,
        "kapasite_max": 2500,
        "kapasite_min": 400,
        "kat_max": 100,
        "mr": True,
        "mrl": False,
        "disli": False,
        "dishisiz": True,
        "oran_11": True,
        "oran_21": False,
        "ustten": True,
        "alttan": False,
        "cw_yan": True,
        "cw_arka": True,
        "pit_min": 1500,
        "overhead_min": 4000,
        "mrdairesi": True,
        "avantajlar": [
            "Çok yüksek hız (≤10 m/s)",
            "Düşük bakım",
            "Uzun ömür",
            "Yüksek bina uygulamaları",
            "Sessiz ve konforlu",
        ],
        "dezavantajlar": [
            "Makine dairesi gerektirir",
            "Yüksek ilk maliyet",
            "Özel kontrol sistemi",
        ],
        "tipik": "Yüksek/çok katlı ofis kuleleri, oteller, rezidanslar",
    },
    {
        "id": "MRL_GL_11_UP",
        "ad": "Makine Dairesiz · Dişlisiz · 1:1 · Üstten Palanga",
        "kisa": "MRL Dişlisiz 1:1",
        "hiz_max": 4.0,
        "kapasite_max": 2000,
        "kapasite_min": 200,
        "kat_max": 40,
        "mr": False,
        "mrl": True,
        "disli": False,
        "dishisiz": True,
        "oran_11": True,
        "oran_21": False,
        "ustten": True,
        "alttan": False,
        "cw_yan": True,
        "cw_arka": True,
        "pit_min": 1100,
        "overhead_min": 3500,
        "mrdairesi": False,
        "avantajlar": [
            "Makine dairesi gerekmez → bina alanı tasarrufu",
            "Enerji verimli (VF sürücü)",
            "Modern estetik",
            "Düşük işletme maliyeti",
            "Geniş kapasite aralığı",
        ],
        "dezavantajlar": [
            "Kuyu başı yeterli olmalı (≥3.500 mm)",
            "Motor kuyu içinde → bakım erişimi daha zor",
            "Isı yönetimi önemli",
        ],
        "tipik": "Konut, ofis, AVM, hastane — modern binaların büyük çoğunluğu",
    },
    {
        "id": "MRL_GL_21_UP",
        "ad": "Makine Dairesiz · Dişlisiz · 2:1 · Üstten Palanga",
        "kisa": "MRL Dişlisiz 2:1",
        "hiz_max": 2.0,
        "kapasite_max": 3500,
        "kapasite_min": 400,
        "kat_max": 20,
        "mr": False,
        "mrl": True,
        "disli": False,
        "dishisiz": True,
        "oran_11": False,
        "oran_21": True,
        "ustten": True,
        "alttan": False,
        "cw_yan": True,
        "cw_arka": True,
        "pit_min": 1200,
        "overhead_min": 3800,
        "mrdairesi": False,
        "avantajlar": [
            "Makine dairesi gerekmez",
            "Yüksek yük + enerji verimliliği",
            "Daha küçük motor",
        ],
        "dezavantajlar": [
            "Daha fazla kasnak ve halat",
            "Kuyu üst yüksekliği kritik",
        ],
        "tipik": "Orta-yüksek kapasiteli konut ve ticari, hastane servis asansörleri",
    },
    {
        "id": "MRL_GL_11_BACK",
        "ad": "Makine Dairesiz · Dişlisiz · 1:1 · Alttan Palanga (Backpack)",
        "kisa": "MRL Backpack 1:1",
        "hiz_max": 2.5,
        "kapasite_max": 1600,
        "kapasite_min": 200,
        "kat_max": 20,
        "mr": False,
        "mrl": True,
        "disli": False,
        "dishisiz": True,
        "oran_11": True,
        "oran_21": False,
        "ustten": False,
        "alttan": True,
        "cw_yan": False,
        "cw_arka": True,
        "pit_min": 1200,
        "overhead_min": 2800,
        "mrdairesi": False,
        "avantajlar": [
            "Çok düşük kuyu üst yüksekliği (≥2.800 mm)",
            "Dar kuyu genişliği",
            "Mevcut binalarda renovasyon için ideal",
            "Panoramik kabin uyumlu",
        ],
        "dezavantajlar": [
            "Kapasite sınırlı (≤1.600 kg)",
            "Karmaşık alt çerçeve yapısı",
            "Daha yüksek kuyu dibi gerekebilir",
        ],
        "tipik": "Tarihi bina yenileme, dar kuyu, konut (villa, butik otel)",
    },
    {
        "id": "MR_GL_21_UP",
        "ad": "Makine Daireli · Dişlisiz · 2:1 · Üstten Palanga",
        "kisa": "MR Dişlisiz 2:1",
        "hiz_max": 6.0,
        "kapasite_max": 5000,
        "kapasite_min": 800,
        "kat_max": 60,
        "mr": True,
        "mrl": False,
        "disli": False,
        "dishisiz": True,
        "oran_11": False,
        "oran_21": True,
        "ustten": True,
        "alttan": False,
        "cw_yan": True,
        "cw_arka": True,
        "pit_min": 1600,
        "overhead_min": 4500,
        "mrdairesi": True,
        "avantajlar": [
            "Çok yüksek yük + yüksek hız",
            "Büyük ticari projeler",
            "Uzun seyir mesafesi",
        ],
        "dezavantajlar": [
            "Makine dairesi gerektirir",
            "Yüksek kuyu başı gereksinimi",
            "Karmaşık halat düzeni",
            "Yüksek maliyet",
        ],
        "tipik": "Yüksek katlı AVM, ofis kuleleri, büyük hastaneler",
    },
    {
        "id": "HYD_DIRECT",
        "ad": "Hidrolik · Doğrudan Tahrik",
        "kisa": "Hidrolik Doğrudan",
        "hiz_max": 0.8,
        "kapasite_max": 5000,
        "kapasite_min": 200,
        "kat_max": 5,
        "mr": False,
        "mrl": False,
        "disli": False,
        "dishisiz": False,
        "oran_11": True,
        "oran_21": False,
        "ustten": False,
        "alttan": True,
        "cw_yan": False,
        "cw_arka": False,
        "pit_min": 400,
        "overhead_min": 2500,
        "mrdairesi": True,  # pompa dairesi
        "avantajlar": [
            "Çok düşük kuyu dibi ve üst yüksekliği",
            "Karşı ağırlık gerekmez",
            "Yüksek yük kapasitesi",
            "Makine dairesi herhangi bir konumda",
        ],
        "dezavantajlar": [
            "Sadece düşük kat sayısı (≤5 kat)",
            "Hız düşük (≤0,8 m/s)",
            "Yüksek enerji tüketimi",
            "Çevre riski (yağ sızıntısı)",
            "Sıcaklık hassasiyeti",
        ],
        "tipik": "Villa, 2–5 katlı küçük bina, engelli platformu",
    },
]

# ─────────────────────────────────────────────
#  YARDIMCI FONKSİYONLAR
# ─────────────────────────────────────────────

def temizle():
    os.system("cls" if os.name == "nt" else "clear")


def baslik_yaz(metin: str, alt_cizgi: str = "═"):
    genislik = 62
    print()
    print(C + B + "╔" + alt_cizgi * (genislik - 2) + "╗")
    pad = (genislik - 2 - len(metin)) // 2
    print(C + B + "║" + " " * pad + W + B + metin + " " * (genislik - 2 - pad - len(metin)) + C + B + "║")
    print(C + B + "╚" + alt_cizgi * (genislik - 2) + "╝" + RS)
    print()


def bolum_baslik(metin: str):
    print(Y + B + f"\n  ▶  {metin}" + RS)
    print(Y + "  " + "─" * 56 + RS)


def soru_sor(metin: str, secenekler: list, varsayilan: int = None) -> str:
    """Numaralandırılmış seçenek menüsü ile soru sorar."""
    print()
    print(G + B + f"  ❓ {metin}" + RS)
    for i, s in enumerate(secenekler, 1):
        isaretci = G + " ▸ " if varsayilan and i == varsayilan else W + "   "
        print(f"{isaretci}{C}{i}{RS}. {s}")
    print()
    while True:
        try:
            cevap = input(Y + "  Seçiminiz" + RS + f" [1–{len(secenekler)}]" +
                          (f" (Varsayılan: {varsayilan})" if varsayilan else "") + ": ").strip()
            if cevap == "" and varsayilan:
                return secenekler[varsayilan - 1]
            val = int(cevap)
            if 1 <= val <= len(secenekler):
                return secenekler[val - 1]
            print(R + f"  Lütfen 1 ile {len(secenekler)} arasında bir sayı girin." + RS)
        except ValueError:
            print(R + "  Geçersiz giriş. Lütfen bir sayı girin." + RS)


def sayi_sor(metin: str, min_val: float, max_val: float, varsayilan: float = None) -> float:
    """Sayısal değer girişi alır."""
    print()
    aralik = f"[{min_val}–{max_val}]"
    varsa = f" (Varsayılan: {varsayilan})" if varsayilan is not None else ""
    while True:
        try:
            cevap = input(G + B + f"  ❓ {metin} " + RS + Y + aralik + varsa + ": " + RS).strip()
            if cevap == "" and varsayilan is not None:
                return float(varsayilan)
            val = float(cevap)
            if min_val <= val <= max_val:
                return val
            print(R + f"  Lütfen {min_val} ile {max_val} arasında bir değer girin." + RS)
        except ValueError:
            print(R + "  Geçersiz giriş. Lütfen sayısal bir değer girin." + RS)


def evet_hayir(metin: str, varsayilan: bool = True) -> bool:
    varsayilan_str = "E/h" if varsayilan else "e/H"
    print()
    while True:
        cevap = input(G + B + f"  ❓ {metin} " + RS + Y + f"[{varsayilan_str}]: " + RS).strip().lower()
        if cevap in ("e", "evet", "y", "yes"):
            return True
        elif cevap in ("h", "hayır", "hayir", "n", "no"):
            return False
        elif cevap == "":
            return varsayilan
        else:
            print(R + "  Lütfen 'e' (evet) veya 'h' (hayır) girin." + RS)


def puan_goster(puan: int, max_puan: int = 10) -> str:
    dolu = "█"
    bos  = "░"
    normalize = round((puan / max_puan) * 10)
    renk = G if normalize >= 7 else (Y if normalize >= 4 else R)
    return renk + dolu * normalize + D + bos * (10 - normalize) + RS


def sonuc_karti_yaz(asansor: dict, puan: int, max_puan: int, sira: int):
    """Tek bir asansör seçeneği için sonuç kartı yazar."""
    genislik = 60
    baslik = f"  #{sira}  {asansor['ad']}"
    uyum_bar = puan_goster(puan, max_puan)

    print()
    renk_kart = G if sira == 1 else (C if sira == 2 else W)
    print(renk_kart + B + "  ┌" + "─" * (genislik - 2) + "┐" + RS)
    print(renk_kart + B + "  │" + RS + B + baslik.ljust(genislik - 2) + renk_kart + B + "│" + RS)
    print(renk_kart + B + "  ├" + "─" * (genislik - 2) + "┤" + RS)

    # Uyum çubuğu
    uyum_yazi = f"  Uyum puanı: {uyum_bar}  {puan}/{max_puan}"
    print(renk_kart + B + "  │" + RS + uyum_yazi.ljust(genislik + 8) + renk_kart + B + "│" + RS)

    # Teknik özellikler
    ozellikler = [
        f"  ⚡ Maks hız        : {asansor['hiz_max']} m/s",
        f"  ⚖  Kapasite        : {asansor['kapasite_min']}–{asansor['kapasite_max']} kg",
        f"  🏢 Maks kat sayısı : {asansor['kat_max']} kat",
        f"  ↕  Kuyu dibi min   : {asansor['pit_min']} mm",
        f"  ↑  Kuyu üstü min   : {asansor['overhead_min']} mm",
    ]
    for oz in ozellikler:
        print(renk_kart + B + "  │" + RS + oz.ljust(genislik - 2) + renk_kart + B + "│" + RS)

    # Avantajlar
    print(renk_kart + B + "  ├" + "─" * (genislik - 2) + "┤" + RS)
    print(renk_kart + B + "  │" + RS + G + "  ✔ Avantajlar".ljust(genislik - 2) + renk_kart + B + "│" + RS)
    for av in asansor["avantajlar"][:3]:
        print(renk_kart + B + "  │" + RS + G + f"    • {av}".ljust(genislik - 2) + renk_kart + B + "│" + RS)

    # Dezavantajlar
    print(renk_kart + B + "  │" + RS + R + "  ✖ Dikkat Edilecekler".ljust(genislik - 2) + renk_kart + B + "│" + RS)
    for dez in asansor["dezavantajlar"][:3]:
        print(renk_kart + B + "  │" + RS + R + f"    • {dez}".ljust(genislik - 2) + renk_kart + B + "│" + RS)

    # Tipik kullanım
    print(renk_kart + B + "  ├" + "─" * (genislik - 2) + "┤" + RS)
    tipik_metin = f"  💡 {asansor['tipik']}"
    # Uzun metni sar
    if len(tipik_metin) > genislik - 4:
        tipik_metin = tipik_metin[:genislik - 7] + "..."
    print(renk_kart + B + "  │" + RS + Y + tipik_metin.ljust(genislik - 2) + renk_kart + B + "│" + RS)
    print(renk_kart + B + "  └" + "─" * (genislik - 2) + "┘" + RS)


# ─────────────────────────────────────────────
#  FİLTRELEME MOTORU
# ─────────────────────────────────────────────

def asansor_filtrele_ve_puanla(cevaplar: dict) -> list:
    """
    Kullanıcı cevaplarına göre veritabanını filtreler ve puanlar.
    Döndürür: [(puan, max_puan, asansor), ...]  sıralı
    """
    sonuclar = []

    for a in ASANSOR_DB:
        puan = 0
        max_p = 0
        elendi = False

        # ── ZORUNLU ELİMİNASYON KURALLARI ──────────────────────────

        # 1) Hız kontrolü
        hiz = cevaplar.get("hiz", 1.0)
        if hiz > a["hiz_max"]:
            continue  # elenmiş

        # 2) Kapasite kontrolü
        kap = cevaplar.get("kapasite", 630)
        if kap < a["kapasite_min"] or kap > a["kapasite_max"]:
            continue

        # 3) Kat sayısı kontrolü
        kat = cevaplar.get("kat_sayisi", 5)
        if kat > a["kat_max"]:
            continue

        # 4) Makine dairesi kısıtı
        mr_var = cevaplar.get("mr_var", None)
        if mr_var is False and a["mrdairesi"] is True and a["id"] not in ("HYD_DIRECT",):
            # Eğer makine dairesi yok ve hidrolik değilse → MR sistemler elenir
            if a["mr"] is True:
                continue
        if mr_var is True and a["mrl"] is True and cevaplar.get("mrl_tercih") is False:
            continue  # Kullanıcı özellikle MR istiyorsa MRL çıkar

        # 5) Kuyu dibi boşluğu (pit depth)
        pit = cevaplar.get("pit_derinligi", None)
        if pit is not None and pit < a["pit_min"]:
            continue

        # 6) Kuyu üst yüksekliği (overhead)
        overhead = cevaplar.get("overhead", None)
        if overhead is not None and overhead < a["overhead_min"]:
            continue

        # 7) Karşı ağırlık kısıtı
        cw_pozisyon = cevaplar.get("cw_pozisyon", "Fark etmez")
        if cw_pozisyon == "Sadece yandan" and not a["cw_yan"]:
            continue
        if cw_pozisyon == "Sadece arkadan" and not a["cw_arka"]:
            continue

        # ── PUANLAMA ────────────────────────────────────────────────

        # Enerji verimliliği önceliği
        enerji = cevaplar.get("enerji_onceligi", "Orta")
        max_p += 2
        if enerji == "Yüksek":
            if a["dishisiz"]:
                puan += 2
            elif a["disli"]:
                puan += 1
        elif enerji == "Orta":
            puan += 1

        # Bütçe önceliği
        butce = cevaplar.get("butce", "Orta")
        max_p += 2
        if butce == "Ekonomik":
            if a["disli"]:
                puan += 2
            else:
                puan += 0
        elif butce == "Orta":
            if a["mrl"] and not a["disli"]:
                puan += 2
            else:
                puan += 1
        else:  # Premium
            if a["dishisiz"]:
                puan += 2
            else:
                puan += 1

        # Bakım kolaylığı
        bakim = cevaplar.get("bakim_kolay", True)
        max_p += 1
        if bakim and a["mr"]:
            puan += 1
        elif not bakim and a["mrl"]:
            puan += 1

        # Hız uyumu (istenene ne kadar yakın)
        max_p += 2
        oran = hiz / a["hiz_max"]
        if 0.5 <= oran <= 1.0:
            puan += 2
        elif oran < 0.5:
            puan += 1  # çok kapasiteli sistem, biraz israf

        # Kapasite uyumu
        max_p += 2
        kap_oran = kap / a["kapasite_max"]
        if 0.4 <= kap_oran <= 0.9:
            puan += 2
        elif kap_oran < 0.4:
            puan += 1

        # Uygulama tipi uyumu
        uygulama = cevaplar.get("uygulama", "Konut")
        max_p += 2
        tipik_lower = a["tipik"].lower()
        if uygulama == "Konut" and ("konut" in tipik_lower or "villa" in tipik_lower or "rezidans" in tipik_lower):
            puan += 2
        elif uygulama == "Ofis/Ticari" and ("ofis" in tipik_lower or "ticari" in tipik_lower or "avm" in tipik_lower):
            puan += 2
        elif uygulama == "Hastane" and "hastane" in tipik_lower:
            puan += 2
        elif uygulama == "Endüstriyel/Yük" and ("yük" in tipik_lower or "endüstri" in tipik_lower or "servis" in tipik_lower):
            puan += 2
        elif uygulama == "Otel/Turizm" and ("otel" in tipik_lower or "butik" in tipik_lower):
            puan += 2
        else:
            puan += 1  # nötr

        # Yenilik / estetik tercihi
        modern = cevaplar.get("modern_tercih", True)
        max_p += 1
        if modern and a["mrl"]:
            puan += 1
        elif not modern and a["mr"] and a["disli"]:
            puan += 1

        sonuclar.append((puan, max_p, a))

    # Puana göre sırala (yüksekten düşüğe)
    sonuclar.sort(key=lambda x: x[0], reverse=True)
    return sonuclar


# ─────────────────────────────────────────────
#  ANA PROGRAM AKIŞI
# ─────────────────────────────────────────────

def sorulari_sor() -> dict:
    cevaplar = {}

    temizle()
    baslik_yaz("ASANSÖR SİSTEM SEÇİCİ  v1.0", "═")
    print(D + "  Avrupa Asansör Yönetmeliği (2014/33/EU) ve EN 81-20/50 standartları\n"
              "  temel alınarak hazırlanmıştır. Sonuçlar ön değerlendirme niteliğindedir." + RS)

    # ── BÖLÜM 1: Proje Bilgileri ─────────────────────────────────
    bolum_baslik("1 / 6  —  Proje Tanımı")

    cevaplar["uygulama"] = soru_sor(
        "Asansör hangi amaçla kullanılacak?",
        ["Konut", "Ofis/Ticari", "Hastane", "Endüstriyel/Yük", "Otel/Turizm"],
        varsayilan=1,
    )

    cevaplar["kat_sayisi"] = int(sayi_sor(
        "Toplam kat sayısı (zemin dahil)?",
        min_val=2, max_val=150, varsayilan=8
    ))

    cevaplar["seyir_yuksekligi"] = sayi_sor(
        "Toplam seyir yüksekliği (m)?",
        min_val=3, max_val=500, varsayilan=cevaplar["kat_sayisi"] * 3.0
    )

    # ── BÖLÜM 2: Performans Gereksinimleri ───────────────────────
    bolum_baslik("2 / 6  —  Performans Gereksinimleri")

    cevaplar["kapasite"] = sayi_sor(
        "İstenen taşıma kapasitesi (kg)?  [EN 81: min 320 kg]",
        min_val=100, max_val=10000, varsayilan=630
    )

    hiz_secenekler = {
        "0,63 m/s — Villa / küçük konut":      0.63,
        "1,00 m/s — Konut standardı":           1.00,
        "1,60 m/s — Orta hız (konut/ofis)":    1.60,
        "2,50 m/s — Hızlı (ofis/AVM)":         2.50,
        "4,00 m/s — Yüksek hız":               4.00,
        "6,00+ m/s — Çok yüksek kule":         6.00,
    }
    hiz_sec = soru_sor(
        "İstenen nominal kabin hızı?",
        list(hiz_secenekler.keys()),
        varsayilan=2,
    )
    cevaplar["hiz"] = hiz_secenekler[hiz_sec]

    cevaplar["kabin_genislik"] = sayi_sor(
        "Kabin iç genişliği (mm)?  [Tipik: 1000–2000 mm]",
        min_val=600, max_val=3000, varsayilan=1100
    )
    cevaplar["kabin_derinlik"] = sayi_sor(
        "Kabin iç derinliği (mm)?",
        min_val=800, max_val=3000, varsayilan=1400
    )

    # ── BÖLÜM 3: Kuyu Koşulları ──────────────────────────────────
    bolum_baslik("3 / 6  —  Kuyu Koşulları")

    pit_biliniyor = evet_hayir("Kuyu dibi (pit) derinliği biliniyor mu?", varsayilan=False)
    if pit_biliniyor:
        cevaplar["pit_derinligi"] = sayi_sor(
            "Mevcut kuyu dibi boşluğu (mm)?",
            min_val=200, max_val=3000, varsayilan=1200
        )
    else:
        cevaplar["pit_derinligi"] = None

    oh_biliniyor = evet_hayir("Kuyu üst boşluğu (overhead) biliniyor mu?", varsayilan=False)
    if oh_biliniyor:
        cevaplar["overhead"] = sayi_sor(
            "Mevcut kuyu üst boşluğu (mm)?",
            min_val=2000, max_val=8000, varsayilan=3600
        )
    else:
        cevaplar["overhead"] = None

    cevaplar["cw_pozisyon"] = soru_sor(
        "Karşı ağırlık (counterweight) konumu için kısıt var mı?",
        ["Fark etmez", "Sadece yandan", "Sadece arkadan"],
        varsayilan=1,
    )

    # ── BÖLÜM 4: Makine Dairesi ──────────────────────────────────
    bolum_baslik("4 / 6  —  Makine Dairesi Durumu")

    mr_durum = soru_sor(
        "Makine dairesi durumu?",
        [
            "Mevcut / planlanmış makine dairesi var",
            "Makine dairesi yok, MRL tercih edilir",
            "Hidrolik düşünülüyor (düşük kat, yüksek yük)",
            "Fark etmez / uzman karar versin",
        ],
        varsayilan=2,
    )
    if "yok" in mr_durum.lower() or "mrl" in mr_durum.lower():
        cevaplar["mr_var"] = False
        cevaplar["mrl_tercih"] = True
    elif "var" in mr_durum.lower():
        cevaplar["mr_var"] = True
        cevaplar["mrl_tercih"] = False
    else:
        cevaplar["mr_var"] = None
        cevaplar["mrl_tercih"] = None

    # ── BÖLÜM 5: Öncelikler ──────────────────────────────────────
    bolum_baslik("5 / 6  —  Proje Öncelikleri")

    cevaplar["butce"] = soru_sor(
        "Bütçe önceliği?",
        ["Ekonomik (ilk maliyet düşük tutulsun)", "Orta (denge)", "Premium (en iyi teknoloji)"],
        varsayilan=2,
    )
    cevaplar["butce"] = {"Ekonomik (ilk maliyet düşük tutulsun)": "Ekonomik",
                         "Orta (denge)": "Orta",
                         "Premium (en iyi teknoloji)": "Premium"}[cevaplar["butce"]]

    cevaplar["enerji_onceligi"] = soru_sor(
        "Enerji verimliliği önceliği?",
        ["Düşük (standart yeterli)", "Orta", "Yüksek (yeşil bina / LEED hedefi)"],
        varsayilan=2,
    )
    cevaplar["enerji_onceligi"] = {"Düşük (standart yeterli)": "Düşük",
                                    "Orta": "Orta",
                                    "Yüksek (yeşil bina / LEED hedefi)": "Yüksek"}[cevaplar["enerji_onceligi"]]

    cevaplar["bakim_kolay"] = evet_hayir(
        "Bakım kolaylığı öncelikli mi? (Makine daireli sistemler daha kolay erişim sunar)",
        varsayilan=False
    )

    cevaplar["modern_tercih"] = evet_hayir(
        "Modern / dijital kontrol sistemi (MRL/gearless) tercih edilsin mi?",
        varsayilan=True
    )

    # ── BÖLÜM 6: Ek Özellikler ───────────────────────────────────
    bolum_baslik("6 / 6  —  Ek Özellikler")

    cevaplar["acil_enerji"] = evet_hayir(
        "Acil durum / ARD (Automatic Rescue Device) gerekli mi?",
        varsayilan=True
    )

    cevaplar["deprem_bolgesi"] = evet_hayir(
        "Deprem bölgesi (sismik kısıt) söz konusu mu?",
        varsayilan=False
    )

    cevaplar["yangin_servisi"] = evet_hayir(
        "İtfaiyeci servisi (Firefighters' lift — EN 81-72) gerekli mi?",
        varsayilan=False
    )

    return cevaplar


def sonuclari_goster(sonuclar: list, cevaplar: dict):
    temizle()
    baslik_yaz("SONUÇLAR — ÖNERİLEN ASANSÖR KONFİGÜRASYONLARI", "═")

    if not sonuclar:
        print(R + B + "\n  ✖  Girilen parametrelerle uyumlu standart sistem bulunamadı.\n"
              "     Lütfen parametreleri gözden geçiriniz veya bir uzmanla görüşünüz.\n" + RS)
        return

    # Özet giriş parametreleri
    bolum_baslik("Girilen Parametreler")
    ozet = [
        ("Uygulama",        cevaplar.get("uygulama", "—")),
        ("Kat sayısı",       f"{cevaplar.get('kat_sayisi', '—')} kat"),
        ("Kapasite",         f"{cevaplar.get('kapasite', '—')} kg"),
        ("Hız",              f"{cevaplar.get('hiz', '—')} m/s"),
        ("Kabin (G×D)",      f"{cevaplar.get('kabin_genislik', '—')} × {cevaplar.get('kabin_derinlik', '—')} mm"),
        ("Kuyu dibi",        f"{cevaplar.get('pit_derinligi', '?')} mm" if cevaplar.get('pit_derinligi') else "Belirtilmedi"),
        ("Kuyu üstü",        f"{cevaplar.get('overhead', '?')} mm" if cevaplar.get('overhead') else "Belirtilmedi"),
        ("Makine dairesi",   "Var" if cevaplar.get('mr_var') else ("Yok" if cevaplar.get('mr_var') is False else "Fark etmez")),
        ("Bütçe",            cevaplar.get("butce", "—")),
        ("Enerji",           cevaplar.get("enerji_onceligi", "—")),
    ]
    for k, v in ozet:
        print(f"  {D}{k:<22}{RS}{W}{v}{RS}")

    # Sonuç kartları (en fazla 4)
    goster_sayisi = min(4, len(sonuclar))
    bolum_baslik(f"Uygun Asansör Sistemleri  ({len(sonuclar)} eşleşme bulundu, en iyi {goster_sayisi} gösteriliyor)")

    for sira, (puan, max_p, asansor) in enumerate(sonuclar[:goster_sayisi], 1):
        sonuc_karti_yaz(asansor, puan, max_p, sira)

    # Ek notlar
    print()
    print(D + "  ─" * 30 + RS)
    print(M + B + "\n  📋 ÖNEMLİ NOTLAR\n" + RS)
    notlar = [
        "Bu analiz ön değerlendirme amacıyla hazırlanmıştır.",
        "Kesin sistem seçimi için lisanslı asansör mühendisi onayı zorunludur.",
        "EN 81-20, EN 81-50 ve yerel yönetmeliklere uygunluk doğrulanmalıdır.",
        "Deprem bölgesiyse EN 81-77 sismik gereksinimleri de değerlendirilmeli.",
        "İtfaiyeci asansörü gerekiyorsa EN 81-72 kapsamında ayrı inceleme yapılmalı.",
    ]
    if cevaplar.get("deprem_bolgesi"):
        notlar.append("⚠  Sismik bölge seçildi → karşı ağırlık kilitleri ve kabin tamponları kritik.")
    if cevaplar.get("yangin_servisi"):
        notlar.append("⚠  İtfaiyeci asansörü → ayrı kuyu, özel kapı ve kontrol paneli gerektirir.")
    for n in notlar:
        print(Y + f"  • {n}" + RS)
    print()


def tekrar_sor() -> bool:
    print()
    return evet_hayir("Yeni bir sorgulama yapmak ister misiniz?", varsayilan=True)


def main():
    while True:
        try:
            cevaplar = sorulari_sor()
            sonuclar = asansor_filtrele_ve_puanla(cevaplar)
            sonuclari_goster(sonuclar, cevaplar)
            if not tekrar_sor():
                print(C + B + "\n  Asansör Sistem Seçici kapatılıyor. İyi çalışmalar!\n" + RS)
                break
        except KeyboardInterrupt:
            print(R + "\n\n  Program sonlandırıldı.\n" + RS)
            sys.exit(0)


if __name__ == "__main__":
    main()
