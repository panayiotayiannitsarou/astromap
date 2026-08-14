from astrology import RULERS, angular_distance, degree_theory, orb_to_text

def fmt(p):
    rx = " ανάδρομος" if p.retrograde else ""
    return f"{p.sign} {p.degree}°{p.minute:02d}′{p.second:02d}″{rx}"

def ruler_block(chart, cusp):
    modern, traditional = RULERS[cusp.sign]
    ruler = next((p for p in chart.points if p.name == modern), None)
    trad = f" · παραδοσιακά {traditional}" if traditional else ""
    if not ruler: return f"{modern}{trad} — δεν εντοπίστηκε στα δεδομένα"
    aspects = [a for a in chart.aspects if ruler.name in (a.first,a.second)]
    aspect_text = "; ".join(f"{a.first}–{a.second} {a.aspect}, orb {a.orb_text}, {a.weight}" for a in aspects) or "καμία επιβεβαιωμένη όψη"
    return f"{modern}{trad}. Θέση: {fmt(ruler)}, {ruler.house}ος Οίκος. Όψεις κυβερνήτη: {aspect_text}"

def house_section(chart, number):
    cusp=chart.cusps[number-1]; nxt=chart.cusps[number%12]
    planets=[p for p in chart.points if p.house==number and p.kind in ("planet","node")]
    involved={p.name for p in planets}
    aspects=[a for a in chart.aspects if a.first in involved or a.second in involved]
    hard=[a for a in aspects if a.aspect in ("Τετράγωνο","Αντίθεση")]
    other=[a for a in aspects if a not in hard]
    near=[]
    for p in planets:
        distance=(nxt.absolute-p.absolute)%360
        if distance <= 5:
            near.append(f"{p.name}: τεχνικά στον {number}ο, απόσταση {orb_to_text(distance)} από την επόμενη ακμή· μπορεί συμπληρωματικά να επηρεάζει τον {number%12+1}ο.")
    plist="\n".join(f"- {p.name}: {fmt(p)} · {degree_theory(p)}" for p in planets) or "- Κανένας πλανήτης."
    def alines(items): return "\n".join(f"- {a.first}–{a.second}: {a.aspect}, orb {a.orb_text}, {a.weight}, πηγή: {a.source}" for a in items) or "- Καμία."
    return f"""{number}ος ΟΙΚΟΣ
Ακμή και έκταση: {fmt(cusp)} → {fmt(nxt)}.
Πλανήτες/σημεία:
{plist}
Κύριος κυβερνήτης:
{ruler_block(chart,cusp)}
Πλανήτες κοντά σε επόμενη ακμή:
{chr(10).join('- '+x for x in near) if near else '- Κανένας σε απόσταση έως 5°.'}
ΥΠΟΧΡΕΩΤΙΚΑ τετράγωνα και αντιθέσεις:
{alines(hard)}
Άλλες επιβεβαιωμένες κύριες όψεις:
{alines(other)}

Στη συγγραφή αυτού του Οίκου συμπερίλαβε υποχρεωτικά: «Σύνθεση με τον υπόλοιπο χάρτη», «Η πρακτική εφαρμογή» και πλαίσιο σύνοψης με Βασική δύναμη, Βασική πρόκληση, Κυβερνήτη και Τελικό συμπέρασμα."""

def build_master_prompt(chart, personal, language, instructions_name, style_name):
    personal_text="\n".join(f"- {k}: {v}" for k,v in personal.items() if v) or "- Δεν δόθηκαν ακόμη προσωπικές πληροφορίες. Ζήτησε τες πριν από τη συγγραφή."
    aspect_appendix="\n".join(f"- {a.first}–{a.second}: {a.aspect}, orb {a.orb_text}, {a.weight}, {a.source}" for a in chart.aspects) or "- Δεν αναγνωρίστηκαν όψεις. Σταμάτησε και ζήτησε έλεγχο."
    houses="\n\n".join(house_section(chart,i) for i in range(1,13))
    return f"""ΔΕΣΜΕΥΤΙΚΗ ΕΝΤΟΛΗ
Χρησιμοποίησε το «{instructions_name}» ως δεσμευτική προδιαγραφή και το «{style_name}» αποκλειστικά ως πρότυπο ύφους, βάθους, δομής και μορφοποίησης. Όλα τα αστρολογικά δεδομένα προέρχονται αποκλειστικά από το νέο PDF και τον παρακάτω ελεγμένο πίνακα. Μην μεταφέρεις δεδομένα ή προσωπικές πληροφορίες από το πρότυπο.

Γλώσσα τελικού Word: {language}.
Όνομα: {chart.name}
Ημερομηνία: {chart.date} · Ώρα: {chart.time} · Τόπος: {chart.place}
Σύστημα Οίκων: {chart.house_system}

ΠΡΟΣΩΠΙΚΟ ΠΛΑΙΣΙΟ
{personal_text}

ΥΠΟΧΡΕΩΤΙΚΟΙ ΚΑΝΟΝΕΣ
1. Αν λείπει ή αμφισβητείται προσωπικό στοιχείο, ζήτησε επιβεβαίωση. Μην επινοήσεις εμπειρίες.
2. Μην παραλείψεις κανένα τετράγωνο ή αντίθεση του Astrodienst, ακόμη και όταν είναι πολύ πλατύ/δευτερεύον.
3. Η ίδια όψη πρέπει να έχει παντού το ίδιο orb και την ίδια κατηγορία.
4. Χρησιμοποίησε προσεκτική, πιθανική, μη μοιρολατρική και μη διαγνωστική γλώσσα.
5. Η Θεωρία των Μοιρών είναι μόνο συμπληρωματική και ακολουθεί ζώδιο, Οίκο, όψεις και κυβερνήτη.
6. Κάθε Οίκος να είναι συνεχές συνθετικό κείμενο και όχι ασύνδετη λίστα.

ΕΛΕΓΜΕΝΑ ΔΕΔΟΜΕΝΑ ΑΝΑ ΟΙΚΟ
{houses}

ΤΕΛΙΚΕΣ ΥΠΟΧΡΕΩΤΙΚΕΣ ΕΝΟΤΗΤΕΣ
- Τελική συνθετική εικόνα.
- Συμβολική κατεύθυνση εξέλιξης: Βόρειος/Νότιος Δεσμός, κυβερνήτης Βόρειου Δεσμού, επιβεβαιωμένες όψεις και πρακτική έκφραση.
- Προτάσεις προσωπικής ανάπτυξης και υποστήριξης, πρακτικές και μη διαγνωστικές.
- Παράρτημα επιβεβαιωμένων όψεων.
- Δεύτερος μαθηματικός, γλωσσικός και οπτικός έλεγχος πριν από την παράδοση.

ΠΑΡΑΡΤΗΜΑ ΕΠΙΒΕΒΑΙΩΜΕΝΩΝ ΟΨΕΩΝ — ΜΟΝΑΔΙΚΗ ΠΗΓΗ
{aspect_appendix}

ΜΟΡΦΟΠΟΙΗΣΗ
Παράδωσε καλαίσθητο Word με τίτλο, υπότιτλο, μεθοδολογία, βασικά δεδομένα, αρίθμηση σελίδων και κάθε Οίκο κατά προτίμηση σε νέα σελίδα. Κράτησε κάθε πλαίσιο σύνοψης ολόκληρο στην ίδια σελίδα."""

