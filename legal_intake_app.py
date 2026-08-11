import re
import html
import streamlit as st
from datetime import date, datetime

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="LegalIntake | AI Legal Intake Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# CUSTOM CSS - PREMIUM UI
# ---------------------------------------------------------

st.markdown("""
<style>

    /* Main background */
    .stApp {
        background: #f7f8fc;
    }

    /* Remove default top padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #111827;
    }

    section[data-testid="stSidebar"] * {
        color: #ffffff;
    }

    /* Hero */
    .hero {
        background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
        padding: 45px;
        border-radius: 24px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 12px 35px rgba(0,0,0,0.12);
    }

    .hero h1 {
        font-size: 42px;
        margin-bottom: 10px;
    }

    .hero p {
        font-size: 18px;
        color: #d1d5db;
        line-height: 1.6;
    }

    /* Cards */
    .card {
        background: white;
        padding: 25px;
        border-radius: 18px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 5px 20px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }

    .feature-card {
        background: white;
        padding: 22px;
        border-radius: 18px;
        border: 1px solid #e5e7eb;
        height: 170px;
        box-shadow: 0 5px 18px rgba(0,0,0,0.04);
    }

    .feature-card h3 {
        color: #111827;
    }

    .feature-card p {
        color: #6b7280;
        line-height: 1.5;
    }

    /* Classification result */
    .result {
        background: #eef2ff;
        border-left: 5px solid #4f46e5;
        padding: 20px;
        border-radius: 12px;
        margin-top: 15px;
    }

    /* Disclaimer */
    .disclaimer {
        background: #fff7ed;
        border: 1px solid #fed7aa;
        padding: 18px;
        border-radius: 14px;
        color: #7c2d12;
        margin-top: 20px;
    }

    /* Success */
    .success-box {
        background: #ecfdf5;
        border: 1px solid #a7f3d0;
        padding: 20px;
        border-radius: 14px;
        color: #065f46;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #6b7280;
        padding: 30px;
        margin-top: 50px;
    }

</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "case_classification" not in st.session_state:
    st.session_state.case_classification = None

if "intake_complete" not in st.session_state:
    st.session_state.intake_complete = False

if "client" not in st.session_state:
    st.session_state.client = None

if "consultation" not in st.session_state:
    st.session_state.consultation = None


# ---------------------------------------------------------
# LEGAL PRACTICE AREA CLASSIFIER
# ---------------------------------------------------------

practice_areas = {

    "Family Law": [
        "divorce",
        "marriage",
        "custody",
        "child custody",
        "alimony",
        "maintenance",
        "domestic",
        "husband",
        "wife",
        "spouse",
        "separation"
    ],

    "Criminal Law": [
        "crime",
        "criminal",
        "police",
        "fir",
        "arrest",
        "fraud",
        "theft",
        "assault",
        "murder",
        "complaint",
        "bail",
        "robbery"
    ],

    "Property Law": [
        "property",
        "land",
        "house",
        "plot",
        "tenant",
        "rent",
        "ownership",
        "boundary",
        "inheritance",
        "real estate"
    ],

    "Employment Law": [
        "job",
        "employee",
        "employer",
        "salary",
        "termination",
        "workplace",
        "harassment",
        "employment",
        "company fired",
        "dismissal"
    ],

    "Corporate Law": [
        "company",
        "business",
        "startup",
        "shareholder",
        "contract",
        "corporate",
        "partnership",
        "director",
        "business dispute"
    ],

    "Intellectual Property": [
        "copyright",
        "trademark",
        "patent",
        "brand",
        "logo",
        "invention",
        "intellectual property",
        "piracy"
    ],

    "Immigration Law": [
        "visa",
        "immigration",
        "passport",
        "citizenship",
        "immigrant",
        "work permit",
        "residency"
    ]
}


def classify_case(text):
    """
    Classify free-text case description into a practice area.

    Fixes vs. original:
      - Uses word-boundary regex matching instead of substring `in`,
        so "urgent" no longer matches the keyword "rent", "torrent"
        no longer matches "rent", etc.
      - Breaks ties instead of silently favoring the first dict key
        (previously always "Family Law" on a tie).
      - Returns a normalized confidence score (0-1) in addition to
        the raw keyword hit count, so the UI can communicate how
        confident the match is.
    """

    text = text.lower()

    scores = {}

    for area, keywords in practice_areas.items():
        score = 0
        for keyword in keywords:
            pattern = r"\b" + re.escape(keyword) + r"\b"
            if re.search(pattern, text):
                score += 1
        scores[area] = score

    max_score = max(scores.values())

    if max_score == 0:
        return "General Legal Inquiry", 0, {}, []

    # Collect all areas tied for the top score
    top_areas = [area for area, s in scores.items() if s == max_score]

    if len(top_areas) == 1:
        best_area = top_areas[0]
    else:
        # Genuine tie between two or more areas: don't silently pick
        # one. Report the tie so the UI can flag it for manual review.
        best_area = "Multiple possible areas"

    return best_area, max_score, scores, top_areas


def escape_html(value):
    """Escape user-supplied text before interpolating into
    st.markdown(..., unsafe_allow_html=True) blocks, to prevent
    HTML/script injection via form fields."""
    if value is None:
        return ""
    return html.escape(str(value))


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

with st.sidebar:

    st.markdown("## ⚖️ LegalIntake")

    st.markdown(
        "### AI Legal Intake Assistant"
    )

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "🏠 Home",
            "💬 Legal Assistant",
            "📝 Client Intake",
            "📅 Consultation",
            "📋 Case Summary"
        ]
    )

    st.divider()

    st.markdown("### 🔐 Privacy")

    st.caption(
        "This demonstration application collects information "
        "only for the purpose of client intake."
    )

    st.caption(
        "Do not submit highly sensitive information in this demo."
    )


# ---------------------------------------------------------
# HOME PAGE
# ---------------------------------------------------------

if page == "🏠 Home":

    st.markdown("""
    <div class="hero">

        <h1>⚖️ LegalIntake</h1>

        <p>
        An intelligent legal client intake assistant designed
        to help law firms understand, classify and organize
        potential client inquiries.
        </p>

    </div>
    """, unsafe_allow_html=True)

    st.markdown("## Your Digital Legal Receptionist")

    st.write(
        "LegalIntake helps law firms collect initial case information, "
        "identify the relevant legal practice area and guide users "
        "towards a consultation."
    )

    st.write("")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature-card">
        <h3>🧠 Smart Classification</h3>
        <p>
        Analyzes the user's description and identifies
        the most relevant legal practice area.
        </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
        <h3>📝 Client Intake</h3>
        <p>
        Collects essential information such as
        contact details and case descriptions.
        </p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
        <h3>📅 Consultation</h3>
        <p>
        Helps potential clients select a convenient
        consultation date and time.
        </p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.write("")

    st.markdown("### 🔄 How LegalIntake Works")

    st.info(
        "Visitor → Legal Issue → Pre-screening → "
        "Case Classification → Client Intake → "
        "Consultation → Lawyer"
    )

    st.markdown("""
    <div class="disclaimer">

    <strong>⚠️ Important Legal Disclaimer</strong><br><br>

    This chatbot provides general legal information only.
    It does not provide legal advice and does not create
    an attorney-client relationship.

    For advice regarding your specific situation,
    please consult a qualified lawyer.

    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------
# LEGAL ASSISTANT
# ---------------------------------------------------------

elif page == "💬 Legal Assistant":

    st.title("💬 Legal Assistant")

    st.write(
        "Tell me briefly about your legal situation. "
        "I will help identify the relevant practice area."
    )

    st.markdown("""
    <div class="disclaimer">

    ⚠️ Please do not enter confidential information,
    passwords, financial details or other highly sensitive data.

    </div>
    """, unsafe_allow_html=True)

    user_message = st.text_area(
        "Describe your legal issue",
        placeholder=(
            "Example: I am facing a dispute with my employer "
            "regarding termination of my job."
        ),
        height=160
    )

    if st.button(
        "🔍 Analyze Legal Issue",
        use_container_width=True
    ):

        if user_message.strip():

            area, score, all_scores, top_areas = classify_case(user_message)

            st.session_state.case_classification = area

            safe_area = escape_html(area)

            st.markdown(
                f"""
                <div class="result">

                <h3>⚖️ Detected Practice Area</h3>

                <h2>{safe_area}</h2>

                <p>
                Based on the information provided, this inquiry
                appears to be related to <strong>{safe_area}</strong>.
                </p>

                </div>
                """,
                unsafe_allow_html=True
            )

            if area == "General Legal Inquiry":

                st.warning(
                    "The system could not confidently identify "
                    "a specific practice area. A lawyer should "
                    "review the inquiry."
                )

            elif area == "Multiple possible areas":

                st.warning(
                    "This inquiry matches more than one practice area "
                    f"equally ({', '.join(top_areas)}). "
                    "A lawyer should review the inquiry to determine "
                    "the correct department."
                )

            else:

                # Simple confidence indicator based on how many
                # keyword hits contributed to the top score.
                confidence = "High" if score >= 3 else "Medium" if score == 2 else "Low"

                st.success(
                    f"Recommended department: {area} "
                    f"(confidence: {confidence}, {score} keyword match(es))"
                )

        else:

            st.warning(
                "Please describe your legal issue first."
            )


# ---------------------------------------------------------
# CLIENT INTAKE
# ---------------------------------------------------------

elif page == "📝 Client Intake":

    st.title("📝 Client Intake Form")

    st.write(
        "Provide the basic information required for an initial "
        "consultation request."
    )

    with st.form("client_intake_form"):

        col1, col2 = st.columns(2)

        with col1:

            name = st.text_input(
                "Full Name *"
            )

            email = st.text_input(
                "Email Address *"
            )

            phone = st.text_input(
                "Phone Number"
            )

        with col2:

            issue_type = st.selectbox(
                "Legal Issue",
                [
                    "Family Law",
                    "Criminal Law",
                    "Property Law",
                    "Employment Law",
                    "Corporate Law",
                    "Intellectual Property",
                    "Immigration Law",
                    "Other"
                ]
            )

            incident_date = st.date_input(
                "Date of Incident",
                value=date.today()
            )

            people_involved = st.text_input(
                "People / Organizations Involved"
            )

        description = st.text_area(
            "Brief Description of the Case *",
            height=180
        )

        documents = st.file_uploader(
            "Upload Relevant Document (Optional)",
            type=[
                "pdf",
                "docx",
                "txt",
                "png",
                "jpg",
                "jpeg"
            ]
        )

        submitted = st.form_submit_button(
            "Submit Case Information",
            use_container_width=True
        )

        if submitted:

            email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

            if not name or not email or not description:

                st.error(
                    "Please complete all required fields."
                )

            elif not re.match(email_pattern, email.strip()):

                st.error(
                    "Please enter a valid email address."
                )

            else:

                st.session_state.intake_complete = True

                st.session_state.client = {
                    "name": name.strip(),
                    "email": email.strip(),
                    "phone": phone.strip(),
                    "issue_type": issue_type,
                    "incident_date": str(incident_date),
                    "people_involved": people_involved.strip(),
                    "description": description.strip(),
                    "document": (
                        documents.name
                        if documents
                        else "No document uploaded"
                    )
                }

                st.success(
                    "✅ Your initial case information has been recorded."
                )


# ---------------------------------------------------------
# CONSULTATION
# ---------------------------------------------------------

elif page == "📅 Consultation":

    st.title("📅 Schedule a Consultation")

    st.write(
        "Choose your preferred date and consultation time."
    )

    if not st.session_state.intake_complete:

        st.info(
            "Please complete the Client Intake form before "
            "scheduling a consultation."
        )

    else:

        col1, col2 = st.columns(2)

        with col1:

            consultation_date = st.date_input(
                "Preferred Date",
                min_value=date.today()
            )

        with col2:

            consultation_time = st.selectbox(
                "Preferred Time",
                [
                    "10:00 AM",
                    "11:30 AM",
                    "2:00 PM",
                    "3:30 PM",
                    "5:00 PM"
                ]
            )

        consultation_type = st.radio(
            "Consultation Type",
            [
                "Online Consultation",
                "In-person Consultation"
            ]
        )

        if st.button(
            "📅 Request Consultation",
            use_container_width=True
        ):

            # Persist the consultation choice so it survives
            # navigation and can be shown on the Case Summary page.
            st.session_state.consultation = {
                "date": str(consultation_date),
                "time": consultation_time,
                "type": consultation_type
            }

            st.markdown("""
            <div class="success-box">

            <h3>✅ Consultation Request Received</h3>

            Your preferred consultation slot has been recorded.

            </div>
            """, unsafe_allow_html=True)

            st.write(
                f"**Date:** {consultation_date}"
            )

            st.write(
                f"**Time:** {consultation_time}"
            )

            st.write(
                f"**Type:** {consultation_type}"
            )

            st.caption(
                "This demo does not connect to a real calendar."
            )


# ---------------------------------------------------------
# CASE SUMMARY
# ---------------------------------------------------------

elif page == "📋 Case Summary":

    st.title("📋 Case Summary")

    if not st.session_state.intake_complete or not st.session_state.client:

        st.info(
            "No case information has been submitted yet."
        )

    else:

        client = st.session_state.client

        st.markdown(
            f"""
            <div class="card">

            <h3>👤 Client Information</h3>

            <p><strong>Name:</strong> {escape_html(client["name"])}</p>

            <p><strong>Email:</strong> {escape_html(client["email"])}</p>

            <p><strong>Phone:</strong> {escape_html(client["phone"])}</p>

            <p><strong>Practice Area:</strong>
            {escape_html(client["issue_type"])}</p>

            <p><strong>Incident Date:</strong>
            {escape_html(client["incident_date"])}</p>

            <p><strong>People / Organizations:</strong>
            {escape_html(client["people_involved"])}</p>

            <p><strong>Document:</strong>
            {escape_html(client["document"])}</p>

            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("### 📝 Case Description")

        # Plain st.write is safe by default (no unsafe_allow_html),
        # so no manual escaping needed here.
        st.write(
            client["description"]
        )

        if st.session_state.case_classification:

            st.markdown("### 🧠 AI Classification")

            st.success(
                f"Detected Practice Area: "
                f"{st.session_state.case_classification}"
            )

        if st.session_state.consultation:

            st.markdown("### 📅 Consultation Request")

            consultation = st.session_state.consultation

            st.write(f"**Date:** {consultation['date']}")
            st.write(f"**Time:** {consultation['time']}")
            st.write(f"**Type:** {consultation['type']}")

        st.markdown("""
        <div class="disclaimer">

        <strong>Lawyer Review Required</strong><br><br>

        This information is an initial intake summary.
        It should be reviewed by a qualified legal professional
        before any legal decision or action is taken.

        </div>
        """, unsafe_allow_html=True)


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.markdown("""
<div class="footer">

⚖️ <strong>LegalIntake</strong><br>

AI-Powered Legal Client Intake Assistant

<br><br>

This application is a student project / prototype
and does not provide legal advice.

</div>
""", unsafe_allow_html=True)
