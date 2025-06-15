import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import base64

# CONFIG
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    h1 {
           color: saddlebrown !important;
       }
       h2 {
           color: saddlebrown !important;
       }
    body {
        background-color: #f8f9fa;
        color: #212529;
    }
    .main {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
    }
    h1, h2, h3, h4 {
        font-family: 'Segoe UI', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧭 Crime Pattern Detection Dashboard (2020–2024)")
st.markdown("A data-driven lens into crime trends, patterns, and weapon usage across India.\n\n---")

# Sidebar - Dark Mode Toggle
dark_mode = st.sidebar.checkbox("🌙 Dark Mode")
if dark_mode:
    st.markdown("""
        <style>
        body {
            background-color: #1e1e1e;
            color: #f1f1f1;
        }
        .main {
            background-color: #2c2c2c;
        }
        </style>
    """, unsafe_allow_html=True)

# Sidebar - CSV Download
@st.cache_data

def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

# Database connection
conn = sqlite3.connect("crime_data.db")

# SECTION 1: Total Crimes Count
st.header("📊 Overall Crime Overview")
query1 = "SELECT COUNT(*) AS Total_Crimes FROM crimes"
df1 = pd.read_sql_query(query1, conn)
st.metric("Total Crimes (2020–2024)", df1['Total_Crimes'][0])

# SECTION 2: Top 10 Cities with Most Crimes
st.header("🏙️ Top 10 Cities with Most Crimes")
query2 = """
SELECT City, COUNT(*) AS Total_Crimes
FROM crimes
GROUP BY City
ORDER BY Total_Crimes DESC
LIMIT 10;
"""
df2 = pd.read_sql_query(query2, conn)
fig2 = px.bar(df2, x="City", y="Total_Crimes", color="City", title="City-wise Crime Count")
st.plotly_chart(fig2)
st.download_button("Download City-wise Data", data=convert_df(df2), file_name="city_crimes.csv", mime='text/csv')

# SECTION 3: Crime Type Distribution
st.header("🧾 Crime Types Distribution")
query3 = """
SELECT `Crime Description`, COUNT(*) AS Total
FROM crimes
GROUP BY `Crime Description`
ORDER BY Total DESC;
"""
df3 = pd.read_sql_query(query3, conn)
fig3 = px.bar(df3, x="Total", y="Crime Description", orientation='h', color="Crime Description", title="Crime Types")
st.plotly_chart(fig3)
st.download_button("Download Crime Type Data", data=convert_df(df3), file_name="crime_types.csv", mime='text/csv')

# SECTION 4: Weapon Usage
st.header("🔪 Weapon Usage in Crimes")
query4 = """
SELECT `Weapon Used` AS Weapon, COUNT(*) AS Total
FROM crimes
WHERE Weapon IS NOT NULL AND `Weapon Used` != ''
GROUP BY Weapon
ORDER BY Total DESC
LIMIT 10;
"""
df4 = pd.read_sql_query(query4, conn)
fig4 = px.bar(df4, x="Total", y="Weapon", orientation='h', color="Weapon", title="Top 10 Weapons Used")
st.plotly_chart(fig4)
st.download_button("Download Weapon Data", data=convert_df(df4), file_name="weapon_usage.csv", mime='text/csv')

# SECTION 5: Gender-wise Victim Distribution
st.header("🚻 Gender-wise Victim Distribution")
query5 = """
SELECT `Victim Gender` AS Gender, COUNT(*) AS Total
FROM crimes
GROUP BY Gender;
"""
df5 = pd.read_sql_query(query5, conn)
fig5 = px.pie(df5, names='Gender', values='Total', title="Victim Gender Distribution")
st.plotly_chart(fig5)
st.download_button("Download Gender-wise Data", data=convert_df(df5), file_name="victim_gender.csv", mime='text/csv')

# SECTION 6: Age-wise Victim Distribution
st.header("👶 Age Distribution of Victims")
query6 = """
SELECT `Victim Age` FROM crimes
WHERE `Victim Age` IS NOT NULL AND `Victim Age` > 0
"""
df6 = pd.read_sql_query(query6, conn)
bins = [0, 12, 18, 30, 45, 60, 100]
labels = ['Child', 'Teen', 'Young Adult', 'Adult', 'Mid-age', 'Senior']
df6['Age Group'] = pd.cut(df6['Victim Age'], bins=bins, labels=labels)
age_counts = df6['Age Group'].value_counts().reset_index()
age_counts.columns = ['Age Group', 'Total']
fig6 = px.bar(age_counts, x="Age Group", y="Total", color="Age Group", title="Victim Age Groups")
st.plotly_chart(fig6)
st.download_button("Download Age-wise Victim Data", data=convert_df(df6), file_name="Age-wise_Victim.csv", mime='text/csv')

# SECTION 7: Time of Day Crime Trend
st.header("🕒 Crime Trend by Time of Occurrence")
query7 = """
SELECT `Time of Occurrence` FROM crimes
"""
df7 = pd.read_sql_query(query7, conn)
df7 = df7.dropna()
df7['Hour'] = df7['Time of Occurrence'].str[:2].astype(int)
hourly = df7['Hour'].value_counts().sort_index().reset_index()
hourly.columns = ['Hour', 'Total']
fig7 = px.line(hourly, x="Hour", y="Total", markers=True, title="Crimes by Hour of Day")
st.plotly_chart(fig7)
st.download_button("Download Time of Day Crime Trend Data", data=convert_df(df7), file_name="Time_of_Day_Crime_Trend.csv", mime='text/csv')

# SECTION 8: Year-wise Crime Count
st.header("📅 Year-wise Crime Trend")
query8 = """
SELECT strftime('%Y', `Date of Occurrence`) AS Year, COUNT(*) AS Total
FROM crimes
GROUP BY Year
ORDER BY Year;
"""
df8 = pd.read_sql_query(query8, conn)
fig8 = px.line(df8, x="Year", y="Total", markers=True, title="Yearly Crime Trend")
st.plotly_chart(fig8)
st.download_button("Download Year-wise Crime Count Data", data=convert_df(df8), file_name="Year-wise_Crime_Count.csv", mime='text/csv')

# SECTION 9: Case Closure Status
st.header("🗂️ Case Closure Status")
query9 = """
SELECT `Case Closed`, COUNT(*) AS Total
FROM crimes
GROUP BY `Case Closed`;
"""
df9 = pd.read_sql_query(query9, conn)
fig9 = px.pie(df9, names='Case Closed', values='Total', title="Case Status")
st.plotly_chart(fig9)
st.download_button("Download Case Closure Status Data", data=convert_df(df9), file_name="Case_Closure_Status.csv", mime='text/csv')

# SECTION 10: Crime Domain Distribution
st.header("🧭 Crime Domain Distribution")
query10 = """
SELECT `Crime Domain`, COUNT(*) AS Total
FROM crimes
GROUP BY `Crime Domain`
ORDER BY Total DESC
LIMIT 10;
"""
df10 = pd.read_sql_query(query10, conn)
fig10 = px.bar(df10, x="Total", y="Crime Domain", orientation='h', color="Crime Domain", title="Top Crime Domains")
st.plotly_chart(fig10)
st.download_button("Download Crime Domain Distribution Data", data=convert_df(df10), file_name="Crime_Domain_Distribution.csv", mime='text/csv')

# Footer
st.markdown("---")
st.markdown("© 2025 Trisha Bej — Crime Pattern Detection Dashboard")
