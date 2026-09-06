import streamlit as st
from database import get_complaints, update_complaint_status
import pandas as pd


def show_admin_dashboard():
    st.markdown("## 🛠️ Admin Control Center")
    st.title("🏫 Campus Care AI")
    st.write(
      "Monitor complaints, manage maintenance tasks, "
      "track priorities and resolve campus issues."
    )

    st.divider()

    st.markdown("### 📊 Campus Complaint Dashboard")

    try:
        complaints = get_complaints()
    except Exception as e:
        st.error("❌ Unable to load complaints from Supabase.")
        st.code(str(e))
        return

    if not complaints:
        st.info("📭 No complaints have been submitted yet.")
        return

    df = pd.DataFrame(complaints)

    for column in [
        "status",
        "priority",
        "category",
        "department"
    ]:
        if column not in df.columns:
            df[column] = ""

    total = len(df)

    pending = len(
        df[df["status"].fillna("") == "Pending"]
    )

    assigned = len(
        df[df["status"].fillna("") == "Assigned"]
    )

    in_progress = len(
        df[df["status"].fillna("") == "In Progress"]
    )

    resolved = len(
        df[df["status"].fillna("") == "Resolved"]
    )

    high_priority = len(
        df[
            df["priority"]
            .fillna("")
            .isin(["High", "Critical"])
        ]
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("📋 Total", total)

    with col2:
        st.metric("⏳ Pending", pending)

    with col3:
        st.metric("👷 Assigned", assigned)

    with col4:
        st.metric("🔧 In Progress", in_progress)

    with col5:
        st.metric("🚨 High Priority", high_priority)

    st.divider()

    st.markdown("### 🔍 Filter Complaints")

    col1, col2, col3 = st.columns(3)

    with col1:
        search = st.text_input(
            "Search Complaint",
            placeholder="Complaint ID, title, location..."
        )

    with col2:
        selected_priority = st.selectbox(
            "Priority",
            ["All", "Low", "Medium", "High", "Critical"]
        )

    with col3:
        selected_status = st.selectbox(
            "Status",
            [
                "All",
                "Pending",
                "Assigned",
                "In Progress",
                "Resolved"
            ]
        )

    filtered_df = df.copy()

    if search:
        search_lower = search.lower()

        filtered_df = filtered_df[
            filtered_df.apply(
                lambda row:
                search_lower in " ".join(
                    str(value).lower()
                    for value in row.values
                ),
                axis=1
            )
        ]

    if selected_priority != "All":
        filtered_df = filtered_df[
            filtered_df["priority"].fillna("")
            == selected_priority
        ]

    if selected_status != "All":
        filtered_df = filtered_df[
            filtered_df["status"].fillna("")
            == selected_status
        ]

    priority_order = {
        "Critical": 1,
        "High": 2,
        "Medium": 3,
        "Low": 4
    }

    filtered_df["priority_order"] = (
        filtered_df["priority"]
        .map(priority_order)
        .fillna(5)
    )

    filtered_df = filtered_df.sort_values(
        "priority_order"
    )

    st.markdown(
        f"### 📋 Complaints ({len(filtered_df)})"
    )

    for _, complaint in filtered_df.iterrows():

        complaint_id = complaint.get("id")
        complaint_code = complaint.get(
            "complaint_code",
            "N/A"
        )

        title = complaint.get(
            "title",
            "Untitled Complaint"
        )

        description = complaint.get(
            "description",
            ""
        )

        location = complaint.get(
            "location",
            "Unknown"
        )

        category = complaint.get(
            "category",
            "Pending AI Analysis"
        )

        priority = complaint.get(
            "priority",
            "Pending"
        )

        department = complaint.get(
            "department",
            "Pending"
        )

        status = complaint.get(
            "status",
            "Pending"
        )

        created_at = complaint.get(
            "created_at",
            ""
        )

        attachment_url = complaint.get(
            "attachment_url",
            None
        )

        attachment_type = complaint.get(
            "attachment_type",
            None
        )

        if priority == "Critical":
            priority_icon = "🔴"
        elif priority == "High":
            priority_icon = "🟠"
        elif priority == "Medium":
            priority_icon = "🟡"
        elif priority == "Low":
            priority_icon = "🟢"
        else:
            priority_icon = "⚪"

        if status == "Resolved":
            status_icon = "✅"
        elif status == "In Progress":
            status_icon = "🔧"
        elif status == "Assigned":
            status_icon = "👷"
        else:
            status_icon = "⏳"

        with st.expander(
            f"{status_icon} {priority_icon} "
            f"{complaint_code} — {title}"
        ):

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**📍 Location**")
                st.write(location)

            with col2:
                st.markdown("**🤖 AI Category**")
                st.write(category)

            with col3:
                st.markdown("**🏢 Department**")
                st.write(department)

            st.divider()

            st.markdown("**📝 Description**")
            st.write(description)

            st.markdown("**🎯 AI Priority**")
            st.write(f"{priority_icon} {priority}")

            st.markdown("**🕒 Submitted**")
            st.write(str(created_at))

            if attachment_url:
                st.markdown("**📎 Evidence**")

                if attachment_type == "pdf":
                    st.markdown(
                        f"[📄 Open PDF Evidence]({attachment_url})"
                    )
                else:
                    st.image(
                        attachment_url,
                        caption="Complaint Evidence",
                        use_container_width=True
                    )

            st.divider()

            st.markdown("### 🔄 Update Complaint Status")

            status_list = [
                "Pending",
                "Assigned",
                "In Progress",
                "Resolved"
            ]

            current_index = (
                status_list.index(status)
                if status in status_list
                else 0
            )

            new_status = st.selectbox(
                "Change Status",
                status_list,
                index=current_index,
                key=f"status_{complaint_id}"
            )

            if st.button(
                "💾 Update Status",
                key=f"update_{complaint_id}",
                use_container_width=True
            ):

                if new_status == status:

                    st.info(
                        "ℹ️ Complaint is already "
                        "in this status."
                    )

                else:

                    try:

                        result = update_complaint_status(
                            complaint_id,
                            new_status
                        )

                        if result:

                            st.success(
                                f"✅ Status updated to "
                                f"'{new_status}'"
                            )

                            st.rerun()

                        else:

                            st.error(
                                "❌ Status update failed."
                            )

                    except Exception as e:

                        st.error(
                            "❌ Error updating status."
                        )

                        st.code(str(e))

    st.divider()

    if st.button(
        "🔄 Refresh Dashboard",
        use_container_width=True
    ):
        st.rerun()