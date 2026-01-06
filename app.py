import re
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Term 6 Dashboard", layout="wide")
st.title("Term 6 Schedule Dashboard")

st.write("Upload the timetable, choose subjects, and download your schedule.")

uploaded_file = st.file_uploader("Upload Final_Schedule_T6 file", type=["xlsx"])


def clean_schedule(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Normalize headers
    df.columns = [str(c).strip() for c in df.columns]

    # Remove fully empty rows
    df = df.dropna(how="all")

    # Rename first two columns
    df.rename(columns={df.columns[0]: "week", df.columns[1]: "day"}, inplace=True)

    # Unpivot timetable grid
    long_df = df.melt(
        id_vars=["week", "day"],
        var_name="time",
        value_name="raw"
    )

    # Keep meaningful rows
    long_df = long_df.dropna(subset=["raw"])

    # Parse subject + location like: Fintech-A (PT-1-2)
    def parse(value):
        value = str(value).strip()
        match = re.match(r"([A-Za-z& ]+-?[A-Z]?)\s*\((.*?)\)", value)

        if match:
            subject = match.group(1).strip()
            location = match.group(2).strip()
        else:
            subject = value
            location = ""

        return pd.Series([subject, location])

    long_df[["subject", "location"]] = long_df["raw"].apply(parse)

    long_df = (
        long_df[["week", "day", "time", "subject, "location"]]
        .sort_values(["week", "day", "time"])
        .reset_index(drop=True)
    )

    return long_df


if uploaded_file:
    df = pd.read_excel(uploaded_file)
    clean_df = clean_schedule(df)

    st.subheader("Parsed Schedule")
    st.dataframe(clean_df)

    subjects = sorted(clean_df["subject"].unique())
    chosen = st.multiselect("Select subjects", subjects)

    if chosen:
        filtered = clean_df[clean_df["subject"].isin(chosen)]
        st.subheader("Filtered")
        st.dataframe(filtered)

        out_name = "Term6_Selected_Schedule.xlsx"
        filtered.to_excel(out_name, index=False)

        with open(out_name, "rb") as f:
            st.download_button(
                label="Download Excel",
                data=f,
                file_name=out_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
