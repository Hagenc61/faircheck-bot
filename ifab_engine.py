import re

LAWS = {
    1: "The Field of Play",
    2: "The Ball",
    3: "The Players",
    4: "The Players' Equipment",
    5: "The Referee",
    6: "The Other Match Officials",
    7: "The Duration of the Match",
    8: "The Start and Restart of Play",
    9: "The Ball in and out of Play",
    10: "Determining the Outcome of a Match",
    11: "Offside",
    12: "Fouls and Misconduct",
    13: "Free Kicks",
    14: "The Penalty Kick",
    15: "The Throw-in",
    16: "The Goal Kick",
    17: "The Corner Kick",
}

# Concise paraphrases of the current IFAB 2026/27 sub-sections.
SUBRULES = {
    1: {"default": ("1.1–1.11", "Sahanın yüzeyi, çizgileri, ölçüleri, kale/ceza alanları, köşe alanı, bayraklar, teknik alan ve kalelerle ilgili hükümler." )},
    2: {"default": ("2.1–2.2", "Topun özellikleri, ölçüleri ve maç sırasında topun uygunluğuyla ilgili hükümler." )},
    3: {"default": ("3.1–3.8", "Oyuncu sayısı, kaptan, oyuncu değişiklikleri, değiştirilen oyuncular, kalecinin değişimi, saha dışındaki oyuncu ve takım görevlileriyle ilgili hükümler." )},
    4: {"default": ("4.1–4.6", "Temel ve zorunlu ekipman, forma renkleri, takılar ve diğer ekipman güvenliğiyle ilgili hükümler." )},
    5: {"default": ("5.1–5.9", "Hakemin yetkileri, kararları, avantaj uygulaması, disiplin yetkisi, sakatlıklar ve maçın yönetimiyle ilgili hükümler." )},
    6: {"default": ("6.1–6.12", "Yardımcı hakemler, dördüncü hakem, VAR ve AVAR'ın görevleri ile hakeme yardımcı olma hükümleri." )},
    7: {"default": ("7.1–7.5", "Maçın devreleri, devre arası, kayıp zaman ve uzatma süresinin belirlenmesiyle ilgili hükümler." )},
    8: {"default": ("8.1–8.3", "Başlama vuruşu, hakem atışı ve diğer yeniden başlatma yöntemlerinin uygulanması." )},
    9: {"default": ("9.1–9.2", "Topun tamamen oyun alanını terk etmesi, oyun dışı kalması ve hakem/top temasının oyuna etkisi." )},
    10: {"default": ("10.1–10.3", "Golün belirlenmesi, kazanan takım ve penaltı vuruşları serisiyle maç sonucunun belirlenmesi." )},
    11: {
        "default": ("11.1–11.4", "Ofsayt pozisyonu, ofsayt ihlali, ihlal olmayan durumlar ve yaptırımlar."),
        "offside": ("11.1–11.4", "Oyuncunun topun oynandığı anda ofsayt pozisyonunda olup olmadığı; oyuna, rakibe veya avantaj elde etmeye müdahale edip etmediği değerlendirilir."),
    },
    12: {
        "default": ("12.1–12.5", "Direkt/endirekt serbest vuruş gerektiren ihlaller, disiplin cezaları ve faul sonrası oyunun yeniden başlatılması."),
        "foul": ("12.1", "Temaslı müdahalelerde ihlalin dikkatsiz, kontrolsüz veya aşırı kuvvetli olup olmadığı değerlendirilir. Dikkatsiz müdahalede disiplin cezası gerekmez; kontrolsüz müdahale sarı kart, aşırı kuvvet kullanımı ise kırmızı kart gerektirebilir."),
        "handball": ("12.1", "Elle oynama değerlendirmesinde topun elle/kol ile oynanması, kolun vücuda göre konumu ve ilgili istisnalar incelenir."),
        "discipline": ("12.4", "Sarı/kırmızı kart değerlendirmesinde ihlalin niteliği, sportmenlik dışı davranış, ciddi faullü oyun, şiddetli hareket ve bariz gol şansının engellenmesi gibi kriterler incelenir."),
        "dogso": ("12.4", "Bariz gol şansının engellenmesinde ihlalin yeri, kaleye uzaklık, hücum yönü, topu kontrol etme/elde etme ihtimali ve savunmacı sayısı gibi kriterler birlikte değerlendirilir."),
    },
    13: {"default": ("13.1–13.3", "Direkt ve endirekt serbest vuruş türleri, uygulama prosedürü ve ihlal/yaptırımlar." )},
    14: {
        "default": ("14.1–14.3", "Penaltı vuruşunun prosedürü, oyuncuların konumu, vuruşun uygulanması ve ihlal/yaptırımlar."),
        "penalty": ("14.1–14.3", "Penaltının verilmesi Law 12'deki doğrudan serbest vuruş gerektiren ihlale dayanır; vuruşun uygulanışı, kalecinin ve diğer oyuncuların konumu ile ihlaller ayrıca kontrol edilir."),
    },
    15: {"default": ("15.1–15.2", "Taç atışının uygulanması, prosedür ve usulsüz taç atışındaki yaptırım." )},
    16: {"default": ("16.1–16.2", "Kale vuruşunun uygulanması, topun konumu, rakiplerin konumu ve ihlal/yaptırımlar." )},
    17: {"default": ("17.1–17.2", "Köşe vuruşunun uygulanması ve prosedür/ihlal hükümleri." )},
}

