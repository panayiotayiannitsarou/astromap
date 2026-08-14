import streamlit as st
import pandas as pd
from parser import parse_astrodienst_pdf
from prompts import build_master_prompt, fmt
from docx_builder import build_audit_docx, build_analysis_docx
from generator import generate_analysis
from reference_loader import docx_text, load_default_references
from astrology import movement_text

st.set_page_config(page_title="AstroCheck Pro", page_icon="✦", layout="wide")
st.markdown("""<style>
.stApp{background:#f5f7f3}.block-container{max-width:1180px;padding-top:2rem}.hero{background:#19332f;color:white;border-radius:22px;padding:30px 34px;margin-bottom:18px}.hero h1{margin:0 0 8px;font-family:Georgia;font-size:42px}.hero p{color:#dce8e2}.ok{padding:14px 16px;background:#e5f2e7;border-left:5px solid #39704c;border-radius:8px}.warn{padding:14px 16px;background:#fff1dd;border-left:5px solid #b7791f;border-radius:8px}div[data-testid="stMetric"]{background:white;border:1px solid #dce4df;padding:12px;border-radius:12px}</style>""",unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>AstroCheck Pro</h1><p>Από το Astrodienst PDF σε ελεγμένα δεδομένα, πλήρεις οδηγίες και Word — με υποχρεωτική καταγραφή τετραγώνων και αντιθέσεων.</p></div>',unsafe_allow_html=True)

if 'chart' not in st.session_state: st.session_state.chart=None
if 'analysis' not in st.session_state: st.session_state.analysis=''

try:
    default_instructions_text, default_style_text = load_default_references()
except Exception as e:
    st.error(f"Σφάλμα ενσωματωμένων αρχείων: {e}")
    st.stop()

with st.sidebar:
    st.header("Πρόοδος")
    st.write("1. PDF και αρχεία")
    st.write("2. Μαθηματικός έλεγχος")
    st.write("3. Προσωπικό πλαίσιο")
    st.write("4. Δημιουργία")
    st.caption("Τα δεδομένα επεξεργάζονται στη συνεδρία και δεν αποθηκεύονται από την εφαρμογή.")

tab1,tab2,tab3,tab4,tab5=st.tabs(["1 · Αρχεία","2 · Έλεγχος","3 · Προσωπικό πλαίσιο","4 · Δημιουργία","5 · Λήψη Word"])

with tab1:
    st.subheader("Ανέβασε μόνο το νέο PDF")
    st.success("✓ Οι οδηγίες v4 και το πρότυπο της Έλενας είναι μόνιμα ενσωματωμένα.")
    pdf=st.file_uploader("Νέο Astrodienst Data Sheet",type=['pdf'],key='pdf')
    with st.expander("Προχωρημένα: προαιρετική προσωρινή αντικατάσταση"):
        instructions=st.file_uploader("Νεότερες οδηγίες",type=['docx'],key='instructions')
        style=st.file_uploader("Νεότερο πρότυπο ύφους",type=['docx'],key='style')
    if pdf and st.button("Ανάγνωση και έλεγχος PDF",type="primary",use_container_width=True):
        try:
            st.session_state.chart=parse_astrodienst_pdf(pdf.getvalue(),pdf.name)
            st.session_state.analysis=''
            st.success("Το PDF διαβάστηκε. Συνέχισε στην καρτέλα «2 · Έλεγχος».")
        except Exception as e: st.error(f"Η ανάγνωση σταμάτησε με ασφάλεια: {e}")

instructions_text = docx_text(instructions.getvalue()) if instructions else default_instructions_text
style_text = docx_text(style.getvalue()) if style else default_style_text
instructions_name = instructions.name if instructions else "Ενσωματωμένες οδηγίες v4"
style_name = style.name if style else "Ενσωματωμένο πρότυπο Έλενας"

chart=st.session_state.chart
with tab2:
    if not chart: st.warning("Πρώτα ανέβασε και έλεγξε το PDF στην καρτέλα 1.")
    else:
        hard=[a for a in chart.aspects if a.aspect in ('Τετράγωνο','Αντίθεση')]
        a,b,c,d=st.columns(4); a.metric("Πλανήτες/σημεία",len(chart.points)); b.metric("Ακμές",len(chart.cusps)); c.metric("Όψεις Astrodienst",len(chart.aspects)); d.metric("Τετράγωνα/αντιθέσεις",len(hard))
        if chart.warnings:
            for w in chart.warnings: st.markdown(f'<div class="warn">⚠ {w}</div>',unsafe_allow_html=True)
        else: st.markdown('<div class="ok">✓ Αναγνωρίστηκαν 12 ακμές και ο πίνακας δυναμικών όψεων.</div>',unsafe_allow_html=True)
        st.subheader("Βασικά στοιχεία")
        st.write({"Όνομα":chart.name,"Ημερομηνία":chart.date,"Ώρα":chart.time,"Τόπος":chart.place,"Σύστημα":chart.house_system})
        with st.expander("Πλανήτες και τεχνική τοποθέτηση σε Οίκους"):
            st.dataframe(pd.DataFrame([{"Σημείο":p.name,"Θέση":fmt(p),"Οίκος":p.house,"Κίνηση":movement_text(p)} for p in chart.points]),use_container_width=True,hide_index=True)
        st.subheader("Υποχρεωτικά τετράγωνα και αντιθέσεις")
        st.dataframe(pd.DataFrame([{"Ζεύγος":f"{x.first}–{x.second}","Όψη":x.aspect,"Orb":x.orb_text,"Βαρύτητα":x.weight,"Πηγή":x.source} for x in hard]),use_container_width=True,hide_index=True)
        confirm=st.checkbox("Επιβεβαίωσα οπτικά ότι οι γραμμές συμφωνούν με τον πίνακα Astrodienst",key='confirmed')
        if not confirm: st.caption("Η τελική δημιουργία θα παραμείνει κλειδωμένη μέχρι την επιβεβαίωση.")

with tab3:
    st.subheader("Πληροφορίες που επιτρέπεται να χρησιμοποιηθούν")
    name_override=st.text_input("Όνομα για το τελικό έγγραφο",value=chart.name if chart else "")
    profession=st.text_input("Επάγγελμα και σπουδές")
    family=st.text_input("Σχέσεις και οικογενειακή κατάσταση")
    projects=st.text_area("Σημαντικά έργα, ενδιαφέροντα ή στόχοι")
    habits=st.text_area("Εργασιακές συνήθειες και καθημερινότητα")
    experiences=st.text_area("Εμπειρίες που θέλεις να ενσωματωθούν")
    language=st.selectbox("Γλώσσα τελικής ανάλυσης",["Ελληνικά","Αγγλικά"])
    st.caption("Ό,τι δεν γράψεις εδώ δεν πρέπει να παρουσιαστεί ως γνωστό προσωπικό γεγονός.")

personal={"Όνομα":name_override,"Επάγγελμα και σπουδές":profession,"Οικογενειακή κατάσταση":family,"Έργα/ενδιαφέροντα":projects,"Εργασιακές συνήθειες":habits,"Εμπειρίες":experiences}
prompt=''
if chart:
    prompt=build_master_prompt(chart,personal,language,instructions_text,style_text,instructions_name,style_name)

with tab4:
    st.subheader("Δημιουργία πλήρους ανάλυσης")
    if not chart: st.warning("Δεν υπάρχει ελεγμένος χάρτης.")
    else:
        checklist={"12 ακμές":len(chart.cusps)==12,"Βόρειος Δεσμός":any(p.name=='Βόρειος Δεσμός' for p in chart.points),"Νότιος Δεσμός":any(p.name=='Νότιος Δεσμός' for p in chart.points),"Πίνακας όψεων":bool(chart.aspects),"Χειροκίνητη επιβεβαίωση":st.session_state.get('confirmed',False),"Οδηγίες v4 μόνιμα ενσωματωμένες":bool(instructions_text),"Πρότυπο Έλενας μόνιμα ενσωματωμένο":bool(style_text)}
        st.dataframe(pd.DataFrame([{"Έλεγχος":k,"Κατάσταση":"✓" if v else "Λείπει"} for k,v in checklist.items()]),use_container_width=True,hide_index=True)
        with st.expander("Προεπισκόπηση πλήρους εντολής"): st.text_area("",prompt,height=320,label_visibility='collapsed')
        st.download_button("Λήψη πλήρους εντολής (.txt)",prompt,file_name="AstroCheck_Master_Prompt.txt",use_container_width=True)
        api=st.text_input("Προαιρετικά: OpenAI API key για αυτόματη συγγραφή",type="password",help="Δεν αποθηκεύεται. Χωρίς κλειδί κατεβάζεις την πλήρη εντολή και τη χρησιμοποιείς στο ChatGPT.")
        ready=all(checklist.values())
        if st.button("Δημιουργία πλήρους ανάλυσης",type="primary",disabled=not ready or not api,use_container_width=True):
            with st.spinner("Δημιουργείται η ανάλυση των 12 Οίκων…"):
                try: st.session_state.analysis=generate_analysis(api,prompt); st.success("Η ανάλυση δημιουργήθηκε. Πήγαινε στην καρτέλα 5.")
                except Exception as e: st.error(f"Η δημιουργία απέτυχε: {e}")
        if not ready: st.warning("Η αυτόματη δημιουργία παραμένει κλειδωμένη μέχρι να ολοκληρωθούν όλοι οι έλεγχοι.")

with tab5:
    st.subheader("Λήψη αρχείων")
    if chart:
        audit=build_audit_docx(chart,personal,prompt)
        st.download_button("Λήψη δελτίου ελέγχου και πλήρους εντολής (Word)",audit,file_name="AstroCheck_Elegxos_kai_Odigies.docx",use_container_width=True)
    if st.session_state.analysis:
        st.text_area("Προεπισκόπηση ανάλυσης",st.session_state.analysis,height=420)
        final_doc=build_analysis_docx(name_override or chart.name,st.session_state.analysis)
        st.download_button("Λήψη πλήρους ανάλυσης (Word)",final_doc,file_name="Pliris_Astrologiki_Analysi.docx",type="primary",use_container_width=True)
    else: st.info("Μετά την αυτόματη δημιουργία θα εμφανιστεί εδώ το τελικό Word.")
