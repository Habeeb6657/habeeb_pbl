import streamlit as st
import google.generativeai as genai
import pymongo
from typing import Dict, List
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

class StudentDashboard:
    def __init__(self):
        # MongoDB Connection
        mongo_connection_string = st.secrets.get("MONGO_CONNECTION_STRING")
        # mongo_connection_string = os.getenv("MONGO_CONNECTION_STRING", st.secrets.get("MONGO_CONNECTION_STRING"))
        self.mongo_client = pymongo.MongoClient(mongo_connection_string)
        self.db = self.mongo_client['student_recommendation_db']
        self.students_collection = self.db['students']

    def get_students_dataframe(self):
        """
        Retrieve students data and convert to pandas DataFrame
        """
        # Fetch all students data
        students_data = list(self.students_collection.find())
        
        # Convert to DataFrame
        if students_data:
            df = pd.DataFrame(students_data)
            # Drop MongoDB's internal _id column
            df = df.drop('_id', axis=1, errors='ignore')
            return df
        return pd.DataFrame()

    def render_dashboard(self):
        """
        Create comprehensive student dashboard with various visualizations
        """
        st.title("📊 Student Insights Dashboard")

        # Fetch students data
        df = self.get_students_dataframe()

        if df.empty:
            st.warning("No student data available.")
            return

        # Dashboard Layout
        col1, col2 = st.columns(2)

        # 1. Education Level Distribution
        with col1:
            st.subheader("Education Level Distribution")
            education_counts = df['education_level'].value_counts()
            fig_edu = px.pie(
                values=education_counts.values, 
                names=education_counts.index, 
                title="Students by Education Level"
            )
            st.plotly_chart(fig_edu)

        # 2. Field of Study Distribution
        with col2:
            st.subheader("Field of Study Breakdown")
            field_counts = df['field_of_study'].value_counts()
            fig_field = px.bar(
                x=field_counts.index, 
                y=field_counts.values, 
                title="Students Across Different Fields",
                labels={'x': 'Field of Study', 'y': 'Number of Students'}
            )
            st.plotly_chart(fig_field)

        # 3. Performance Metrics
        st.subheader("Performance Analysis")
        col3, col4 = st.columns(2)

        with col3:
            # Boxplot of Previous Marks
            fig_marks = px.box(df, y='previous_marks', title='Previous Marks Distribution')
            st.plotly_chart(fig_marks)

        with col4:
            # Average Marks by Education Level
            avg_marks = df.groupby('education_level')['previous_marks'].mean()
            fig_avg_marks = px.bar(
                x=avg_marks.index, 
                y=avg_marks.values, 
                title='Average Marks by Education Level',
                labels={'x': 'Education Level', 'y': 'Average Marks'}
            )
            st.plotly_chart(fig_avg_marks)

        # 4. Technical Skills Analysis
        st.subheader("Technical Skills Landscape")
        
        # Flatten the technical skills
        all_skills = [skill for skills in df['technical_skills'] for skill in skills]
        skill_counts = pd.Series(all_skills).value_counts()
        
        fig_skills = px.bar(
            x=skill_counts.index, 
            y=skill_counts.values, 
            title='Distribution of Technical Skills',
            labels={'x': 'Technical Skills', 'y': 'Number of Students'}
        )
        st.plotly_chart(fig_skills)

        # 5. Learning Interests
        st.subheader("Learning Interests Overview")
        all_interests = [interest for interests in df['learning_interests'] for interest in interests]
        interest_counts = pd.Series(all_interests).value_counts()
        
        fig_interests = px.pie(
            values=interest_counts.values, 
            names=interest_counts.index, 
            title="Student Learning Interests"
        )
        st.plotly_chart(fig_interests)

        # 6. Detailed Student Data Table
        st.subheader("Student Details")
        st.dataframe(df)

def main():
    st.set_page_config(
        page_title="Students Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_st_style, unsafe_allow_html=True)

    dashboard = StudentDashboard()
    dashboard.render_dashboard()

if __name__ == "__main__":
    main()
