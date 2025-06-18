
# 📌 Streamlit AI Schedule Reviewer - One Excel Version

import streamlit as st
import pandas as pd
import networkx as nx
import openai

st.title("🗂️ AI Schedule Reviewer (XER Toolkit Excel Version)")

# Upload single Excel file
uploaded_file = st.file_uploader("Upload your XER Toolkit export (.xlsx)", type=["xlsx"])

if uploaded_file:
    # Read ALL sheets
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names
    st.write(f"Workbook Sheets: {sheet_names}")

    # Load each sheet to a dict
    sheets = {name: pd.read_excel(xls, sheet_name=name) for name in sheet_names}

    # Show each sheet
    for name, df in sheets.items():
        st.subheader(f"Sheet: {name}")
        st.dataframe(df)

    # Extract main sheets for checks
    activities = sheets.get("Activities")
    relationships = sheets.get("Relationships")

    if activities is not None and relationships is not None:
        st.subheader("Rule Checks")

        # Example: Dangling activities
        dangling = activities[activities['Predecessors'].isna() & activities['Successors'].isna()]
        st.write("Dangling Activities:", dangling)

        # Example: Long Duration
        long_tasks = activities[activities['Duration'] > 30]
        st.write("Long Duration Activities (>30 days):", long_tasks)

        # Example: Logic Loops
        G = nx.DiGraph()
        for _, row in relationships.iterrows():
            G.add_edge(row['Predecessor'], row['Successor'])
        cycles = list(nx.simple_cycles(G))
        st.write("Logic Loops:", cycles)

        # OpenAI API Key
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
        st.warning("Activities or Relationships sheet not found! Please check your XER Toolkit export.")

