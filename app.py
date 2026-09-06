
import streamlit as st
from database import create_complaint, upload_file
from datetime import datetime
from ai_engine import analyze_complaint
from pathlib import Path
from admin import show_admin_dashboard

st.set_page_config(
    page_title="Campus Care AI",
    page_icon="🏫",
    layout="wide"
)

css_path = Path("style.css")

with open(css_path, "r", encoding="utf-8") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )

if "portal" not in st.session_state:
    st.session_state.portal = None

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False


def student_dashboard():

    st.markdown(
        '<div class="ui-card">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title">📝 Report a Campus Problem</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-caption">'
        'Provide accurate details so our AI can analyze the issue effectively.'
        '</div>',
        unsafe_allow_html=True
    )

    title = st.text_input(
        "Complaint Title",
        placeholder="Example: Classroom fan not working"
    )

    description = st.text_area(
        "Describe the Problem",
        placeholder="Explain the problem in detail..."
    )

    location = st.selectbox(
        "Location",
        [
            "Main Building",
            "Engineering Block",
            "Computer Lab",
            "Library",
            "Canteen",
            "Hostel",
            "Parking Area",
            "Other"
        ]
    )

    room = st.text_input(
        "Room / Area Number",
        placeholder="Example: Room 204"
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="ui-card">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title">📎 Evidence</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-caption">'
        'Add a photo or PDF as evidence of the campus problem.'
        '</div>',
        unsafe_allow_html=True
    )

    attachment_type = st.radio(
        "Choose evidence type:",
        [
            "📷 Take Photo",
            "🖼️ Upload Image",
            "📄 Upload PDF"
        ],
        horizontal=True
    )

    camera_photo = None
    image_file = None
    pdf_file = None

    if attachment_type == "📷 Take Photo":

        st.info(
            "📷 Capture a clear photo showing the campus problem."
        )

        camera_photo = st.camera_input(
            "Take a photo"
        )

    elif attachment_type == "🖼️ Upload Image":

        image_file = st.file_uploader(
            "🖼️ Choose an image",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=False
        )

    elif attachment_type == "📄 Upload PDF":

        pdf_file = st.file_uploader(
            "📄 Choose a PDF",
            type=["pdf"],
            accept_multiple_files=False
        )

    if camera_photo:

        st.image(
            camera_photo,
            caption="Captured Evidence",
            width=500
        )

    if image_file:

        st.image(
            image_file,
            caption="Selected Evidence",
            width=500
        )

    if pdf_file:

        st.success(
            f"📄 PDF selected: {pdf_file.name}"
        )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

    submit = st.button(
        "🚀 Submit Complaint",
        type="primary",
        use_container_width=True,
        key="submit_complaint"
    )

    if submit:

        if not title.strip() or not description.strip() or not room.strip():

            st.error(
                "❌ Please fill Complaint Title, Description and Room/Area."
            )

            st.stop()

        complaint_code = (
            "CMP-"
            + datetime.now().strftime("%Y%m%d%H%M%S")
        )

        full_location = f"{location} - {room}"

        attachment = None
        attachment_type_value = None

        if attachment_type == "📷 Take Photo":

            if camera_photo:

                attachment = camera_photo
                attachment_type_value = "image"

        elif attachment_type == "🖼️ Upload Image":

            if image_file:

                attachment = image_file
                attachment_type_value = "image"

        elif attachment_type == "📄 Upload PDF":

            if pdf_file:

                attachment = pdf_file
                attachment_type_value = "pdf"

        attachment_url = None

        try:

            if attachment:

                file_bytes = attachment.getvalue()

                if attachment_type_value == "image":

                    extension = "jpg"
                    content_type = "image/jpeg"

                else:

                    extension = "pdf"
                    content_type = "application/pdf"

                file_name = (
                    f"{complaint_code}.{extension}"
                )

                with st.spinner(
                    "📤 Uploading evidence..."
                ):

                    attachment_url = upload_file(
                        file_bytes,
                        file_name,
                        content_type
                    )

            with st.spinner(
                "🤖 Gemini AI is analyzing your complaint..."
            ):

                ai_result = analyze_complaint(
                    title,
                    description,
                    full_location
                )

            category = ai_result["category"]
            priority = ai_result["priority"]
            department = ai_result["department"]
            reason = ai_result["reason"]

            complaint_data = {
                "complaint_code": complaint_code,
                "title": title,
                "description": description,
                "location": full_location,
                "category": category,
                "priority": priority,
                "department": department,
                "status": "Pending",
                "attachment_url": attachment_url,
                "attachment_type": attachment_type_value
            }

            with st.spinner(
                "💾 Saving complaint to campus database..."
            ):

                result = create_complaint(
                    complaint_data
                )

            if result:

                st.success(
                    "✅ Complaint submitted successfully!"
                )

                st.info(
                    f"🆔 Complaint ID: **{complaint_code}**"
                )

                st.markdown(
                    """
                    <div class="ai-result">
                        <div class="ai-result-title">
                            🤖 Gemini AI Analysis
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.metric(
                        "🏷️ Category",
                        category
                    )

                with col2:

                    st.metric(
                        "🚨 Priority",
                        priority
                    )

                with col3:

                    st.metric(
                        "🏢 Department",
                        department
                    )

                st.markdown(
                    f"""
                    <div class="ai-reason">
                        <strong>💡 AI Reason</strong><br>
                        {reason}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if attachment_url:

                    st.success(
                        "📎 Evidence uploaded successfully!"
                    )

            else:

                st.error(
                    "❌ Complaint could not be submitted."
                )

        except Exception as e:

            st.error(
                f"❌ Error: {e}"
            )


if st.session_state.portal is None:

    st.title("🏫 Campus Care AI")

    st.subheader(
        "Smart Campus Complaint & Maintenance Platform"
    )

    st.write(
        "Report campus problems, upload evidence, and let AI "
        "intelligently prioritize maintenance requests for "
        "faster and smarter resolution."
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("🎓 Student Portal")

        st.write(
            "Report campus problems, upload evidence and "
            "submit maintenance requests easily."
        )

        if st.button(
            "🎓 Enter Student Portal",
            use_container_width=True,
            type="primary",
            key="student_portal"
        ):

            st.session_state.portal = "student"
            st.rerun()

    with col2:

        st.subheader("🔐 Admin Portal")

        st.write(
            "Monitor complaints, manage maintenance tasks "
            "and track campus operations efficiently."
        )

        if st.button(
            "🔐 Enter Admin Portal",
            use_container_width=True,
            key="admin_portal"
        ):

            st.session_state.portal = "admin"
            st.rerun()

    st.divider()

    st.caption(
        "🤖 AI Powered  •  📊 Smart Analytics  •  🛠️ Predictive Maintenance"
    )


elif st.session_state.portal == "student":

    student_dashboard()

    st.divider()

    if st.button(
        "⬅️ Back to Portal",
        use_container_width=True,
        key="back_student"
    ):

        st.session_state.portal = None
        st.rerun()


elif st.session_state.portal == "admin":

    if not st.session_state.admin_logged_in:



        st.markdown(
            '<div class="ui-card">',
            unsafe_allow_html=True
        )

        st.header("🔐 Admin Login")

        st.write(
            "Only authorized campus administrators "
            "can access the admin dashboard."
        )

        username = st.text_input(
            "👤 Username",
            placeholder="Enter admin username"
        )

        password = st.text_input(
            "🔑 Password",
            type="password",
            placeholder="Enter admin password"
        )

        login = st.button(
            "🚀 Login",
            type="primary",
            use_container_width=True,
            key="admin_login"
        )

        if login:

            if (
                username == "RIYA"
                and password == "RIYA@123"
            ):

                st.session_state.admin_logged_in = True

                st.success(
                    "✅ Login successful!"
                )

                st.rerun()

            else:

                st.error(
                    "❌ Invalid username or password."
                )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

        st.divider()

        if st.button(
            "⬅️ Back to Portal",
            use_container_width=True,
            key="back_admin"
        ):

            st.session_state.portal = None
            st.rerun()

    else:

        show_admin_dashboard()

        st.divider()

        if st.button(
            "🚪 Logout",
            use_container_width=True,
            key="admin_logout"
        ):

            st.session_state.admin_logged_in = False
            st.session_state.portal = None
            st.rerun()
