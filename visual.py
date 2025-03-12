import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests

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
                # Convert date columns to datetime (if applicable)
                if "hire_date" in df.columns:
                    df["hire_date"] = pd.to_datetime(df["hire_date"])
                if "last_date" in df.columns:
                    df["last_date"] = pd.to_datetime(df["last_date"])
        
                # Calculate tenure (in years)
                if "hire_date" in df.columns and "last_date" in df.columns:
                    df["tenure"] = (df["last_date"].fillna(pd.Timestamp.today()) - df["hire_date"]).dt.days / 365
        
                # Sidebar filters
                st.sidebar.header("🔍 Filters")
                department_name = st.sidebar.multiselect("Department Name", df["dept_names"].unique())
                left_filter = st.sidebar.selectbox("Left", ["All", "Left", "Stayed"])
                title_filter = st.sidebar.multiselect("Job Title", df["title"].unique())
                hire_year_filter = st.sidebar.multiselect("Hire Year", df["hire_date"].dt.year.unique())
        
                # Apply filters
                if department_name:
                    df = df[df["dept_names"].isin(department_name)]
                if left_filter == "Left":
                    df = df[df["left"] == 1]
                elif left_filter == "Stayed":
                    df = df[df["left"] == 0]
                if title_filter:
                    df = df[df["title"].isin(title_filter)]
                if hire_year_filter:
                    df = df[df["hire_date"].dt.year.isin(hire_year_filter)]
        
                # Custom CSS to reduce font size of metrics
                st.markdown("""
                    <style>
                    .stMetric {
                        font-size: 6px !important;
                    }
                    </style>
                    """, unsafe_allow_html=True)
        
                # Display key metrics
                st.header("📈 Key Metrics")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Employees", f"{df.shape[0]:,}")
                with col2:
                    st.metric("Employees Left", f"{df[df["left"] == 1].shape[0]:,}")
                with col3:
                    st.metric("Employees Stayed", f"{df[df["left"] == 0].shape[0]:,}")
        
        
                col4, col5, col6 = st.columns(3)
        
                with col4:
                    st.metric("Average Salary", f"{int(df['salary'].mean()):,}")
                with col5:
                    st.metric("Average Tenure", f"{df['tenure'].mean():.2f} yr")
                with col6:
                    st.metric("Median Tenure", f"{df['tenure'].median():.2f} yr")
        
                # Visualization 1: Salary Distribution
                st.header("📊 Salary Distribution Among Employees")
                plt.figure(figsize=(6, 4))
                plt.hist(df["salary"], bins=5, color="skyblue", edgecolor="black")
                plt.title("Salary Distribution Among Employees")
                plt.xlabel("Salary")
                plt.ylabel("Number of Employees")
                plt.grid(False)
                st.pyplot(plt)
        

        
                # Visualization 2: Tenure Distribution
                st.header("📊 Tenure Distribution of Employees")
                plt.figure(figsize=(6, 4))
                plt.hist(df["tenure"], color="skyblue", edgecolor="black")
                plt.title("Tenure Distribution of Employees")
                plt.xlabel("Tenure (Years)")
                plt.ylabel("Number of Employees")
                plt.grid(axis="y", linestyle="--", alpha=0.7)
                st.pyplot(plt)
        
                # Visualization 3: Employee  Distribution
                st.header("📊 Employee Distribution")
                emp_left = df[df["left"] == 1].shape[0]
                emp_stayed = df[df["left"] == 0].shape[0]
                result_df = pd.DataFrame({
                    "emp_status": ["Left", "Stayed"],
                    "no_of_emp": [emp_left, emp_stayed]
                })
                result_df["percntg"] = (result_df["no_of_emp"] * 100.00) / result_df["no_of_emp"].sum()
                colors = sns.color_palette("pastel")
                plt.figure(figsize=(2, 2))
                plt.pie(result_df["no_of_emp"], labels=result_df["emp_status"], autopct="%1.1f%%", colors=colors, startangle=140, textprops={"fontsize": 8} )
                plt.title("Employee Distribution", fontsize=4)
                st.pyplot(plt)
        
                # Visualization 4: Employee Distribution by Gender
                st.header("📊 Employee Distribution by Gender")
                male_emp = df[(df["sex"] == "M")].shape[0]
                female_emp = df[ (df["sex"] == "F")].shape[0]
                gen_df = pd.DataFrame({
                    "emp_gender": ["Male", "Female"],
                    "no_of_emp": [male_emp, female_emp]
                })
                plt.figure(figsize=(6, 4))
                sns.barplot(x="emp_gender", y="no_of_emp", data=gen_df, hue="emp_gender", legend=False, palette="coolwarm")
                plt.xlabel("Gender")
                plt.ylabel("Number of Employees ")
                plt.title("Employee Distribution by Gender")
                st.pyplot(plt)

                # Visualization 5: Number of Employees by Job Title
                st.header("📊 Number of Employees by Job Title")
                result = df.groupby("title").size().reset_index(name="total_emp")
                result = result.sort_values(by="total_emp", ascending=False)
                
           
                plt.figure(figsize=(10, 6))
                sns.barplot(x="title", y="total_emp", data=result, hue="title", palette="viridis", legend=False)
                plt.title("Number of Employees by Job Title", fontsize=16)
                plt.xlabel("Job Title", fontsize=14)
                plt.ylabel("Number of Employees", fontsize=14)
                plt.xticks(rotation=45, fontsize=12)
                plt.yticks(fontsize=12)
                
                # Add value labels on top of each bar
                for index, value in enumerate(result["total_emp"]):
                    plt.text(index, value + 0.1, f"{value:,}", ha="center", va="bottom", fontsize=12) 
                
                plt.tight_layout()
                
           
                st.pyplot(plt)

                # Visualization 6: Average Salary by Job Title
                st.header("📊 Average Salary by Job Title")
                result = df.groupby("title")["salary"].mean().reset_index(name="avg_sal")
                result = result.sort_values(by="avg_sal", ascending=False)
                plt.figure(figsize=(10, 6))
                sns.barplot(x="title", y="avg_sal", data=result, hue="title", palette="viridis")
                plt.title("Average Salary by Job Title", fontsize=16)
                plt.xlabel("Job Title", fontsize=14)
                plt.ylabel("Average Salary", fontsize=14)
                plt.xticks(rotation=45, fontsize=12)
                plt.yticks(fontsize=12)
                for index, value in enumerate(result["avg_sal"]):
                    plt.text(index, value + 500, f"{int(value):,}", ha="center", va="bottom", fontsize=12)
                plt.tight_layout()
                st.pyplot(plt)
        

        
                # Visualization 7: Employee Distribution by Salary Range
                st.header("📊 Employee Distribution by Salary Range")
                def get_salary_range(salary):
                    if 40000 <= salary <= 60000:
                        return "40k-60k"
                    elif 60001 <= salary <= 80000:
                        return "60k-80k"
                    elif 80001 <= salary <= 100000:
                        return "80k-100k"
                    elif 100001 <= salary <= 129492:
                        return "100k-130k"
                    else:
                        return "Unknown"
                df["salary_range"] = df["salary"].apply(get_salary_range)
                salary_counts = df.groupby("salary_range")["emp_no"].count().reset_index(name="NO_OF_EMP")
                total_employees = salary_counts["NO_OF_EMP"].sum()
                salary_counts["PCT"] = salary_counts["NO_OF_EMP"] * 100.0 / total_employees
                salary_counts_sorted = salary_counts.sort_values("salary_range")
                plt.figure(figsize=(12, 6))
                sns.barplot(data=salary_counts_sorted, x="salary_range", y="NO_OF_EMP", hue="salary_range", palette="viridis")
                plt.title("Employee Distribution by Salary Range")
                plt.xlabel("Salary Range")
                plt.ylabel("Number of Employees")
                ax2 = plt.gca().twinx()
                sns.lineplot(data=salary_counts_sorted, x="salary_range", y="PCT", ax=ax2, color="red", marker="o", label="Percentage", linewidth=2)
                ax2.set_ylabel("Percentage of Total (%)", fontsize=12, color="red")
                plt.xticks(rotation=45, ha="right")
                st.pyplot(plt)


        
                # Visualization 8: Total Number of People and Percentage by Last Performance Rating
                st.header("📊 Total Number of People and Percentage by Last Performance Rating")
               
                grouped_df = df.groupby("Last_performance_rating").size().reset_index(name="total_no")
                total_count = grouped_df["total_no"].sum()
                grouped_df["pct"] = (grouped_df["total_no"] * 100.0) / total_count
                grouped_df = grouped_df.sort_values(by="total_no", ascending=False)
                plt.figure(figsize=(12, 6))
                sns.barplot(x="Last_performance_rating", y="total_no", data=grouped_df, hue="Last_performance_rating", palette="viridis")
                plt.title("Total Number of People and Percentage by Last Performance Rating", fontsize=16)
                plt.xlabel("Last Performance Rating", fontsize=12)
                plt.ylabel("Total Number of People", fontsize=12)
                ax2 = plt.gca().twinx()
                sns.lineplot(x="Last_performance_rating", y="pct", data=grouped_df, ax=ax2, color="red", marker="o", label="Percentage", linewidth=2)
                ax2.set_ylabel("Percentage of Total (%)", fontsize=12, color="red")
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(plt)
        
                # Visualization 9: Number of Employees by Tenure Group
                st.header("📊 Number of Employees by Tenure Group")
                
                def tenure_group(tenure):
                    if 1 <= tenure <= 4:
                        return "Low Tenure(>=1 to <=4)"
                    elif 4 < tenure <= 8:
                        return "Medium Tenure(>4 to <=8)"
                    else:
                        return "High Tenure(>8 to <=14)"
                df["tenure_group"] = df["tenure"].apply(tenure_group)
                grouped_df = df.groupby("tenure_group").size().reset_index(name="NO_OF_EMP")
                grouped_df["PCT"] = (grouped_df["NO_OF_EMP"] * 100.00) / grouped_df["NO_OF_EMP"].sum()
                plt.figure(figsize=(10, 6))
                sns.barplot(x="tenure_group", y="NO_OF_EMP", data=grouped_df, hue="tenure_group", palette="viridis")
                plt.title("Number of Employees by Tenure Group", fontsize=16)
                plt.xlabel("Tenure Group", fontsize=14)
                plt.ylabel("Number of Employees", fontsize=14)
                plt.xticks(fontsize=12)
                plt.yticks(fontsize=12)
                st.pyplot(plt)
        
                # Visualization 10: Percentage of Employees by Tenure Group (Pie Chart)
                st.header("📊 Percentage of Employees by Tenure Group")
                plt.figure(figsize=(8, 8))
                plt.pie(
                    grouped_df["PCT"],
                    labels=grouped_df["tenure_group"],
                    autopct="%1.1f%%",
                    startangle=140,
                    colors=sns.color_palette("viridis", len(grouped_df)))
                plt.title("Percentage of Employees by Tenure Group", fontsize=16)
                st.pyplot(plt)
        
                # Visualization 11: Number and Percentage of Employees by Age Group
                st.header("📊 Number and Percentage of Employees by Age Group")
                df['hire_date'] = pd.to_datetime(df['birth_date'])
                df['last_date'] = pd.to_datetime(df['last_date'])
        
                df['birth_date'] = pd.to_datetime(df['birth_date'])
        
                df['age'] = ((df['last_date'].fillna(pd.Timestamp.today()) - df['birth_date']).dt.days) / 365
        
                
        
                def age_group(age):
                    if 21 <= age <= 30:
                        return "21-30"
                    elif 30 < age <= 40:
                        return "31-40"
                    elif 40 < age <= 50:
                        return "41-50"
                    elif 50 < age <= 60:
                        return "51-60"
                    else:
                        return ">60"
        
                df["age_group"] = df["age"].apply(age_group)
        
                grouped_df = df.groupby("age_group").size().reset_index(name="NO_OF_EMP")
                grouped_df["PCT"] = (grouped_df["NO_OF_EMP"] * 100.00) / grouped_df["NO_OF_EMP"].sum()
        
                fig, ax1 = plt.subplots(figsize=(12, 6))
                sns.barplot(x="age_group", y="NO_OF_EMP", data=grouped_df, hue="age_group", palette="viridis", ax=ax1)
                ax1.set_title("Number and Percentage of Employees by Age Group", fontsize=16)
                ax1.set_xlabel("Age Group", fontsize=14)
                ax1.set_ylabel("Number of Employees", fontsize=14)
                ax1.tick_params(axis="x", labelsize=12)
                ax1.tick_params(axis="y", labelsize=12)
        
                ax2 = ax1.twinx()
                sns.lineplot(x="age_group", y="PCT", data=grouped_df, color="red", marker="o", ax=ax2)
                ax2.set_ylabel("Percentage (%)", fontsize=14)
                ax2.tick_params(axis="y", labelsize=12)
        
                st.pyplot(fig)
        

                # Visualization 12: Number of Employees Hired by Year
                st.header("📊 Number of Employees Hired by Year")
                df["hire_year"] = pd.to_datetime(df["hire_date"]).dt.year
                
                result = df.groupby("hire_year").size().reset_index(name="employee_count")
                result = result.sort_values(by="hire_year")
                sns.set(style="dark")
                
                plt.figure(figsize=(10, 6))
                sns.lineplot(x='hire_year', y='employee_count', data=result, marker='o', color='blue')
                plt.title('Number of Employees Hired by Year', fontsize=16)
                plt.xlabel('Year', fontsize=14)
                plt.ylabel('Number of Employees', fontsize=14)
                plt.xticks(fontsize=12)
                plt.yticks(fontsize=12)
                
                for index, row in result.iterrows():
                    plt.text(row['hire_year'], row['employee_count'] + 0.1, f"{row['employee_count']:,}", ha='center', va='bottom', fontsize=12)
                
                plt.grid(False)
                plt.tight_layout()
                st.pyplot(plt)
        
                # Visualization 13: Number of Exits per Year
                st.header("📊 Number of Exits per Year")
                df["last_date"] = pd.to_datetime(df["last_date"], errors="coerce")
                df_valid = df[df["last_date"].notna()]
                df_valid["exit_year"] = df_valid["last_date"].dt.year
                exit_counts = df_valid.groupby("exit_year").agg(total_exits=("emp_no", "count")).reset_index()
                exit_counts_sorted = exit_counts.sort_values(by="exit_year").reset_index(drop=True)
                plt.figure(figsize=(6, 4))
                sns.lineplot(data=exit_counts_sorted, x="exit_year", y="total_exits", marker="o", color="blue")
                plt.title("Number of Exits per Year", fontsize=16)
                plt.xlabel("Exit Year", fontsize=12)
                plt.ylabel("Total Exits", fontsize=12)
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(plt)

        
                # Visualization 14: Average Salary by Hire Year
                st.header("📊 Average Salary by Hire Year")
                df["hire_year"] = pd.to_datetime(df["hire_date"]).dt.year
                
                result = df.groupby("hire_year")["salary"].mean().reset_index(name="avg_salary")
                result = result.sort_values(by="hire_year")
                plt.figure(figsize=(6, 4))
                sns.lineplot(data=result, x="hire_year", y="avg_salary", marker="o", color="green")
                plt.title("Average Salary by Hire Year", fontsize=16)
                plt.xlabel("Hire Year", fontsize=12)
                plt.ylabel("Average Salary", fontsize=12)
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(plt)
        
                # Visualization 15: Gender Distribution in the Company
                st.header("📊 Gender Distribution in the Company")
                female_count = df[df["sex"] == "F"].shape[0]
                male_count = df[df["sex"] == "M"].shape[0]
                gender_counts = pd.DataFrame({
                    "gender": ["Female", "Male"],
                    "total_no": [female_count, male_count]
                })
                total_count = gender_counts["total_no"].sum()
                gender_counts["pct"] = (gender_counts["total_no"] * 100) / total_count
                plt.figure(figsize=(3, 3))
                plt.pie(gender_counts["total_no"], labels=gender_counts["gender"], autopct="%1.1f%%", startangle=90, colors=["#ff9999", "#66b3ff"])
                plt.title("Gender Distribution in the Company", fontsize=16)
                plt.axis("equal")
                plt.tight_layout()
                st.pyplot(plt)

        # Run the app
        if __name__ == "__main__":
            main()
