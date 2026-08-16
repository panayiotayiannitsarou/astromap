"""
validator.py
=============
Ελέγχει το ΤΕΛΙΚΟ κείμενο ανάλυσης (πριν γίνει Word) ενάντια στο ελεγμένο
Chart -- δεν εμπιστεύεται ότι το μοντέλο ακολούθησε τις οδηγίες, το
επαληθεύει μηχανικά. Αυτό είναι το ίδιο ακριβώς λάθος που παρατηρήθηκε
χειροκίνητα (παρέλειψη όψεων παρά τις ρητές οδηγίες) -- ο σκοπός αυτού του
module είναι να μην ξαναπεράσει αθόρυβα.

v2: δύο προσθήκες, ύστερα από δύο συγκεκριμένα περιστατικά που η v1 δεν θα
είχε πιάσει:
  1. Ο μηχανικός έλεγχος κάλυπτε μόνο "Τετράγωνο"/"Αντίθεση". Μια σύνοδος με
     τον Ωροσκόπο ή το Μεσουράνημα (π.χ. Χείρωνας–Ωροσκόπος) δεν ελεγχόταν
     καθόλου, άρα η απουσία της δεν θα εμφανιζόταν ποτέ ως σφάλμα. Τώρα ο
     ορισμός του "mandatory" περιλαμβάνει και κάθε σύνοδο όπου συμμετέχει
     γωνία (astrology.OPPOSITE_ANGLE).
  2. Ο παλιός έλεγχος co-occurrence δεχόταν μια όψη ως "καλυμμένη" αν
     εμφανιζόταν ΟΠΟΥΔΗΠΟΤΕ στο κείμενο -- π.χ. μια όψη του κυβερνήτη ενός
     Οίκου που αναφέρεται μόνο στον Οίκο όπου φυσικά βρίσκεται ο πλανήτης,
     αλλά ποτέ στον Οίκο που ο ίδιος πλανήτης κυβερνά, περνούσε ως OK. Τώρα
     γίνεται ξεχωριστός έλεγχος ανά Οίκο (κανόνας 6Β): κάθε mandatory όψη
     πρέπει να εμφανίζεται μέσα στο τμήμα κειμένου κάθε Οίκου όπου το σημείο
     της είναι "involved" -- Οίκος-κατοικίας ΚΑΙ κάθε Οίκος που κυβερνά.

Η λήψη του τελικού Word πρέπει να παραμένει κλειδωμένη όσο
ValidationResult.ok είναι False.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field

from astrology import RULERS, OPPOSITE_ANGLE

REQUIRED_SECTIONS = [
    "Τελική συνθετική εικόνα",
    "Συμβολική κατεύθυνση εξέλιξης",
    "Προτάσεις προσωπικής ανάπτυξης",
    "Παράρτημα επιβεβαιωμένων όψεων",
]

ANGLE_NAMES = set(OPPOSITE_ANGLE.keys())  # {"Ωροσκόπος", "Μεσουράνημα"}

_HOUSE_PATTERNS = [
    re.compile(rf"\b{n}ος\s+Ο[ιί]κ", re.IGNORECASE) for n in range(1, 13)
]
# Εναλλακτική διατύπωση: "Οίκος 7", "ΟΙΚΟΣ 7"
_HOUSE_PATTERNS_ALT = [
    re.compile(rf"Ο[ιί]κ\w*\s+{n}\b") for n in range(1, 13)
]

_WINDOW = 350  # χαρακτήρες γύρω από κάθε εμφάνιση ονόματος, για αναζήτηση ταιριάσματος


@dataclass
class ValidationResult:
    ok: bool
    missing_houses: list = field(default_factory=list)
    missing_aspects: list = field(default_factory=list)      # εντελώς απούσες, πουθενά στο κείμενο
    suspect_aspects: list = field(default_factory=list)      # ονόματα υπάρχουν, orb όχι κοντά
    missing_from_appendix: list = field(default_factory=list)
    missing_sections: list = field(default_factory=list)
    missing_per_house: list = field(default_factory=list)    # (house_number, aspect) -- κανόνας 6Β

    def summary(self) -> str:
        if self.ok:
            return "✓ Η ανάλυση φαίνεται πλήρης: όλα τα υποχρεωτικά στοιχεία εντοπίστηκαν στο κείμενο, σε κάθε Οίκο που έπρεπε."
        parts = []
        if self.missing_houses:
            parts.append(f"{len(self.missing_houses)} Οίκοι δεν εντοπίστηκαν ({', '.join(map(str, self.missing_houses))})")
        if self.missing_aspects:
            parts.append(f"{len(self.missing_aspects)} υποχρεωτικές όψεις (τετράγωνα/αντιθέσεις/σύνοδοι με γωνία) λείπουν εντελώς")
        if self.suspect_aspects:
            parts.append(f"{len(self.suspect_aspects)} όψεις με ύποπτο ή απόν orb")
        if self.missing_from_appendix:
            parts.append(f"{len(self.missing_from_appendix)} όψεις δεν εντοπίστηκαν στο Παράρτημα")
        if self.missing_sections:
            parts.append(f"λείπουν οι ενότητες: {', '.join(self.missing_sections)}")
        if self.missing_per_house:
            parts.append(f"{len(self.missing_per_house)} όψεις κυβερνήτη λείπουν από συγκεκριμένο Οίκο (κανόνας 6Β)")
        return "Η ανάλυση δεν ολοκληρώθηκε: " + "· ".join(parts) + "."

    def details_lines(self) -> list[str]:
        lines = []
        for n in self.missing_houses:
            lines.append(f"Οίκος {n}: δεν βρέθηκε επικεφαλίδα στο κείμενο.")
        for a in self.missing_aspects:
            lines.append(f"{a.first}–{a.second} ({a.aspect}, orb {a.orb_text}): δεν αναφέρεται πουθενά.")
        for a in self.suspect_aspects:
            lines.append(f"{a.first}–{a.second}: αναφέρονται και τα δύο ονόματα, αλλά όχι το orb {a.orb_text} κοντά τους -- έλεγξε χειροκίνητα.")
        for a in self.missing_from_appendix:
            lines.append(f"{a.first}–{a.second}: δεν εντοπίστηκε μέσα στο Παράρτημα Επιβεβαιωμένων Όψεων.")
        for s in self.missing_sections:
            lines.append(f"Λείπει η υποχρεωτική ενότητα: «{s}».")
        for house_n, a in self.missing_per_house:
            lines.append(f"Οίκος {house_n}: η όψη {a.first}–{a.second} (orb {a.orb_text}) δεν αναφέρεται μέσα σε αυτόν τον Οίκο, παρότι εμπλέκει πλανήτη/κυβερνήτη του.")
        return lines


def _find_appendix(text: str) -> str:
    idx = text.find("Παράρτημα")
    return text[idx:] if idx != -1 else ""


def _co_occurs_with_orb(text: str, name_a: str, name_b: str, orb_text: str) -> tuple[bool, bool]:
    """Επιστρέφει (co_occurs, orb_found_nearby)."""
    co_occurs = False
    orb_found = False
    for m in re.finditer(re.escape(name_a), text):
        start = max(0, m.start() - _WINDOW)
        end = min(len(text), m.end() + _WINDOW)
        window = text[start:end]
        if name_b in window:
            co_occurs = True
            if orb_text in window:
                orb_found = True
                break
    return co_occurs, orb_found


def _house_segments(text: str) -> dict[int, str]:
    """Εντοπίζει το τμήμα κειμένου κάθε Οίκου (από την επικεφαλίδα του μέχρι
    την επόμενη), με αναζήτηση με σειρά 1..12 ώστε να μην μπερδεύονται
    αριθμοί Οίκων που αναφέρονται εν παρόδω αλλού στο κείμενο."""
    starts = {}
    cursor = 0
    for n in range(1, 13):
        m = _HOUSE_PATTERNS[n - 1].search(text, cursor) or _HOUSE_PATTERNS_ALT[n - 1].search(text, cursor)
        if not m:
            continue
        starts[n] = m.start()
        cursor = m.start() + 1
    segments = {}
    ordered = sorted(starts.items(), key=lambda kv: kv[1])
    for i, (n, start) in enumerate(ordered):
        end = ordered[i + 1][1] if i + 1 < len(ordered) else len(text)
        segments[n] = text[start:end]
    return segments


def _involved_points(chart, house_number: int) -> set[str]:
    """Ίδια λογική με prompts.house_section: πλανήτες μέσα στον Οίκο, κύριος
    και παραδοσιακός κυβερνήτης, και -- για τους Οίκους 1/7/4/10 -- η γωνία
    που ο ίδιος ο Οίκος ορίζει (κανόνας 6Β)."""
    cusp = chart.cusps[house_number - 1]
    planets = [p for p in chart.points if p.house == house_number and p.kind in ("planet", "node")]
    modern_ruler, traditional_ruler = RULERS[cusp.sign]
    involved = {p.name for p in planets}
    involved.add(modern_ruler)
    if traditional_ruler:
        involved.add(traditional_ruler)
    if house_number in (1, 7):
        involved.add("Ωροσκόπος")
    if house_number in (4, 10):
        involved.add("Μεσουράνημα")
    return involved


def validate_analysis(chart, analysis_text: str) -> ValidationResult:
    text = analysis_text

    missing_houses = []
    for n in range(1, 13):
        if _HOUSE_PATTERNS[n - 1].search(text) or _HOUSE_PATTERNS_ALT[n - 1].search(text):
            continue
        missing_houses.append(n)

    # v2: mandatory = τετράγωνα/αντιθέσεις (όπως πριν) ΣΥΝ κάθε σύνοδο όπου
    # συμμετέχει γωνία (Ωροσκόπος/Μεσουράνημα) -- πριν αγνοούνταν εντελώς.
    hard = [a for a in chart.aspects if a.aspect in ("Τετράγωνο", "Αντίθεση")]
    angle_conjunctions = [
        a for a in chart.aspects
        if a.aspect == "Σύνοδος" and (a.first in ANGLE_NAMES or a.second in ANGLE_NAMES)
    ]
    mandatory = hard + angle_conjunctions

    missing_aspects = []
    suspect_aspects = []
    for a in mandatory:
        co_occurs, orb_ok = _co_occurs_with_orb(text, a.first, a.second, a.orb_text)
        if not co_occurs:
            missing_aspects.append(a)
        elif not orb_ok:
            suspect_aspects.append(a)

    appendix_text = _find_appendix(text)
    missing_from_appendix = []
    if appendix_text:
        for a in mandatory:
            if a.first not in appendix_text or a.second not in appendix_text:
                missing_from_appendix.append(a)

    missing_sections = [s for s in REQUIRED_SECTIONS if s not in text]

    # v2: έλεγχος ανά Οίκο (κανόνας 6Β) -- κάθε mandatory όψη πρέπει να
    # εμφανίζεται ΜΕΣΑ στο τμήμα κειμένου κάθε Οίκου όπου εμπλέκεται
    # πλανήτης/κυβερνήτης/γωνία του, όχι απλώς κάπου στο έγγραφο.
    missing_per_house = []
    segments = _house_segments(text)
    for house_number in range(1, 13):
        segment = segments.get(house_number)
        if not segment:
            continue  # ήδη καταγράφηκε στο missing_houses
        involved = _involved_points(chart, house_number)
        for a in mandatory:
            if a.first not in involved and a.second not in involved:
                continue
            co_occurs, orb_ok = _co_occurs_with_orb(segment, a.first, a.second, a.orb_text)
            if not (co_occurs and orb_ok):
                missing_per_house.append((house_number, a))

    ok = not (missing_houses or missing_aspects or suspect_aspects
              or missing_from_appendix or missing_sections or missing_per_house)
    return ValidationResult(ok, missing_houses, missing_aspects, suspect_aspects,
                             missing_from_appendix, missing_sections, missing_per_house)
