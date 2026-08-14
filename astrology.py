from models import Aspect, Point

SIGNS = ["Κριός", "Ταύρος", "Δίδυμοι", "Καρκίνος", "Λέων", "Παρθένος", "Ζυγός", "Σκορπιός", "Τοξότης", "Αιγόκερως", "Υδροχόος", "Ιχθύες"]
SIGN_CODES = dict(zip("abcdefghijkl", SIGNS))
RULERS = {
    "Κριός": ("Άρης", None), "Ταύρος": ("Αφροδίτη", None), "Δίδυμοι": ("Ερμής", None),
    "Καρκίνος": ("Σελήνη", None), "Λέων": ("Ήλιος", None), "Παρθένος": ("Ερμής", None),
    "Ζυγός": ("Αφροδίτη", None), "Σκορπιός": ("Πλούτωνας", "Άρης"), "Τοξότης": ("Δίας", None),
    "Αιγόκερως": ("Κρόνος", None), "Υδροχόος": ("Ουρανός", "Κρόνος"), "Ιχθύες": ("Ποσειδώνας", "Δίας")
}
DEGREE_QUALITIES = {
    "Κριός":"πρωτοβουλία, τόλμη και αμεσότητα", "Ταύρος":"σταθερότητα, ασφάλεια, αισθησιασμός και πρακτικότητα",
    "Δίδυμοι":"περιέργεια, επικοινωνία και πνευματική ευελιξία", "Καρκίνος":"ευαισθησία, προστασία και συναισθηματική μνήμη",
    "Λέων":"δημιουργικότητα, περηφάνια και ανάγκη έκφρασης", "Παρθένος":"ανάλυση, ακρίβεια και πρακτική βελτίωση",
    "Ζυγός":"συνεργασία, αρμονία και αισθητική", "Σκορπιός":"βάθος, διεισδυτικότητα και μεταμόρφωση",
    "Τοξότης":"αναζήτηση νοήματος, ελευθερία και διεύρυνση", "Αιγόκερως":"σοβαρότητα, αυτοέλεγχος, φιλοδοξία και αξιοπιστία",
    "Υδροχόος":"ανεξαρτησία, πρωτοτυπία και συλλογική σκέψη", "Ιχθύες":"διαίσθηση, φαντασία και συμπόνια"
}

def absolute(sign: str, degree: int, minute: int, second: int) -> float:
    return SIGNS.index(sign) * 30 + degree + minute / 60 + second / 3600

def angular_distance(a: float, b: float) -> float:
    raw = abs(a - b) % 360
    return min(raw, 360 - raw)

def house_of(value: float, cusps: list[Point]) -> int:
    for i in range(12):
        start, end = cusps[i].absolute, cusps[(i + 1) % 12].absolute
        if (start < end and start <= value < end) or (start >= end and (value >= start or value < end)):
            return i + 1
    raise ValueError("Δεν ήταν δυνατός ο υπολογισμός του Οίκου.")

def orb_weight(orb: float) -> str:
    if orb < 2: return "Στενή/ισχυρή"
    if orb < 4: return "Κανονική"
    if orb <= 7: return "Πλατιά αλλά έγκυρη"
    return "Πολύ πλατιά/δευτερεύουσα"

def orb_to_text(orb: float) -> str:
    total = round(abs(orb) * 3600)
    d, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{d}°{m:02d}′{s:02d}″"

def degree_theory(p: Point) -> str:
    if p.degree == 0:
        return "0°: αρχική, “καθαρή” εκδήλωση του πραγματικού ζωδίου"
    sign = SIGNS[(p.degree - 1) % 12]
    extra = " Παράλληλα μπορεί να εξεταστεί ως κρίσιμη/αναιρετική μοίρα." if p.degree == 29 else ""
    return f"{p.degree}° = συμβολική μοίρα {sign}: {DEGREE_QUALITIES[sign]}.{extra}"

def opposite_node(node: Point) -> Point:
    value = (node.absolute + 180) % 360
    si = int(value // 30)
    rem = value - si * 30
    degree = int(rem); minute = int((rem-degree)*60); second = round((((rem-degree)*60)-minute)*60)
    return Point("SN", "Νότιος Δεσμός", SIGNS[si], degree, minute, second, value, kind="node")

