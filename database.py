import streamlit as st
from supabase import create_client

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL or Key missing in Streamlit Secrets")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def create_complaint(data):
    response = (
        supabase
        .table("complaints")
        .insert(data)
        .execute()
    )

    return response.data


def get_complaints():
    try:
        response = (
            supabase
            .table("complaints")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

        data = response.data

        if data is None:
            return []

        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            return [data]

        return []

    except Exception as e:
        print("Get complaints error:", e)
        return []


def upload_file(file_data, file_name, content_type):
    try:
        supabase.storage.from_("complaint-files").upload(
            file_name,
            file_data,
            {
                "content-type": content_type
            }
        )

        public_url = (
            supabase.storage
            .from_("complaint-files")
            .get_public_url(file_name)
        )

        return public_url

    except Exception as e:
        print("File upload error:", e)
        return None


def update_complaint_status(complaint_id, new_status):
    try:
        response = (
            supabase
            .table("complaints")
            .update({
                "status": new_status,
                "updated_at": "now()"
            })
            .eq("id", complaint_id)
            .execute()
        )

        return response.data

    except Exception as e:
        print("Status update error:", e)
        return []


def get_complaint_stats():
    complaints = get_complaints()

    if not isinstance(complaints, list):
        complaints = []

    total = len(complaints)

    pending = sum(
        1 for c in complaints
        if isinstance(c, dict) and c.get("status") == "Pending"
    )

    assigned = sum(
        1 for c in complaints
        if isinstance(c, dict) and c.get("status") == "Assigned"
    )

    in_progress = sum(
        1 for c in complaints
        if isinstance(c, dict) and c.get("status") == "In Progress"
    )

    resolved = sum(
        1 for c in complaints
        if isinstance(c, dict) and c.get("status") == "Resolved"
    )

    high_priority = sum(
        1 for c in complaints
        if isinstance(c, dict)
        and c.get("priority") in ["High", "Critical"]
    )

    return {
        "total": total,
        "pending": pending,
        "assigned": assigned,
        "in_progress": in_progress,
        "resolved": resolved,
        "high_priority": high_priority
    }
