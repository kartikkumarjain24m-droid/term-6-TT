import streamlit as st
import pandas as pd

st.set_page_config(page_title="Term 6 Schedule Dashboard", layout="wide")

st.title("Term 6 Schedule Dashboard")

st.write("Upload your timetable file (Excel)")

uploaded_file = st.file_uploader("Upload .xlsx file", type=["xlsx"])

if uploaded_file is not None:
    # Read the file
    try:
        df = pd.read_excel(uploaded_file)

        st.subheader("Preview")
        st.dataframe(df, use_container_width=True)

        # Subject options based on provided list
        subject_list = [
            "Fintech-A","Fintech-B",
            "BEDM-A","BEDM-B",
            "Art-A","Art-B",
            "WH-A","WH-B",
            "LETV",
            "Film&Firm-A","Film&Firm-B",
            "SHRM",
            "SCM-A","SCM-B",
            "AIS",
            "EB",
            "AIAM-A","AIAM-B",
            "SA-A","SA-B",
            "CSM",
            "EM",
            "I4TS"
        ]

        st.subheader("Select Subjects")
        selected_subjects = st.multiselect(
            "Choose subjects",
            subject_list
        )

        if selected_subjects:
            # Try matching against any relevant column name
            possible_cols = ["Subject", "Course", "Subject Name", "Section", "Class"]
            col_found = None

            for c in possible_cols:
                if c in df.columns:
                    col_found = c
                    break

            if not col_found:
                st.error(
                    "Could not detect a subject column. "
                    "Share your column names so I can map them correctly."
                )
            else:
                filtered = df[df[col_found].isin(selected_subjects)]

                st.subheader("Filtered Schedule")
                st.dataframe(filtered, use_container_width=True)

                if not filtered.empty:
                    # Download as Excel
                    download_file = filtered.to_excel(
                        "filtered_schedule.xlsx", index=False
                    )

                    with open("filtered_schedule.xlsx", "rb") as f:
                        st.download_button(
                            label="Download Schedule (Excel)",
                            data=f,
                            file_name="schedule_term6.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                else:
                    st.warning("No records found for the selected subjects.")
        else:
            st.info("Select at least one subject to see the schedule.")

    except Exception as e:
        st.error(f"File load failed: {e}")
else:
    st.info("Upload your timetable to begin.")

