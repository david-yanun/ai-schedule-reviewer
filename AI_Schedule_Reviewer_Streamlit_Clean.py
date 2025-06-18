
# 📌 Streamlit AI Schedule Reviewer Prototype

import streamlit as st
import pandas as pd
import networkx as nx
import openai

st.title("🗂️ AI Schedule Reviewer")

# Upload CSVs
activities_file = st.file_uploader("Upload Activities.csv")
relationships_file = st.file_uploader("Upload Relationships.csv")

if activities_file and relationships_file:
    activities = pd.read_csv(activities_file)
    relationships = pd.read_csv(relationships_file)

    st.subheader("Rule Checks")
    # Dangling
    dangling = activities[activities['Predecessors'].isna() & activities['Successors'].isna()]
    st.write("Dangling Activities:", dangling)

    # Long Duration
    long_tasks = activities[activities['Duration'] > 30]
    st.write("Long Duration Activities (>30 days):", long_tasks)

    # Logic Loops
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