KEYWORDS = {
    1: ["saha", "çizgi", "ceza alanı", "ceza sahası", "field of play", "penalty area", "goal area"],
    2: ["top", "futbol topu", "ball", "top patladı", "top bozuk"],
    3: ["oyuncu", "yedek", "değişiklik", "oyuncu değişikliği", "substitute", "substitution", "kaptan", "captain"],
    4: ["forma", "krampon", "tekmelik", "takı", "kolye", "küpe", "ekipman", "equipment", "jewellery", "jewelry"],
    5: ["hakem", "orta hakem", "hakemin kararı", "referee", "avantaj", "advantage", "düdük"],
    6: ["yardımcı hakem", "dördüncü hakem", "var", "video hakem", "video yardımcı hakem", "assistant referee", "fourth official", "var referee"],
    7: ["süre", "uzatma", "devre", "ilk yarı", "ikinci yarı", "maç süresi", "time", "added time", "half-time", "half time"],
    8: ["başlama", "başlama vuruşu", "santra", "hakem atışı", "hava atışı", "restart", "kick-off", "kickoff", "dropped ball"],
    9: ["top dışarı", "taç çizgisi", "kale çizgisi", "top çizgiyi geçti", "top oyunda mı", "out of play", "ball out", "goal line", "touchline"],
    10: ["gol", "gol mü", "gol oldu mu", "gol kararı", "skor", "kazanan", "seri penaltı", "penalty shootout", "goal awarded"],
    11: ["ofsayt", "ofsayt mı", "ofsayt mi", "offside", "onside", "ofsayt pozisyonu", "aktif ofsayt", "pasif ofsayt"],
    12: ["faul", "faul mü", "foul", "tekme", "itme", "çekme", "tackle", "müdahale", "elle oynama", "el", "handball", "hand", "dirsek", "kırmızı", "kirmizi", "red card", "sarı", "sari", "yellow card", "sportmenlik dışı", "violent conduct", "dogso", "bariz gol şansı"],
    13: ["serbest vuruş", "direkt serbest", "endirekt serbest", "free kick", "direct free kick", "indirect free kick", "duvar", "baraj"],
    14: ["penaltı", "penalti", "penaltı mı", "penalti mi", "penaltı vuruşu", "penalty kick", "penalty", "kaleci çizgisi", "penaltı atışı"],
    15: ["taç", "taç atışı", "throw-in", "throw in", "taç nasıl kullanılır"],
    16: ["kale vuruşu", "kale atışı", "goal kick", "goal-kick"],
    17: ["korner", "köşe vuruşu", "corner", "corner kick"],
}

VAR_TERMS = ["var", "video hakem", "video assistant referee", "inceleme", "review", "kontrol", "check", "hakem monitörü", "on-field review", "var protokolü"]


def _law_label(numbers):
    return " / ".join(f"IFAB Law {n} – {LAWS[n]}" for n in sorted(set(numbers)))


