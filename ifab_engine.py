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

KEYWORDS = {
    1: ["saha", "çizgi", "ceza alanı", "ceza sahası", "orta saha", "kale alanı", "field of play", "penalty area", "goal area"],
    2: ["top", "futbol topu", "ball", "top patladı", "top bozuk", "ikinci top", "yedek top"],
    3: ["oyuncu", "oyuncular", "yedek", "değişiklik", "oyuncu değişikliği", "substitute", "substitution", "kaptan", "captain", "7 oyuncu", "yedi oyuncu"],
    4: ["forma", "krampon", "tekmelik", "takı", "kolye", "küpe", "ekipman", "equipment", "jewellery", "jewelry", "shin pad"],
    5: ["hakem", "orta hakem", "hakemin kararı", "hakem ne yapmalı", "referee", "avantaj", "advantage", "düdük"],
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


def analyze_text(text: str) -> dict:
    t = (text or "").strip()
    laws = _find_laws(t)
    has_var = any(term in t.lower() for term in VAR_TERMS)

    if not laws:
        return {
            "decision": "GÖRÜNTÜ / DETAY GEREKLİ",
            "law": "IFAB Laws of the Game 2026/27",
            "reason": "Sorunun hangi oyun kuralına ait olduğu metinden kesin olarak belirlenemedi. Pozisyonun videosunu/görselini veya olayı daha ayrıntılı paylaşın.",
            "confidence": "DÜŞÜK",
            "laws": list(LAWS.keys()),
            "var_relevant": has_var,
        }

    primary = laws[:4]
    law_text = _law_label(primary)
    if has_var:
        law_text += " / VAR protokolü"

    if 11 in primary:
        reason = "Ofsayt değerlendirmesinde topun oynandığı an, ikinci son rakibin konumu, hücum oyuncusunun ofsayt pozisyonu ve oyuna/ rakibe etkisi değerlendirilmelidir. Görüntü olmadan kesin karar verilmez."
    elif 14 in primary:
        reason = "Penaltı değerlendirmesinde ihlalin ceza alanı içinde olup olmadığı ve doğrudan serbest vuruş gerektiren bir ihlal bulunup bulunmadığı incelenmelidir. Penaltı vuruşunun uygulanışında Law 14 kriterleri ayrıca kontrol edilir."
    elif 12 in primary:
        reason = "Faul ve disiplin değerlendirmesinde temas, müdahalenin niteliği, dikkatsiz/kontrolsüz/aşırı kuvvet kullanımı, ihlalin yeri ve gerekiyorsa kart veya DOGSO kriterleri birlikte değerlendirilmelidir."
    elif 8 in primary:
        reason = "Başlama ve yeniden başlatma şekli, topun ve oyuncuların konumu ile yeniden başlatmanın türü Law 8 hükümlerine göre kontrol edilmelidir."
    else:
        reason = "Olay birden fazla IFAB kuralını ilgilendirebilir. İlgili Law'lar birlikte değerlendirilmelidir; kesin görsel karar için pozisyon görüntüsü gerekir."

    if has_var:
        reason += " VAR söz konusuysa yalnızca protokolde incelemeye açık olaylar ve ilgili müdahale kriterleri ayrıca kontrol edilmelidir."

    return {
        "decision": "GÖRÜNTÜ GEREKLİ",
        "law": law_text,
        "reason": reason,
        "confidence": "DÜŞÜK",
        "laws": primary,
        "var_relevant": has_var,
    }


def format_reply(result: dict) -> str:
    return (
        "⚽ FAIR CHECK\n\n"
        f"Karar: {result['decision']}\n"
        f"📖 {result['law']}\n\n"
        f"Gerekçe: {result['reason']}\n\n"
        f"Güven: {result['confidence']}\n"
        "ℹ️ FairCheck, IFAB Laws of the Game 2026/27 çerçevesinde ilgili kural(lar)ı belirler. Metin tek başına kesin görsel hakem kararı için yeterli değildir."
    )
