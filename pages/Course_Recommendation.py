import streamlit as st
import google.generativeai as genai
import pymongo
from typing import Dict, List
import os

class StudentRecommendationApp:
    def __init__(self):
        # Securely load API key from environment or secrets
        gemini_api_key = st.secrets.get("GEMINI_API_KEY")
        # gemini_api_key = os.getenv("GEMINI_API_KEY", st.secrets.get("GEMINI_API_KEY"))
        genai.configure(api_key=gemini_api_key)
        
        self.gemini_model = genai.GenerativeModel('gemini-pro')
        
        # MongoDB Connection
        mongo_connection_string = st.secrets.get("MONGO_CONNECTION_STRING")
        # mongo_connection_string = os.getenv("MONGO_CONNECTION_STRING", st.secrets.get("MONGO_CONNECTION_STRING"))
        self.mongo_client = pymongo.MongoClient(mongo_connection_string)
        self.db = self.mongo_client['student_recommendation_db']
        self.students_collection = self.db['students']
        
        # Create a unique index on the name field to ensure uniqueness
        self.students_collection.create_index([("name", pymongo.ASCENDING)], unique=True)
    
    def collect_student_details(self) -> Dict:
        """
        Collect comprehensive student details through Streamlit form
        """
        st.header("Student Profile & Learning Recommendation")
        
        with st.form("student_details"):
            # Personal Details
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Full Name", placeholder="Enter your full name")
                email = st.text_input("Email Address", placeholder="your.email@example.com")
                phone = st.text_input("Phone Number", placeholder="+91 XXXXXXXXXX")
            
            with col2:
                roll_no = st.text_input("Roll Number/Student ID")
                age = st.number_input("Age", min_value=16, max_value=65)
                gender = st.selectbox("Gender", ["Select", "Male", "Female", "Other"])
            
            # Academic Details
            st.subheader("Academic Information")
            current_education_level = st.selectbox("Current Education Level", [
                "High School", 
                "Undergraduate", 
                "Postgraduate", 
                "Professional Degree",
                "Doctoral"
            ])
            
            field_of_study = st.selectbox("Field of Study", [
                "Computer Science", 
                "Engineering", 
                "Data Science", 
                "Business", 
                "Arts & Humanities", 
                "Social Sciences",
                "Natural Sciences",
                "Other"
            ])
            
            # Performance Metrics
            st.subheader("Performance & Skills")
            previous_marks = st.number_input("Previous Evaluation Marks (%)", min_value=0.0, max_value=100.0)
            
            technical_skills = st.multiselect("Technical Skills", [
                "Programming", 
                "Data Analysis", 
                "Machine Learning", 
                "Web Development",
                "Cloud Computing",
                "Cybersecurity",
                "None"
            ])
            
            learning_interests = st.multiselect("Learning Interests", [
                "Software Development",
                "Data Science",
                "Artificial Intelligence",
                "Cloud Technologies",
                "Digital Marketing",
                "Business Analytics",
                "UX/UI Design",
                "Cybersecurity"
            ])
            
            submit_button = st.form_submit_button("Generate Personalized Recommendations")
            
            if submit_button:
                # Validate required fields
                if not name:
                    st.error("Full Name is required")
                    return None
                
                student_data = {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "roll_no": roll_no,
                    "age": age,
                    "gender": gender,
                    "education_level": current_education_level,
                    "field_of_study": field_of_study,
                    "previous_marks": previous_marks,
                    "technical_skills": technical_skills,
                    "learning_interests": learning_interests
                }
                return student_data
        
        return None
    
    def analyze_student_profile(self, student_data: Dict) -> str:
        """
        Use Gemini API to analyze student profile and generate recommendations
        """
        prompt = f"""
        Analyze the following student profile and suggest personalized learning paths:
        
        Profile Details:
        - Education Level: {student_data['education_level']}
        - Field of Study: {student_data['field_of_study']}
        - Previous Marks: {student_data['previous_marks']}%
        - Technical Skills: {', '.join(student_data['technical_skills'])}
        - Learning Interests: {', '.join(student_data['learning_interests'])}
        
        Provide a detailed recommendation for online courses, learning platforms, 
        and potential career growth paths based on this profile.
        """
        
        recommendation = self.gemini_model.generate_content(prompt)
        return recommendation.text
    
    def recommend_courses(self, analysis: str) -> List[Dict]:
        """
        Extract course recommendations from Gemini analysis
        """
        # Placeholder for actual course recommendation logic
        courses = [
            {
                "platform": "Coursera",
                "title": "Machine Learning Specialization",
                "url": "https://www.coursera.org/specializations/machine-learning",
                "difficulty": "Intermediate"
            },
            {
                "platform": "Udemy",
                "title": "Complete Python Bootcamp",
                "url": "https://www.udemy.com/course/complete-python-bootcamp/",
                "difficulty": "Beginner"
            }
        ]
        return courses
    
    def save_student_data(self, student_data: Dict):
        """
        Save or update student data in MongoDB using upsert
        """
        try:
            # Use upsert to update existing record or insert new one
            result = self.students_collection.update_one(
                {"name": student_data["name"]},  # Filter by name
                {"$set": student_data},  # Update or set all fields
                upsert=True  # Create new document if not exists
            )
            
            # Provide feedback to user
            if result.upserted_id:
                st.success(f"New student profile created for {student_data['name']}")
            else:
                st.info(f"Profile updated for {student_data['name']}")
        
        except pymongo.errors.DuplicateKeyError:
            st.error(f"Error: A profile with the name {student_data['name']} already exists.")
        except Exception as e:
            st.error(f"An error occurred while saving the profile: {str(e)}")
    
    def run(self):
        """
        Main application flow
        """
        st.title("Personalized Learning Recommendation Platform")
        
        student_data = self.collect_student_details()
        
        if student_data:
            # Analyze profile
            analysis = self.analyze_student_profile(student_data)
            st.write("Profile Analysis:", analysis)
            
            # Get course recommendations
            recommended_courses = self.recommend_courses(analysis)
            
            st.subheader("Recommended Courses")
            for course in recommended_courses:
                st.write(f"**{course['title']}** on {course['platform']}")
                st.write(f"Difficulty: {course['difficulty']}")
                st.write(f"[Enroll Now]({course['url']})")
            
            # Save/Update student data
            self.save_student_data(student_data)

def main():
    st.set_page_config(
        page_title="Student Recommendation",
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

    app = StudentRecommendationApp()
    app.run()

if __name__ == "__main__":
    main()
