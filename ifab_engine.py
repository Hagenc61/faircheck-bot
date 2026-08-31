import re


def analyze_text(text: str) -> dict:
    t = (text or "").lower()

    # This is a text-only pre-check. Visual decisions require the actual video/image.
    if any(x in t for x in ["ofsayt", "ofsayt mı", "ofsayt mi", "offside"]):
        return {
            "decision": "GÖRÜNTÜ GEREKLİ",
            "law": "IFAB Law 11 – Offside",
            "reason": "Ofsayt kararı için topun oynandığı an, ikinci son rakibin konumu ve oyuncunun oyuna müdahalesi görülmelidir.",
            "confidence": "DÜŞÜK",
        }

    if any(x in t for x in ["penaltı", "penalti", "penaltı mı", "penalti mi"]):
        return {
            "decision": "GÖRÜNTÜ GEREKLİ",
            "law": "IFAB Law 12/14 – Fouls and Misconduct / Penalty Kick",
            "reason": "Penaltı için ihlalin ceza alanı içinde gerçekleşip gerçekleşmediği ve doğrudan serbest vuruş gerektiren bir ihlal olup olmadığı görülmelidir.",
            "confidence": "DÜŞÜK",
        }

    if any(x in t for x in ["el", "elle oynama", "handball", "hand"]):
        return {
            "decision": "GÖRÜNTÜ GEREKLİ",
            "law": "IFAB Law 12 – Fouls and Misconduct",
            "reason": "El/kol ihlalinde topun kola temas şekli ve oyuncunun kolunu vücuda göre nasıl konumlandırdığı değerlendirilmelidir.",
            "confidence": "DÜŞÜK",
        }

    if any(x in t for x in ["faul", "faul mü", "foul", "tekme", "itme", "çekme", "tackle", "müdahale"]):
        return {
            "decision": "GÖRÜNTÜ GEREKLİ",
            "law": "IFAB Law 12 – Fouls and Misconduct",
            "reason": "Faul değerlendirmesinde temasın olup olmadığı ve müdahalenin dikkatsiz, kontrolsüz veya aşırı kuvvet içerip içermediği görülmelidir.",
            "confidence": "DÜŞÜK",
        }

    if any(x in t for x in ["kırmızı", "kirmizi", "red card", "sarı", "sari", "yellow card"]):
        return {
            "decision": "GÖRÜNTÜ GEREKLİ",
            "law": "IFAB Law 12 – Fouls and Misconduct",
            "reason": "Kart değerlendirmesi için ihlalin niteliği, şiddeti ve rakibin güvenliğine yönelik risk görülmelidir.",
            "confidence": "DÜŞÜK",
        }

    return {
        "decision": "POZİSYON GEREKLİ",
        "law": "IFAB Laws of the Game",
        "reason": "Sağlıklı bir değerlendirme için pozisyon videosunu veya görselini ve mümkünse hangi kararı sorguladığınızı paylaşın.",
        "confidence": "DÜŞÜK",
    }


def format_reply(result: dict) -> str:
    return (
        "⚽ FAIR CHECK\n\n"
        f"Karar: {result['decision']}\n"
        f"📖 {result['law']}\n\n"
        f"Gerekçe: {result['reason']}\n\n"
        f"Güven: {result['confidence']}\n"
        "ℹ️ Bu aşama metin tabanlı ön değerlendirmedir; kesin karar için görüntü gerekir."
    )
