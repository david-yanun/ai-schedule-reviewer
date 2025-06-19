
# 📌 Streamlit AI Schedule Reviewer - Final Robust Version
# Handles top graphics, embedded filters, shapes by using header + usecols

import streamlit as st
import pandas as pd
import networkx as nx
import openai

st.title("🗂️ AI Schedule Reviewer (Final Robust XER Toolkit Version)")

uploaded_file = st.file_uploader("Upload your XER Toolkit export (.xlsx)", type=["xlsx"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)

    st.write(f"Workbook Sheets: {xls.sheet_names}")

    sheets = {}

    if len(xls.sheet_names) > 3:
        for name in xls.sheet_names[3:]:
            try:
                # Robust: header=3 means row 4 is the true header
                # usecols="A:Z" limits read to reasonable columns, ignores junk
                df = pd.read_excel(
                    xls,
                    sheet_name=name,
                    header=3,      # 0-indexed, so row 4
                    usecols="A:Z"  # widen if your data uses more columns
                )
                if not df.empty and len(df.columns) > 0:
                    sheets[name] = df
                else:
                    st.info(f"Skipped sheet '{name}' because it was empty or no usable columns found.")
            except Exception as e:
                st.warning(f"Skipped sheet '{name}' due to error: {e}")

    if not sheets:
        st.error("No valid data sheets found after skipping first 3 sheets and reading with robust settings. Please check your export format.")
    else:
        for name, df in sheets.items():
            st.subheader(f"Sheet: {name}")
            st.dataframe(df)

        activities = sheets.get("Activities")
        relationships = sheets.get("Relationships")

        if activities is not None and relationships is not None:
            st.subheader("Rule Checks")

            dangling = activities[activities['Predecessors'].isna() & activities['Successors'].isna()]
            st.write("Dangling Activities:", dangling)

            long_tasks = activities[activities['Duration'] > 30]
            st.write("Long Duration Activities (>30 days):", long_tasks)

            G = nx.DiGraph()
            for _, row in relationships.iterrows():
                G.add_edge(row['Predecessor'], row['Successor'])
            cycles = list(nx.simple_cycles(G))
            st.write("Logic Loops:", cycles)

            api_key = st.text_input("Enter your OpenAI API Key", type="password")

            if api_key and st.button("Generate AI Review"):
                openai.api_key = api_key
                issues_summary = f"Dangling: {len(dangling)}, Long tasks: {len(long_tasks)}, Loops: {len(cycles)}"
                response = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a senior planner reviewing a construction schedule."},
                        {"role": "user", "content": f"Please review this schedule analysis: {issues_summary}. Provide recommendations in plain English."}
                    ]
                )
                st.subheader("AI Review Result")
                st.write(response['choices'][0]['message']['content'])
        else:
            st.warning("Activities or Relationships sheet not found among valid sheets!")
