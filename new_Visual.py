import altair as alt
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import traceback
from datetime import datetime


# Page configuration
st.set_page_config(layout="wide")
st.markdown(
    """
    <style>
        .main .block-container {
            max-width: 95%;
            padding: 2rem;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 60px;  /* Increased height to accommodate larger text */
            white-space: pre-wrap;
            background-color: #F0F2F6;
            border-radius: 4px 4px 0px 0px;
            gap: 10px;
            padding-top: 10px;
            padding-bottom: 10px;
            font-size: 1.2rem !important;  /* Increased font size */
            font-weight: 600 !important;   /* Made text bolder */
        }
        .stTabs [aria-selected="true"] {
            background-color: #FFFFFF;
            font-size: 1.3rem !important;  /* Slightly larger for selected tab */
        }
        /* Optional: Increase space between tabs */
        .stTabs [data-baseweb="tab"]:not(:last-child) {
            margin-right: 12px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Function to load data from a public Google Drive link
def load_data_from_google_drive(public_link):
    try:
        # Fetch the file content for debugging
        response = requests.get(public_link)
        content = response.text

        # Print the first few lines for inspection
        st.write("First 5 lines of the file:")
        st.code(content.splitlines()[:5])

        # Load the data into a DataFrame
        df = pd.read_csv(public_link, encoding="utf-8")
        return df
    except Exception as e:
        st.error(f"Error loading data from Google Drive: {e}")
        return None

# Cache the data to improve performance
@st.cache_data
def load_data():
    # Fetch the Google Drive link from Streamlit secrets
    public_link = st.secrets["google_drive_link"]
    return load_data_from_google_drive(public_link)

# Sidebar Login
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.sidebar.title("🔐 Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        if username == "adminSaheli" and password == "25@das20":
            st.session_state["logged_in"] = True
            st.sidebar.success("✅ Logged in successfully!")
            st.rerun()
        else:
            st.sidebar.error("❌ Invalid credentials. Try again.")

# Show App Functionality Only If Logged In
if st.session_state["logged_in"]:





        # Streamlit App
        def main():
            st.title("📊 Employee Data Visualization Dashboard")
            st.markdown("Welcome to the interactive employee data visualization dashboard! Use the sidebar filters to explore the data.")
        
            # Load data
            df = load_data()
        
            if df is not None:
                # Data preprocessing
                if "hire_date" in df.columns:
                    df["hire_date"] = pd.to_datetime(df["hire_date"], errors='coerce')
                if "last_date" in df.columns:
                    df["last_date"] = pd.to_datetime(df["last_date"], errors='coerce')
                if "birth_date" in df.columns:
                    df["birth_date"] = pd.to_datetime(df["birth_date"], errors='coerce')
        
                # Calculate tenure
                max_last_date = df['last_date'].max() 
                if "hire_date" in df.columns and "last_date" in df.columns:
                    df["tenure"] = ((df['last_date'].fillna(max_last_date) - df['hire_date']).dt.days / 365.0)
        
                # Sidebar filters
                st.sidebar.header("🔍 Filters")
                department_name = st.sidebar.multiselect("Department Name", df["dept_name"].unique())
                left_filter = st.sidebar.selectbox("Left", ["All", "Left", "Stayed"])
                title_filter = st.sidebar.multiselect("Job Title", df["title"].unique())
                gender_filter = st.sidebar.selectbox("Gender", ["All", "M", "F"])
               
        
                # Apply filters
                if department_name:
                    df = df[df["dept_name"].isin(department_name)]
                if left_filter == "Left":
                    df = df[df["left"] == 1]
                elif left_filter == "Stayed":
                    df = df[df["left"] == 0]
                if title_filter:
                    df = df[df["title"].isin(title_filter)]
                if gender_filter != "All":
                    df = df[df["sex"] == gender_filter]
        
        
                # Key Metrics
                st.header("📈 Key Metrics")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Employees", f"{df['emp_no'].nunique():,}")
                with col2:
                    st.metric("Employees Left", f"{df[df['left'] == 1]['emp_no'].nunique():,}")
                with col3:
                    st.metric("Employees Stayed", f"{df[df['left'] == 0]['emp_no'].nunique():,}")
                with col4:
                    st.metric("Emp in more than 1 departments", f"{(df['emp_no'].value_counts()>1).sum():,}")
        
                col5, col6, col7, col8 = st.columns(4)
                with col5:
                    st.metric("Total Department", df['dept_name'].nunique())
                with col6:
                    st.metric("Average Salary", f"{df.groupby('emp_no')['salary'].mean().mean():,.2f}")
                with col7:
                    st.metric("Average Tenure", f"{df['tenure'].mean():.2f} yr")
                with col8:
                    st.metric("Median Tenure", f"{df['tenure'].median():.2f} yr")
        
                col9, col10, col11, col12 = st.columns(4)
                with col9:
                    st.metric("Avg tenure (Emp who left)", f"{df.loc[df['left'] == 1, 'tenure'].mean():.2f} yrs")
                with col10:
                    st.metric("Tenure Range(in year)", f"{df.groupby('emp_no')['tenure'].min().min():.1f} - {df.groupby('emp_no')['tenure'].max().max():.1f}")
                with col11:
                    df['age'] = (df['last_date'] - df['birth_date']).dt.days / 365.0 
                    st.metric("Avg age (Emp who left)", f"{df.loc[df['left'] == 1, 'age'].mean():.2f} yrs")
                with col12:
                    st.metric("Avg projects per emp", f"{df.groupby('emp_no')['no_of_projects'].mean().mean():,.2f}")
        
                col13, col14, col15, col16 = st.columns(4)
                with col13:
                    total_emp = df.groupby('Last_performance_rating').size().reset_index(name='total_emp')
        
                    rating_map = {'PIP': 1, 'C': 2, 'B': 3, 'S': 4, 'A': 5}
                    average_performance_rating = (
                        total_emp.apply(lambda row: row['total_emp'] * rating_map.get(row['Last_performance_rating'], 0), axis=1).sum() 
                        / total_emp['total_emp'].sum()
                    )
        
                    if 1 <= average_performance_rating < 2:
                        avg_ratings = 'PIP'
                    elif 2 <= average_performance_rating < 3:
                        avg_ratings = 'C'
                    elif 3 <= average_performance_rating < 4:
                        avg_ratings = 'B'
                    elif 4 <= average_performance_rating < 5:
                        avg_ratings = 'S'
                    else:
                        avg_ratings = 'A'
                    st.metric("Avg Performance Rating", avg_ratings)
                with col14:
                    st.metric("Salary Range", f"{df.groupby('emp_no')['salary'].min().min():.1f} - {df.groupby('emp_no')['salary'].max().max():.1f}")
                    
                with col15:
                    left_employees = df[df['left'] == 1]['emp_no'].nunique()
                    total_employees = df['emp_no'].nunique()
                    attrition_rate = (left_employees / total_employees) * 100.00
                    st.metric("Attrition Rate", f"{attrition_rate:.2f}%")
        
                with col16:
                    st.metric("Total Manager", df.loc[df['title'] == 'Manager', 'emp_no'].nunique())    
        
                # Create tabs
                tab1, tab2, tab3, tab4 = st.tabs([
                    "1. Age Group & Year-wise Attrition Analysis",
                    "2. Employee Analysis", 
                    "3. Department Level Analysis",
                    "4. Salary Analysis"
                ])
        
                with tab1:
                    st.header("Age Group & Year-wise Attrition Analysis")
                    
                    # Visualization 1: Employee Turnover by Age Group
                    filtered_df = df[df['left'] == 1].copy()
                    filtered_df['age'] = ((filtered_df['last_date'] - filtered_df['birth_date']).dt.days / 365)
        
                    def age_group(age):
                        if 21 <= age <= 30: return '21-30'
                        elif 30 < age <= 40: return '31-40'
                        elif 40 < age <= 50: return '41-50'
                        elif 50 < age <= 60: return '51-60'
                        else: return '60+'
        
                    filtered_df['age_group'] = filtered_df['age'].apply(age_group)
                    grouped_df = (filtered_df.groupby('age_group')['emp_no']
                                 .nunique()
                                 .reindex(['21-30', '31-40', '41-50', '51-60', '60+'])
                                 .reset_index(name='NO_OF_EMP'))
                    grouped_df['PCT'] = (grouped_df['NO_OF_EMP'] * 100.00) / grouped_df['NO_OF_EMP'].sum()
        
                    plt.figure(figsize=(8, 4))
                    ax = sns.barplot(x='age_group', y='NO_OF_EMP', data=grouped_df, color='#1f77b4',
                                    order=['21-30', '31-40', '41-50', '51-60', '60+'])
                    plt.title('Employee Turnover by Age Group', fontsize=10,fontweight='bold')
                    plt.xlabel('Age Group', fontsize=8)
                    plt.ylabel('Number of Employees', fontsize=8)
                    for p in ax.patches:
                        ax.annotate(f"{int(p.get_height())}", (p.get_x() + p.get_width() / 2., p.get_height()),
                                   ha='center', va='center', xytext=(0, 5), textcoords='offset points', fontsize=10)
                    plt.grid(axis='y', alpha=0.2)
                    st.pyplot(plt)
        
                    # Visualization 2: Year-wise Attrition Rate
                    if all(col in df.columns for col in ['hire_date', 'last_date', 'left']):
                        hired_emp = (df.groupby(df['hire_date'].dt.year)
                                    .agg(total_emp_hired=('emp_no', 'nunique'))
                                    .reset_index()
                                    .rename(columns={'hire_date': 'year'}))
                        left_emp = (df[df['left'] == 1]
                                   .groupby(df['last_date'].dt.year)
                                   .agg(total_emp_left=('emp_no', 'nunique'))
                                   .reset_index()
                                   .rename(columns={'last_date': 'year'}))
                        merged = pd.merge(hired_emp, left_emp, on='year', how='outer').fillna(0)
                        merged['cum_hired_emp_count'] = merged['total_emp_hired'].cumsum()
                        merged['cum_left_emp_count'] = merged['total_emp_left'].cumsum()
                        merged['new_count'] = merged['cum_left_emp_count'].shift(1).fillna(0)
                        merged['total_emp'] = merged['cum_hired_emp_count'] - merged['new_count']
                        merged['pct'] = (merged['total_emp_left'] / merged['total_emp'].replace(0, 1)) * 100
                        result = merged[merged['total_emp'] > 0].sort_values('year')
        
                        plt.figure(figsize=(14, 6))
                        plt.plot(result['year'], result['pct'], marker='o', markersize=8,
                                color='royalblue', linewidth=3, label='Attrition Rate')
                        plt.title('Employee Attrition Rate Trend', fontsize=16,fontweight='bold', pad=20)
                        plt.xlabel('Year', fontsize=12)
                        plt.ylabel('Attrition Rate (%)', fontsize=12)
                        for x, y in zip(result['year'], result['pct']):
                            plt.text(x, y, f'{y:.1f}%', ha='center', va='bottom', fontsize=10, weight='bold')
                        plt.grid(alpha=0.2)
                        plt.legend()
                        st.pyplot(plt)
                    else:
                        st.warning("Required columns (hire_date, last_date, left) not available for attrition analysis")
        
                with tab2:
                    st.header("Employee Analysis")
                    
                    # Visualization 3: Gender Distribution
                    female_count = df[df['sex'] == 'F'].shape[0]
                    male_count = df[df['sex'] == 'M'].shape[0]
                    gender_counts = pd.DataFrame({
                        'gender': ['Female', 'Male'],
                        'total_no': [female_count, male_count]
                    })
                    gender_counts['pct'] = (gender_counts['total_no'] * 100) / gender_counts['total_no'].sum()
        
                    plt.figure(figsize=(1, 1))
                    plt.pie(gender_counts['total_no'], labels=gender_counts['gender'], 
                           autopct='%1.1f%%', startangle=90, colors=['#ff9999', '#66b3ff'],textprops={'fontsize':6})
                    plt.title('Employee Distribution by Gender', fontsize=4)
                    plt.axis('equal')
                    st.pyplot(plt)
        
                    # Visualization 4: Performance Rating Distribution
                    grouped_df = df.groupby("Last_performance_rating")["emp_no"].nunique().reset_index(name="total_emp")  
                    grouped_df["pct"] = (grouped_df["total_emp"] * 100.0) / grouped_df["total_emp"].sum()
                    grouped_df = grouped_df.sort_values(by="total_emp", ascending=False)
        
                    plt.figure(figsize=(14, 5))
                    ax = sns.barplot(x="Last_performance_rating", y="total_emp", data=grouped_df, 
                                    hue="Last_performance_rating", palette="viridis")
                    for p in ax.patches:
                        ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()),
                                   ha='center', va='bottom', fontsize=10)
                    plt.title("Employee Distribution by Last Performance Rating", fontsize=16,fontweight='bold')
                    plt.xlabel("Last Performance Rating", fontsize=12)
                    plt.ylabel("Total Employees", fontsize=12)
                    ax2 = plt.gca().twinx()
                    sns.lineplot(x="Last_performance_rating", y="pct", data=grouped_df, 
                                ax=ax2, color="red", marker="o", label="Percentage", linewidth=2)
                    ax2.set_ylabel("Percentage of Total (%)", fontsize=12, color="red")
                    plt.xticks(rotation=45)
                    st.pyplot(plt)
        
                    # Visualization 5: Job Title Distribution
                    result = df.groupby("title")["emp_no"].nunique().reset_index(name="total_emp")  
                    result = result.sort_values(by="total_emp", ascending=False)
                    plt.figure(figsize=(14, 5))
                    sns.barplot(x="title", y="total_emp", data=result, hue="title", palette="viridis")
                    plt.title("Employee Count by Job Title", fontsize=16,fontweight='bold')
                    plt.xlabel("Job Title", fontsize=12)
                    plt.ylabel("Number of Employees", fontsize=12)
                    plt.xticks(rotation=45, fontsize=12)
                    for index, value in enumerate(result["total_emp"]):
                        plt.text(index, value + 0.1, str(value), ha="center", va="bottom", fontsize=12)
                    st.pyplot(plt)
        
                    # Visualization 6: Projects Distribution
                    df['project_category'] = pd.cut(
                        df['no_of_projects'],
                        bins=[0, 3, 7, 10],
                        labels=['Low(1-3)', 'Medium(4-7)', 'High(8-10)'],
                        right=True,
                        include_lowest=True
                    )
                    summary = (df.groupby('project_category', observed=True)['emp_no']
                             .nunique()
                             .reset_index()
                             .rename(columns={'emp_no': 'Total_emp'}))
                    plt.figure(figsize=(14, 5))
                    ax = sns.barplot(x='project_category', y='Total_emp', data=summary, 
                                    hue='project_category', palette='viridis')
                    plt.title('Employee Distribution by No of Projects', fontsize=16,fontweight='bold')
                    plt.xlabel('Project Category', fontsize=12)
                    plt.ylabel('Total Employees', fontsize=12)
                    for index, value in enumerate(summary['Total_emp']):
                        plt.text(index, value * 0.5, str(value), color='white', ha='center', va='bottom', fontsize=12)
                    st.pyplot(plt)
        
                    # Visualization 7: Tenure Distribution
                    def tenure_group(tenure):
                        if 1 <= tenure <= 4: return "Low Tenure(1-4)"
                        elif 4 < tenure <= 8: return "Medium Tenure(5-8)"
                        else: return "High Tenure(9+)"
                    df["tenure_group"] = df["tenure"].apply(tenure_group)
                    grouped_df = df.groupby("tenure_group")['emp_no'].nunique().reset_index(name="NO_OF_EMP")
                    grouped_df["PCT"] = (grouped_df["NO_OF_EMP"] * 100.00) / grouped_df["NO_OF_EMP"].sum()
        
                    plt.figure(figsize=(14, 5))
                    ax = sns.barplot(x="tenure_group", y="NO_OF_EMP", data=grouped_df, 
                                    hue="tenure_group", palette="viridis")
                    for p in ax.patches:
                        ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()),
                                   ha='center', va='bottom', fontsize=10)
                    plt.title("Employee distribution by Tenure Group", fontsize=16,fontweight='bold')
                    plt.xlabel("Tenure Group", fontsize=12)
                    plt.ylabel("Number of Employees", fontsize=12)
                    st.pyplot(plt)
        
                    # Visualization 8: Hiring Trend
                    df["hire_year"] = pd.to_datetime(df["hire_date"]).dt.year
                    result = df.groupby("hire_year")["emp_no"].nunique().reset_index(name="employee_count") 
                    result = result.sort_values(by="hire_year")
                    plt.figure(figsize=(14, 5))
                    ax = sns.lineplot(x='hire_year', y='employee_count', data=result, marker='o', color='blue')
                    plt.title('Employee Hired Trends by Year', fontsize=16,fontweight='bold')
                    plt.xlabel('Year', fontsize=12)
                    plt.ylabel('Number of Employees', fontsize=12)
                    for index, row in result.iterrows():
                        plt.text(row['hire_year'], row['employee_count'] + 0.1, f"{row['employee_count']:,}", 
                                ha='center', va='bottom', fontsize=10)
                    st.pyplot(plt)
        
                    # Visualization 9: Exit Trends
                    if 'last_date' in df.columns:
                        df['exit_year'] = df['last_date'].dt.year
                        exit_counts = (df.groupby('exit_year', observed=True)
                                      .agg(total_exits=('emp_no', 'count'))
                                      .reset_index()
                                      .sort_values('exit_year'))
                        plt.figure(figsize=(14, 5))
                        ax = sns.lineplot(x='exit_year', y='total_exits', data=exit_counts,
                                         marker='o', markersize=8, linewidth=2.5, color='#e63946')
                        plt.title('Employee Exit Trends by Year', fontsize=16,fontweight='bold', pad=20)
                        plt.xlabel('Year', fontsize=12)
                        plt.ylabel('Number of Exits', fontsize=12)
                        for x, y in zip(exit_counts['exit_year'], exit_counts['total_exits']):
                            ax.text(x, y + 0.5, f'{y:,}', ha='center', va='bottom',
                                   fontsize=10, bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
                        st.pyplot(plt)
        
                    # Visualization 10: Total Employees by Year
                    if all(col in df.columns for col in ['hire_date', 'last_date']):
                        hired = df.groupby(df['hire_date'].dt.year)["emp_no"].nunique().reset_index(name="total_emp_hired")
                        left = df[df['left'] == 1].groupby(df['last_date'].dt.year)["emp_no"].nunique().reset_index(name="total_emp_left")
                        all_years = pd.DataFrame({'years': pd.Series(sorted(set(hired['hire_date'].tolist() + left['last_date'].tolist()))).astype(int)})
                        merged = pd.merge(all_years, hired, left_on='years', right_on='hire_date', how='left').fillna(0)
                        merged = pd.merge(merged, left, left_on='years', right_on='last_date', how='left').fillna(0)
                        merged.drop(['hire_date', 'last_date'], axis=1, inplace=True)
                        merged['cum_hired_emp_count'] = merged['total_emp_hired'].cumsum().astype(int)
                        merged['cum_left_emp_count'] = merged['total_emp_left'].cumsum().astype(int)
                        merged['new_count'] = merged['cum_left_emp_count'].shift(1).fillna(0).astype(int)
                        merged['total_emp'] = merged['cum_hired_emp_count'] - merged['new_count']
        
                        plt.figure(figsize=(20, 7))
                        plt.plot(merged['years'], merged['total_emp'], marker='o', color='skyblue', label='Total Employees')
                        for index, value in enumerate(merged['total_emp']):
                            plt.text(merged['years'].iloc[index], value + 50, f"{value:,}", 
                                    ha='center', fontsize=10, bbox=dict(facecolor='white', alpha=0.7, edgecolor='gray'))
                        plt.title('Total Employee by Year', fontsize=20,fontweight='bold')
                        plt.xlabel('Year', fontsize=16)
                        plt.ylabel('Total Employee Count', fontsize=16)
                        plt.xticks(merged['years'], fontsize=12, rotation=45)
                        st.pyplot(plt)
        
                with tab3:
                    st.header("Department Level Analysis")
                    
                    # Visualization 11: Employees by Department
                    result = df.groupby('dept_name')["emp_no"].nunique().reset_index(name='total_emp')
                    result = result.sort_values(by='total_emp', ascending=False).reset_index(drop=True)
                    plt.figure(figsize=(14, 5))
                    ax = sns.barplot(x='total_emp', y='dept_name', data=result, palette='Blues_r')
                    for index, value in enumerate(result['total_emp']):
                        ax.text(value + 1, index, f"{value:,}", va='center')
                    plt.title('Total Employees by Department', fontsize=16,fontweight='bold')
                    plt.xlabel('Total Employees', fontsize=12)
                    plt.ylabel('Department Name', fontsize=12)
                    st.pyplot(plt)
        
                    # Visualization 12: Average Salary by Department
                    df_grouped = df.groupby('dept_name').agg(
                        avg_salary=('salary', 'mean'),
                        total_employees=('salary', 'count')
                    ).reset_index()
                    df_grouped = df_grouped.sort_values(by='avg_salary', ascending=False)
                    plt.figure(figsize=(14, 5))
                    bars = plt.bar(df_grouped['dept_name'], df_grouped['avg_salary'], color='skyblue')
                    for bar, count in zip(bars, df_grouped['total_employees']):
                        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), 
                                f'{count:,}', ha='center', va='bottom')
                    plt.title('Average Salary by Department',fontsize=16,fontweight='bold')
                    plt.xlabel('Department Name',fontsize=12)
                    plt.ylabel('Average Salary',fontsize=12)
                    plt.xticks(rotation=45, ha='right')
                    st.pyplot(plt)
        
                    # Visualization 13: Managers by Department
                    manager_counts = (df[df['title'] == 'Manager']
                                     .groupby('dept_name')['emp_no']
                                     .count()
                                     .reset_index()
                                     .rename(columns={'emp_no': 'total_manager'})
                                     .sort_values(by='total_manager', ascending=False))
                    plt.figure(figsize=(14, 5))
                    ax = sns.barplot(x='dept_name', y='total_manager', hue='dept_name', 
                                    data=manager_counts, palette='dark:#1f3b6f_r', legend=False)
                    for p in ax.patches:
                        ax.annotate(f"{p.get_height():,.0f}", 
                                   (p.get_x() + p.get_width() / 2, p.get_height() / 2),
                                   ha='center', va='center', color='white', fontsize=10, fontweight='bold')
                    plt.title('Total Managers by Department', fontsize=16, fontweight='bold')
                    plt.xlabel('Department Name', fontsize=12)
                    plt.ylabel('Total Managers', fontsize=12)
                    st.pyplot(plt)
        
                with tab4:
                    st.header("Salary Analysis")
                    
                    # Visualization 14: Year-wise Average Salary
                    if all(col in df.columns for col in ['hire_date', 'last_date', 'salary']):
                        try:
                            final_table = df.copy()
                            
                            # Your exact calculation code
                            final_table['hire_year'] = final_table['hire_date'].dt.year
                            final_table['last_year'] = final_table['last_date'].dt.year
        
                            # First get unique employees by hire_year with their salaries
                            unique_hires = final_table.drop_duplicates(subset=['emp_no', 'hire_year'])
        
                            # Then aggregate by hire_year
                            hired_df = unique_hires.groupby('hire_year').agg({
                                'emp_no': 'count',          # Count of unique employees (since we already deduplicated)
                                'salary': 'sum'             # Sum of salaries for these unique employees
                            }).rename(columns={
                                'emp_no': 'total_emp_hired',
                                'salary': 'total_salary_hired'
                            })
        
                            # Similarly for employees who left (if needed)
                            unique_leavers = final_table[final_table['left'] == 1].drop_duplicates(subset=['emp_no', 'last_year'])
        
                            left_df = unique_leavers.groupby('last_year').agg({
                                'emp_no': 'count',
                                'salary': 'sum'
                            }).rename(columns={
                                'emp_no': 'total_emp_left',
                                'salary': 'total_salary_left'
                            })
        
                            merged_df = pd.merge(hired_df, left_df, left_index=True, right_index=True, how='outer').fillna(0)
                            merged_df.reset_index(inplace=True)
                            merged_df.rename(columns={'index': 'years'}, inplace=True)
                            merged_df['years'] = merged_df['years'].astype(int)
        
                            merged_df['cum_hired_emp_count'] = merged_df['total_emp_hired'].cumsum().astype(int)
                            merged_df['cum_left_emp_count'] = merged_df['total_emp_left'].cumsum().astype(int)
                            merged_df['cum_hired_salary'] = merged_df['total_salary_hired'].cumsum().round(2)
                            merged_df['cum_left_salary'] = merged_df['total_salary_left'].cumsum().round(2)
        
                            merged_df['new_count'] = merged_df['cum_left_emp_count'].shift(1).fillna(0).astype(int)
                            merged_df['total_emp'] = merged_df['cum_hired_emp_count'] - merged_df['new_count']
                            merged_df['new_sal'] = merged_df['cum_hired_salary'].shift(1).fillna(0).round(2)
                            merged_df['total_sal'] = merged_df['cum_hired_salary'] - merged_df['cum_left_salary'].shift(1).fillna(0)
                            merged_df['avg_sal'] = (merged_df['total_sal'] / merged_df['total_emp'].replace(0, 1)).round(2)  # Added .replace(0,1) to avoid divide by zero
        
                            # Fixed visualization for Streamlit
                            fig, ax = plt.subplots(figsize=(12, 6))  # Reduced size from 24 to 12
                            
                            # Your exact plotting code
                            ax.plot(merged_df['years'].astype(str), merged_df['avg_sal'], 
                                marker='o', color='skyblue', linestyle='-', linewidth=2)
        
                            for i, val in enumerate(merged_df['avg_sal']):
                                ax.text(i, val, f'{val:,.2f}', ha='center', va='bottom', rotation=90)
        
                            ax.set_title('Average Salary by Year',fontsize=18,fontweight='bold')
                            ax.set_xlabel('Year',fontsize=14)
                            ax.set_ylabel('Average Salary',fontsize=14)
                            ax.grid(axis='y', linestyle='--', alpha=0.5)
                            
                            plt.tight_layout()  # Prevent label cutoff
                            st.pyplot(fig)  # Streamlit display
                            plt.close(fig)  # Clean up memory
        
        
        
                        except Exception as e:
                            st.error(f"Error generating salary trend: {str(e)}")
                            st.error(f"Traceback: {traceback.format_exc()}")
                    else:
                        st.warning("Required columns (hire_date, last_date, salary) not available")
        
        
                    # Visualization 15: Salary by Job Title
                    result = df.groupby(['title', 'emp_no'])['salary'].mean().reset_index()
                    result = result.groupby('title')['salary'].mean().reset_index(name='avg_sal')
                    result = result.sort_values(by='avg_sal', ascending=False)
                    plt.figure(figsize=(10, 4))
                    ax = sns.barplot(x='title', y='avg_sal', data=result, palette='viridis')
                    plt.title('Average Salary by Job Title', fontsize=14,fontweight='bold')
                    plt.xlabel('Job Title', fontsize=10)
                    plt.ylabel('Average Salary', fontsize=10)
                    for index, value in enumerate(result['avg_sal']):
                        ax.annotate(f'{value:.2f}', (index, value + 500),
                                   ha='center', va='bottom', fontsize=10)
                    st.pyplot(plt)
        
                    # Visualization 16: Salary by Performance Rating
                    filtered_table = df.drop_duplicates(subset='emp_no')
                    result = filtered_table.groupby('Last_performance_rating').agg(
                        avg_salary=('salary', 'mean'),
                        employee_count=('emp_no', 'size')
                    ).reset_index()
                    result = result.sort_values(by='Last_performance_rating')
                    plt.figure(figsize=(10, 4))
                    plt.bar(result['Last_performance_rating'].astype(str), result['avg_salary'], color='skyblue')
                    for i, val in enumerate(result['avg_salary']):
                        plt.text(i, val, f'{val:,.2f}', ha='center', va='bottom')
                    plt.title('Average Salary by Last Performance Rating',fontsize=14,fontweight='bold')
                    plt.xlabel('Last Performance Rating',fontsize=10)
                    plt.ylabel('Average Salary',fontsize=10)
                    st.pyplot(plt)
        
                    # Visualization 17: Employees by Salary Range
                    df['salary'] = df.groupby('emp_no')['salary'].transform('mean').round()
                    df['salary_range'] = pd.cut(
                        df['salary'],
                        bins=[39999, 60000, 80000, 100000, 129492],
                        labels=['40k-60k', '60k-80k', '80k-100k', '100k-130k'],
                        right=True
                    )
                    salary_dist = df.groupby('salary_range', observed=False).agg(
                        NO_OF_EMP=('emp_no', 'nunique')
                    ).reset_index()
                    plt.figure(figsize=(10, 4))
                    ax = sns.barplot(x='salary_range', y='NO_OF_EMP', data=salary_dist, color='skyblue')
                    for i, row in salary_dist.iterrows():
                        ax.annotate(f"{row['NO_OF_EMP']}", (i, row['NO_OF_EMP']), 
                                   ha='center', va='bottom')
                    plt.title('Employees by Salary Range', fontsize=14,fontweight='bold')
                    plt.xlabel('Salary Range', fontsize=10)
                    plt.ylabel('Total Employees', fontsize=10)
                    st.pyplot(plt)
        
        if __name__ == "__main__":
            main()