def _find_laws(text: str):
    t = (text or "").lower()
    scores = {}
    for law, words in KEYWORDS.items():
        score = sum((2 if " " in word else 1) for word in words if word in t)
        if score:
            scores[law] = score
    for match in re.findall(r"(?:law|kural|madde)\s*(?:no\.?\s*)?(\d{1,2})", t):
        n = int(match)
        if n in LAWS:
            scores[n] = scores.get(n, 0) + 10
    return [n for n, _ in sorted(scores.items(), key=lambda item: (-item[1], item[0]))]


def _subrule_for(law, text):
    t = (text or "").lower()
    if law == 12:
        if any(x in t for x in ["elle oynama", "el", "handball", "hand"]):
            return SUBRULES[12]["handball"]
        if any(x in t for x in ["kırmızı", "kirmizi", "red card", "sarı", "sari", "yellow card"]):
            if any(x in t for x in ["dogso", "bariz gol şansı", "bariz gol"]):
                return SUBRULES[12]["dogso"]
            return SUBRULES[12]["discipline"]
        return SUBRULES[12]["foul"]
    if law == 11:
        return SUBRULES[11]["offside"]
    if law == 14:
        return SUBRULES[14]["penalty"]
    return SUBRULES[law]["default"]


def analyze_text(text: str) -> dict:
    t = (text or "").strip()
    laws = _find_laws(t)
    has_var = any(term in t.lower() for term in VAR_TERMS)

    if not laws:
        return {
            "decision": "GÖRÜNTÜ / DETAY GEREKLİ",
            "law": "IFAB Laws of the Game 2026/27",
            "subrule": "Genel",
            "explanation": "Sorunun hangi oyun kuralına ait olduğu metinden kesin olarak belirlenemedi.",
            "reason": "Pozisyonun videosunu/görselini veya olayı daha ayrıntılı paylaşın.",
            "confidence": "DÜŞÜK",
            "laws": list(LAWS.keys()),
            "var_relevant": has_var,
        }

    primary = laws[:4]
    law_text = _law_label(primary)
    if has_var:
        law_text += " / VAR protokolü"

    subrule_no, explanation = _subrule_for(primary[0], t)

    if 11 in primary:
        reason = "Ofsayt için topun oynandığı an, oyuncunun konumu ve oyuna/rakibe etkisi görüntü üzerinden kontrol edilmelidir."
    elif 14 in primary:
        reason = "Penaltı için önce Law 12 kapsamında ihlal olup olmadığı ve ihlalin ceza alanı içinde gerçekleşip gerçekleşmediği kontrol edilmelidir; ardından Law 14 prosedürü uygulanır."
    elif 12 in primary:
        reason = "Temasın niteliği, müdahalenin dikkatsiz/kontrolsüz/aşırı kuvvetli olup olmadığı ve varsa disiplin kriterleri birlikte değerlendirilmelidir."
    else:
        reason = "Olayın ilgili Law ve alt hükümleri birlikte değerlendirilmelidir. Kesin görsel karar için pozisyon görüntüsü gerekir."

    if has_var:
        reason += " VAR varsa ilgili olayın VAR protokolü kapsamında incelemeye uygun olup olmadığı ayrıca kontrol edilmelidir."

    return {
        "decision": "GÖRÜNTÜ GEREKLİ",
        "law": law_text,
        "subrule": subrule_no,
        "explanation": explanation,
        "reason": reason,
        "confidence": "DÜŞÜK",
        "laws": primary,
        "var_relevant": has_var,
    }


def format_reply(result: dict) -> str:
    return (
        "⚽ FAIR CHECK\n\n"
        f"Karar: {result['decision']}\n"
        f"📖 {result['law']}\n"
        f"📌 Alt kural: {result['subrule']}\n\n"
        f"📚 Kural açıklaması: {result['explanation']}\n\n"
        f"🔎 Değerlendirme: {result['reason']}\n\n"
        f"Güven: {result['confidence']}\n"
        "ℹ️ FairCheck, IFAB Laws of the Game 2026/27 çerçevesinde ilgili kural ve alt hükümleri eşleştirir. Metin tek başına kesin görsel hakem kararı için yeterli değildir."
    )
