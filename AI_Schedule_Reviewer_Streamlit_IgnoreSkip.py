
# 📌 Streamlit AI Schedule Reviewer - Robust Version
# Ignores first 3 sheets (graphics) + skips first 3 rows in each data sheet

import streamlit as st
import pandas as pd
import networkx as nx
import openai

st.title("🗂️ AI Schedule Reviewer (Stable XER Toolkit Version)")

uploaded_file = st.file_uploader("Upload your XER Toolkit export (.xlsx)", type=["xlsx"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)

    # Show all sheet names for transparency
    st.write(f"Workbook Sheets: {xls.sheet_names}")

    # Define: skip first 3 sheets entirely, read the rest, skip top 3 rows
    sheets = {}
    if len(xls.sheet_names) > 3:
        for name in xls.sheet_names[3:]:
            sheets[name] = pd.read_excel(xls, sheet_name=name, skiprows=3)

    # Show what was actually loaded
    for name, df in sheets.items():
        st.subheader(f"Sheet: {name}")
        st.dataframe(df)

    # Get main sheets
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
        st.warning("Activities or Relationships sheet not found in sheets after skipping graphics!")

