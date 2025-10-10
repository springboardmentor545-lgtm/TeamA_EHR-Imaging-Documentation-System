import streamlit as st
import warnings
from datetime import datetime
warnings.filterwarnings('ignore')

# Import from our modules
from database import (
    init_db, create_medical_staff, create_patient_user, login_user, get_all_patients, 
    get_patient_by_id, get_patient_studies, save_report_to_db,
    get_patient_reports, get_all_reports, get_dashboard_stats,
    delete_report, delete_all_patient_reports, cleanup_duplicates,
    get_patient_by_user_id, get_all_users, get_medical_staff, delete_user, update_user_role
)
from utils import load_master_metadata, process_cardiac_imaging_data
from report_generator import (
    generate_formatted_clinical_report, create_pdf_report,
    generate_patient_report_both_modalities
)

# Page configuration
st.set_page_config(
    page_title="Cardiac EHR System",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .card {
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin: 10px 0;
    }
    .success-card {
        background-color: #d4edda;
        border-color: #c3e6cb;
    }
    .warning-card {
        background-color: #fff3cd;
        border-color: #ffeaa7;
    }
    .report-box {
        background-color: #f8f9fa;
        color: black;
        border-left: 4px solid #007bff;
        padding: 15px;
        margin: 10px 0;
        white-space: pre-wrap;
        font-family: monospace;
    }
    .patient-view {
        background-color: #e8f4fd;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize all session state variables with safe defaults"""
    # List of all session state variables we need
    session_vars = {
        'db_initialized': False,
        'duplicates_cleaned': False,
        'logged_in': False,
        'user_info': None,
        'current_page': "Login",
        'selected_patient': None,
        'analysis_results': None,
        'recent_patient_registrations': []
    }
    
    # Initialize each variable if it doesn't exist
    for var, default_value in session_vars.items():
        if var not in st.session_state:
            st.session_state[var] = default_value
    
    # Initialize database only once
    if not st.session_state.db_initialized:
        init_db()
        st.session_state.db_initialized = True
        
    # Clean up duplicates only once
    if not st.session_state.duplicates_cleaned:
        cleanup_duplicates()
        st.session_state.duplicates_cleaned = True

def main():
    # Initialize session state first - this must be the first thing we do
    initialize_session_state()
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/heart-health.png", width=80)
        st.title("Cardiac EHR System")
        
        if st.session_state.logged_in:
            user_role = st.session_state.user_info['role']
            st.success(f"Welcome, {st.session_state.user_info['full_name']}!")
            st.write(f"Role: {user_role}")
            
            # Different navigation based on user role
            if user_role == 'Patient':
                pages = ["Patient Dashboard", "My Reports", "My Studies"]
            elif user_role == 'Administrator':
                pages = ["Dashboard", "Patient Database", "Cardiac Analysis", "EHR Reports", "User Management"]
            else:  # Doctors and Technicians
                pages = ["Dashboard", "Patient Database", "Cardiac Analysis", "EHR Reports"]
            
            selected_page = st.selectbox("Navigation", pages, 
                                       index=pages.index(st.session_state.current_page) 
                                       if st.session_state.current_page in pages else 0)
            st.session_state.current_page = selected_page
            
            if st.button("Logout"):
                # Clear all session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        else:
            st.session_state.current_page = "Login"
    
    # Page routing with role-based access control
    if not st.session_state.logged_in:
        login_page()
    else:
        user_role = st.session_state.user_info['role']
        
        if user_role == 'Patient':
            # Patient-specific pages
            if st.session_state.current_page == "Patient Dashboard":
                patient_dashboard_page()
            elif st.session_state.current_page == "My Reports":
                patient_reports_page()
            elif st.session_state.current_page == "My Studies":
                patient_studies_page()
                
        elif user_role == 'Administrator':
            # Admin has access to everything including User Management
            if st.session_state.current_page == "Dashboard":
                dashboard_page()
            elif st.session_state.current_page == "Patient Database":
                patient_database_page()
            elif st.session_state.current_page == "Cardiac Analysis":
                cardiac_analysis_page()
            elif st.session_state.current_page == "EHR Reports":
                ehr_reports_page()
            elif st.session_state.current_page == "User Management":
                user_management_page()
                
        else:  # Doctors and Technicians
            # Medical staff don't see User Management
            if st.session_state.current_page == "Dashboard":
                dashboard_page()
            elif st.session_state.current_page == "Patient Database":
                patient_database_page()
            elif st.session_state.current_page == "Cardiac Analysis":
                cardiac_analysis_page()
            elif st.session_state.current_page == "EHR Reports":
                ehr_reports_page()
            else:
                # If they somehow navigate to a restricted page, redirect to dashboard
                st.session_state.current_page = "Dashboard"
                st.rerun()

def login_page():
    st.markdown('<h1 class="main-header">Cardiac EHR Analysis System</h1>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Patient Registration"])
    
    with tab1:
        with st.form("login_form"):
            st.subheader("User Login")
            
            # Show recent patient registrations in session state for easy reference
            # Use safe access with get() method
            recent_registrations = st.session_state.get('recent_patient_registrations', [])
            if recent_registrations:
                with st.expander("📋 Your Recent Patient Registrations", expanded=True):
                    for reg in recent_registrations[-3:]:  # Show last 3
                        st.write(f"**Patient ID:** {reg['patient_id']} | **Username:** `{reg['username']}`")
            
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            login_btn = st.form_submit_button("Login")
            
            if login_btn:
                if username and password:
                    with st.spinner("Logging in..."):
                        user_data = login_user(username, password)
                        if user_data:
                            st.session_state.logged_in = True
                            st.session_state.user_info = dict(user_data)
                            
                            # Set patient ID for patient users
                            if user_data['role'] == 'Patient':
                                st.session_state.selected_patient = user_data['patient_id']
                            
                            st.success(f"✅ Login successful! Welcome {user_data['full_name']}")
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password")
                else:
                    st.warning("⚠️ Please enter both username and password")
        
        # Display predefined medical staff credentials for demo
        with st.expander("🔑 Demo Credentials & Access Levels"):
            st.write("**👑 Administrator (Full Access):**")
            st.write("- Username: `admin` | Password: `admin123`")
            st.write("- Username: `director` | Password: `director123`")
            st.write("➡️ Can access: Dashboard, Patient Database, Cardiac Analysis, EHR Reports, **User Management**")
            
            st.write("**👨‍⚕️ Doctor (Clinical Access):**")
            st.write("- Username: `dr_smith` | Password: `smith123`")
            st.write("- Username: `dr_jones` | Password: `jones123`") 
            st.write("➡️ Can access: Dashboard, Patient Database, Cardiac Analysis, EHR Reports")
            
            st.write("**🔧 Technician (Technical Access):**")
            st.write("- Username: `tech_davis` | Password: `davis123`")
            st.write("- Username: `tech_garcia` | Password: `garcia123`")
            st.write("➡️ Can access: Dashboard, Patient Database, Cardiac Analysis, EHR Reports")
            
            st.write("**👤 Patient (Limited Access):**")
            st.write("- Register with any Patient ID from your metadata")
            st.write("➡️ Can access: Patient Dashboard, My Reports, My Studies")
    
    with tab2:
        with st.form("patient_registration_form"):
            st.subheader("👤 Patient Registration")
            st.info("ℹ️ Note: You must have an existing patient record in the system to register.")
            
            # Show available patient IDs for reference
            available_patients = get_all_patients()
            if available_patients:
                patient_ids = [p['patient_id'] for p in available_patients[:10]]  # Show first 10
                st.write(f"**Available Patient IDs (first 10):** {', '.join(patient_ids)}")
            
            patient_id = st.text_input("Patient ID*", placeholder="e.g., Patient_001, Patient_002, etc.")
            full_name = st.text_input("Full Name*", placeholder="Your full name")
            email = st.text_input("Email", placeholder="your.email@example.com")
            password = st.text_input("Password*", type="password", placeholder="Minimum 6 characters")
            confirm_password = st.text_input("Confirm Password*", type="password", placeholder="Re-enter your password")
            register_btn = st.form_submit_button("Register as Patient")
            
            if register_btn:
                if not patient_id:
                    st.error("❌ Please enter your Patient ID")
                elif not full_name:
                    st.error("❌ Please enter your full name")
                elif not password:
                    st.error("❌ Please enter a password")
                elif len(password) < 6:
                    st.error("❌ Password must be at least 6 characters long")
                elif password != confirm_password:
                    st.error("❌ Passwords do not match")
                else:
                    with st.spinner("Creating your account..."):
                        success, message = create_patient_user(patient_id, password, full_name, email)
                        if success:
                            # Initialize recent_patient_registrations if it doesn't exist
                            if 'recent_patient_registrations' not in st.session_state:
                                st.session_state.recent_patient_registrations = []
                            
                            # Store registration info for easy login
                            st.session_state.recent_patient_registrations.append({
                                'patient_id': patient_id,
                                'username': f"patient_{patient_id}",
                                'password': password
                            })
                            
                            st.success("✅ " + message)
                            st.info(f"**Your login credentials:**")
                            st.info(f"**Username:** `patient_{patient_id}`")
                            st.info(f"**Password:** The password you just set")
                            st.info("**➡️ Go to the Login tab to access your account**")
                            st.balloons()
                        else:
                            st.error("❌ " + message)

# Medical Staff Pages
def dashboard_page():
    st.markdown('<h1 class="main-header">Clinical Dashboard</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Refresh Dashboard", use_container_width=True):
            st.rerun()
    
    # Dashboard metrics
    stats = get_dashboard_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Patients", stats['total_patients'])
    with col2:
        st.metric("Total EHR Reports", stats['total_reports'])
    with col3:
        st.metric("Imaging Studies", stats['total_studies'])
    with col4:
        st.metric("Recent Reports (7 days)", stats['recent_reports'])
    
    # Master metadata info
    df = load_master_metadata()
    if not df.empty:
        st.subheader("Master Metadata Overview")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Records", len(df))
        with col2:
            st.metric("Unique Patients", df['Patient_ID'].nunique())
        with col3:
            st.metric("CT Studies", len(df[df['Modality'] == 'CT']))
            st.metric("MRI Studies", len(df[df['Modality'] == 'MRI']))
    
    # Recent EHR reports
    st.subheader("Recent EHR Reports")
    reports = get_all_reports()[:5]
    
    if reports:
        for report in reports:
            with st.container():
                st.markdown(f"""
                <div class="report-box">
                    <h4>EHR Report for Patient {report['patient_id']}</h4>
                    <p><strong>Modality:</strong> {report['modality']} | <strong>Condition:</strong> {report['condition_diagnosed']} | <strong>ICD-10:</strong> {report['icd10_code']}</p>
                    <p><strong>Generated by:</strong> {report['generated_by_name']} on {report['created_at']}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No EHR reports generated yet. Start by analyzing a patient's cardiac images.")
    
    # Quick actions
    st.subheader("Quick Actions")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("View Patient Database", use_container_width=True):
            st.session_state.current_page = "Patient Database"
            st.rerun()
    with col2:
        if st.button("Start Cardiac Analysis", use_container_width=True):
            st.session_state.current_page = "Cardiac Analysis"
            st.rerun()
    with col3:
        if st.button("View EHR Reports", use_container_width=True):
            st.session_state.current_page = "EHR Reports"
            st.rerun()

def patient_database_page():
    st.markdown('<h1 class="main-header">Patient Database</h1>', unsafe_allow_html=True)
    
    st.subheader("Patients from Master Metadata")
    patients = get_all_patients()
    
    if patients:
        for patient in patients:
            patient_dict = dict(patient)
            with st.expander(f"Patient {patient_dict['patient_id']} - Age: {patient_dict['age']} - Gender: {patient_dict['gender']}"):
                
                studies = get_patient_studies(patient_dict['patient_id'])
                st.write("**Imaging Studies:**")
                for study in studies:
                    study_dict = dict(study)
                    st.write(f"- **{study_dict['modality']}**: {study_dict['study_date']} (Slices: {study_dict['num_slices']}, Ward: {study_dict['ward_id']})")
                    st.write(f"  Folder: {study_dict['folder_path']}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"Analyze This Patient", key=f"analyze_{patient_dict['patient_id']}"):
                        st.session_state.selected_patient = patient_dict['patient_id']
                        st.session_state.current_page = "Cardiac Analysis"
                        st.rerun()
                with col2:
                    reports = get_patient_reports(patient_dict['patient_id'])
                    if reports:
                        st.write(f"**Existing EHR Reports:** {len(reports)}")
                    else:
                        st.write("**Existing EHR Reports:** None")
                with col3:
                    reports = get_patient_reports(patient_dict['patient_id'])
                    if reports:
                        if st.button(f"Delete All Reports", key=f"delete_all_{patient_dict['patient_id']}"):
                            with st.spinner("Deleting reports..."):
                                deleted_count = delete_all_patient_reports(patient_dict['patient_id'])
                                if deleted_count > 0:
                                    st.success(f"Deleted {deleted_count} reports for patient {patient_dict['patient_id']}")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete reports")
    else:
        st.info("No patients found in the database.")

def cardiac_analysis_page():
    st.markdown('<h1 class="main-header">Cardiac Image Analysis</h1>', unsafe_allow_html=True)
    
    patients = get_all_patients()
    if not patients:
        st.error("No patients found in the database.")
        return
    
    patient_ids = [patient['patient_id'] for patient in patients]
    
    if st.session_state.selected_patient and st.session_state.selected_patient in patient_ids:
        default_index = patient_ids.index(st.session_state.selected_patient)
    else:
        default_index = 0
    
    selected_patient = st.selectbox("Select Patient", patient_ids, index=default_index)
    
    if selected_patient:
        patient_info = get_patient_by_id(selected_patient)
        patient_studies = get_patient_studies(selected_patient)
        
        if patient_info:
            patient_dict = dict(patient_info)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.subheader("Patient Information")
                st.write(f"**Patient ID:** {patient_dict['patient_id']}")
                st.write(f"**Age:** {patient_dict['age']}")
                st.write(f"**Gender:** {patient_dict['gender']}")
            with col2:
                st.subheader("Available Studies")
                if patient_studies:
                    for study in patient_studies:
                        study_dict = dict(study)
                        st.write(f"- **{study_dict['modality']}** ({study_dict['num_slices']} slices)")
                else:
                    st.write("No imaging studies available")
            with col3:
                st.subheader("Report Management")
                existing_reports = get_patient_reports(selected_patient)
                if existing_reports:
                    st.write(f"**Existing Reports:** {len(existing_reports)}")
                    if st.button("🗑️ Delete All Reports for This Patient", key="delete_all"):
                        with st.spinner("Deleting reports..."):
                            deleted_count = delete_all_patient_reports(selected_patient)
                            if deleted_count > 0:
                                st.success(f"Deleted {deleted_count} reports for patient {selected_patient}")
                                st.rerun()
                            else:
                                st.error("Failed to delete reports")
                else:
                    st.write("**Existing Reports:** None")
        
        # Analysis section
        st.subheader("Cardiac Analysis")
        
        if st.button("Start Cardiac Analysis", type="primary"):
            with st.spinner("Initializing cardiac analysis system..."):
                results = process_cardiac_imaging_data(patient_studies, selected_patient)
            
            if results:
                st.session_state.analysis_results = results
                
                for modality, data in results.items():
                    if 'report' in data:
                        report = data['report']
                        st.subheader(f"{modality} Analysis Results")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Condition Diagnosed", report['condition_diagnosed'].replace('_', ' ').title())
                            st.metric("ICD-10 Code", report['icd10_code'])
                        with col2:
                            st.metric("Cardiac Area", f"{report['image_characteristics']['cardiac_area']:.3f}")
                            st.metric("Symmetry Score", f"{report['image_characteristics']['symmetry']:.3f}")
                        st.subheader("Key Findings")
                        for finding in report['findings']:
                            st.write(f"• {finding}")
                        st.subheader("Recommendations")
                        for recommendation in report['recommendations']:
                            st.write(f"• {recommendation}")
                
                st.session_state.analysis_results = results
                st.session_state.selected_patient = selected_patient
                st.session_state.patient_info = patient_dict
                st.success("Cardiac analysis completed! You can now generate the EHR report.")
        
        # Report generation section
        if st.session_state.get('analysis_results') and st.session_state.get('selected_patient') == selected_patient:
            st.subheader("EHR Report Generation")
            
            clinical_report = generate_patient_report_both_modalities(selected_patient, st.session_state.analysis_results)
            formatted_report = generate_formatted_clinical_report(selected_patient, st.session_state.analysis_results, patient_dict)
            
            st.subheader("Formatted Clinical EHR Report")
            st.text_area("Report Content", formatted_report, height=400, key="report_display")
            
            pdf_report = create_pdf_report(formatted_report, selected_patient)
            
            if st.button("💾 Save EHR Report to Database", type="primary", key="save_report_btn"):
                try:
                    for modality, data in st.session_state.analysis_results.items():
                        if 'report' in data:
                            report_data = data['report']
                            
                            image_features_serializable = {}
                            for key, value in report_data['image_characteristics'].items():
                                if hasattr(value, 'item'):
                                    image_features_serializable[key] = value.item()
                                else:
                                    image_features_serializable[key] = value
                            
                            findings_serializable = [str(f) for f in report_data['findings']]
                            recommendations_serializable = [str(r) for r in report_data['recommendations']]
                            
                            save_report_to_db(
                                selected_patient, 
                                modality,
                                report_data['condition_diagnosed'],
                                report_data['icd10_code'],
                                str(image_features_serializable),
                                str(findings_serializable),
                                str(recommendations_serializable),
                                clinical_report,
                                formatted_report,
                                st.session_state.user_info['id']
                            )
                    
                    st.success(f"✅ EHR Report for patient {selected_patient} saved successfully to database!")
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error saving report to database: {str(e)}")
            
            st.subheader("Download Options")
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📄 Download Text Report",
                    data=formatted_report,
                    file_name=f"ehr_report_{selected_patient}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
            with col2:
                st.download_button(
                    label="📊 Download PDF Report",
                    data=pdf_report.getvalue(),
                    file_name=f"ehr_report_{selected_patient}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )
        elif not st.session_state.get('analysis_results'):
            st.info("ℹ️ Please run the cardiac analysis first to generate reports.")

def ehr_reports_page():
    st.markdown('<h1 class="main-header">EHR Reports Database</h1>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["All EHR Reports", "Search Reports"])
    
    with tab1:
        st.subheader("Generated EHR Reports")
        reports = get_all_reports()
        
        if reports:
            st.metric("Total Reports in Database", len(reports))
            
            for report in reports:
                report_dict = dict(report)
                with st.expander(f"📋 EHR Report for Patient {report_dict['patient_id']} - {report_dict['modality']} - {report_dict['created_at']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Patient ID:** {report_dict['patient_id']}")
                        st.write(f"**Age:** {report_dict.get('age', 'N/A')}")
                        st.write(f"**Gender:** {report_dict.get('gender', 'N/A')}")
                        st.write(f"**Modality:** {report_dict['modality']}")
                    with col2:
                        st.write(f"**Condition:** {report_dict['condition_diagnosed']}")
                        st.write(f"**ICD-10 Code:** {report_dict['icd10_code']}")
                        st.write(f"**Generated by:** {report_dict['generated_by_name']}")
                        st.write(f"**Date:** {report_dict['created_at']}")
                    
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col2:
                        if st.button(f"🗑️ Delete This Report", key=f"delete_{report_dict['id']}"):
                            if delete_report(report_dict['id']):
                                st.success(f"Report deleted successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to delete report")
                    with col3:
                        if st.button(f"🔄 Refresh", key=f"refresh_{report_dict['id']}"):
                            st.rerun()
                    
                    st.subheader("Clinical Report Content")
                    if report_dict.get('formatted_report'):
                        st.text_area("Report Content", report_dict['formatted_report'], height=300, key=f"formatted_{report_dict['id']}")
                        pdf_report = create_pdf_report(report_dict['formatted_report'], report_dict['patient_id'])
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.download_button(
                                label="📄 Download Text Report",
                                data=report_dict['formatted_report'],
                                file_name=f"ehr_report_{report_dict['patient_id']}_{report_dict['created_at'].split()[0].replace('-', '')}.txt",
                                mime="text/plain",
                                key=f"text_{report_dict['id']}"
                            )
                        with col2:
                            st.download_button(
                                label="📊 Download PDF Report",
                                data=pdf_report.getvalue(),
                                file_name=f"ehr_report_{report_dict['patient_id']}_{report_dict['created_at'].split()[0].replace('-', '')}.pdf",
                                mime="application/pdf",
                                key=f"pdf_{report_dict['id']}"
                            )
                    else:
                        st.info("No formatted report content available.")
        else:
            st.info("No EHR reports found in the database. Generate some reports first.")
    
    with tab2:
        st.subheader("Search EHR Reports")
        search_term = st.text_input("Enter Patient ID or Condition")
        
        if search_term:
            reports = get_all_reports()
            filtered_reports = [
                r for r in reports 
                if search_term.lower() in r['patient_id'].lower() or 
                   (r['condition_diagnosed'] and search_term.lower() in r['condition_diagnosed'].lower())
            ]
            
            if filtered_reports:
                st.write(f"**Found {len(filtered_reports)} reports matching '{search_term}'**")
                for report in filtered_reports:
                    report_dict = dict(report)
                    with st.expander(f"Patient {report_dict['patient_id']} - {report_dict['condition_diagnosed']}"):
                        st.write(f"**Modality:** {report_dict['modality']}")
                        st.write(f"**Date:** {report_dict['created_at']}")
                        if st.button(f"Delete This Report", key=f"search_delete_{report_dict['id']}"):
                            if delete_report(report_dict['id']):
                                st.success(f"Report deleted successfully!")
                                st.rerun()
                        if report_dict.get('formatted_report'):
                            st.text_area("Report", report_dict['formatted_report'], height=200, key=f"search_{report_dict['id']}")
            else:
                st.info("No reports found matching your search criteria.")

def user_management_page():
    st.markdown('<h1 class="main-header">User Management</h1>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Add Medical Staff", "View Users"])
    
    with tab1:
        st.subheader("Add New Medical Staff")
        with st.form("add_staff_form"):
            col1, col2 = st.columns(2)
            with col1:
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
            with col2:
                role = st.selectbox("Role", ["Doctor", "Technician", "Administrator"])
                full_name = st.text_input("Full Name")
                email = st.text_input("Email")
            
            add_btn = st.form_submit_button("Add Medical Staff")
            
            if add_btn:
                if not all([username, password, full_name]):
                    st.error("Please fill all required fields")
                elif password != confirm_password:
                    st.error("Passwords do not match")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    success = create_medical_staff(username, password, role, full_name, email)
                    if success:
                        st.success(f"Medical staff account created successfully for {full_name}")
                    else:
                        st.error("Username already exists")
    
    with tab2:
        st.subheader("Existing Medical Staff")
        # This would require additional database functions to list users
        st.info("User listing functionality would be implemented here")

# Patient-Specific Pages
def patient_dashboard_page():
    st.markdown('<h1 class="main-header">Patient Portal</h1>', unsafe_allow_html=True)
    
    patient_id = st.session_state.user_info['patient_id']
    patient_info = get_patient_by_user_id(st.session_state.user_info['id'])
    
    if patient_info:
        patient_dict = dict(patient_info)
        
        st.markdown(f"""
        <div class="patient-view">
            <h3>Welcome, {st.session_state.user_info['full_name']}</h3>
            <p><strong>Patient ID:</strong> {patient_dict['patient_id']}</p>
            <p><strong>Age:</strong> {patient_dict['age']}</p>
            <p><strong>Gender:</strong> {patient_dict['gender']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick stats
        col1, col2, col3 = st.columns(3)
        with col1:
            studies = get_patient_studies(patient_id)
            st.metric("Imaging Studies", len(studies))
        with col2:
            reports = get_patient_reports(patient_id)
            st.metric("Medical Reports", len(reports))
        with col3:
            st.metric("Last Updated", datetime.now().strftime("%Y-%m-%d"))
        
        # Recent reports preview
        st.subheader("Recent Medical Reports")
        if reports:
            for report in reports[:3]:
                report_dict = dict(report)
                with st.container():
                    st.markdown(f"""
                    <div class="report-box">
                        <h4>{report_dict['modality']} Report - {report_dict['created_at'].split()[0]}</h4>
                        <p><strong>Condition:</strong> {report_dict['condition_diagnosed'].replace('_', ' ').title()}</p>
                        <p><strong>Generated by:</strong> {report_dict['generated_by_name']}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No medical reports available yet.")
    else:
        st.error("Patient information not found")

def patient_reports_page():
    st.markdown('<h1 class="main-header">My Medical Reports</h1>', unsafe_allow_html=True)
    
    patient_id = st.session_state.user_info['patient_id']
    reports = get_patient_reports(patient_id)
    
    if reports:
        for report in reports:
            report_dict = dict(report)
            with st.expander(f"📋 {report_dict['modality']} Report - {report_dict['created_at'].split()[0]}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Modality:** {report_dict['modality']}")
                    st.write(f"**Condition:** {report_dict['condition_diagnosed'].replace('_', ' ').title()}")
                    st.write(f"**ICD-10 Code:** {report_dict['icd10_code']}")
                with col2:
                    st.write(f"**Generated by:** {report_dict['generated_by_name']}")
                    st.write(f"**Date:** {report_dict['created_at']}")
                
                if report_dict.get('formatted_report'):
                    st.subheader("Report Content")
                    st.text_area("Report", report_dict['formatted_report'], height=300, key=f"patient_report_{report_dict['id']}")
                    
                    # Download options for patient
                    pdf_report = create_pdf_report(report_dict['formatted_report'], patient_id)
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="📄 Download Text Report",
                            data=report_dict['formatted_report'],
                            file_name=f"my_report_{patient_id}_{report_dict['created_at'].split()[0].replace('-', '')}.txt",
                            mime="text/plain",
                            key=f"patient_text_{report_dict['id']}"
                        )
                    with col2:
                        st.download_button(
                            label="📊 Download PDF Report",
                            data=pdf_report.getvalue(),
                            file_name=f"my_report_{patient_id}_{report_dict['created_at'].split()[0].replace('-', '')}.pdf",
                            mime="application/pdf",
                            key=f"patient_pdf_{report_dict['id']}"
                        )
    else:
        st.info("No medical reports available yet.")

def patient_studies_page():
    st.markdown('<h1 class="main-header">My Imaging Studies</h1>', unsafe_allow_html=True)
    
    patient_id = st.session_state.user_info['patient_id']
    studies = get_patient_studies(patient_id)
    
    if studies:
        for study in studies:
            study_dict = dict(study)
            with st.expander(f"🔬 {study_dict['modality']} Study - {study_dict['study_date']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Modality:** {study_dict['modality']}")
                    st.write(f"**Number of Slices:** {study_dict['num_slices']}")
                    st.write(f"**Study Date:** {study_dict['study_date']}")
                with col2:
                    st.write(f"**Ward ID:** {study_dict['ward_id']}")
                    st.write(f"**Folder Path:** {study_dict['folder_path']}")
    else:
        st.info("No imaging studies found in your records.")
def user_management_page():
    """User Management - Admin Only"""
    st.markdown('<h1 class="main-header">User Management</h1>', unsafe_allow_html=True)
    
    # Double-check admin access
    if st.session_state.get('user_info', {}).get('role') != 'Administrator':
        st.error("⛔ Access Denied: User Management is for Administrators only")
        st.info("Please contact your system administrator for access")
        return
    
    tab1, tab2, tab3 = st.tabs(["View All Users", "Add Medical Staff", "Manage Users"])
    
    with tab1:
        st.subheader("👥 All System Users")
        
        users = get_all_users()
        if not users:
            st.info("No users found in the system")
            return
        
        # Display users in a nice format
        for user in users:
            user_dict = dict(user)
            
            with st.expander(f"👤 {user_dict['full_name']} ({user_dict['username']})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Role:** {user_dict['role']}")
                    st.write(f"**Email:** {user_dict['email'] or 'Not provided'}")
                
                with col2:
                    st.write(f"**User ID:** {user_dict['id']}")
                    st.write(f"**Patient ID:** {user_dict['patient_id'] or 'N/A'}")
                
                with col3:
                    st.write(f"**Created:** {user_dict['created_at'].split()[0]}")
                    
                    # Show special badge for main admin
                    if user_dict['username'] == 'admin':
                        st.success("🔐 Main Administrator")
    
    with tab2:
        st.subheader("➕ Add New Medical Staff")
        
        with st.form("add_staff_form"):
            col1, col2 = st.columns(2)
            with col1:
                username = st.text_input("Username*", help="Unique username for login")
                password = st.text_input("Password*", type="password", help="Minimum 6 characters")
                confirm_password = st.text_input("Confirm Password*", type="password")
            with col2:
                role = st.selectbox("Role*", ["Doctor", "Technician", "Administrator"])
                full_name = st.text_input("Full Name*")
                email = st.text_input("Email")
            
            add_btn = st.form_submit_button("Add Medical Staff")
            
            if add_btn:
                if not all([username, password, full_name, role]):
                    st.error("❌ Please fill all required fields (*)")
                elif password != confirm_password:
                    st.error("❌ Passwords do not match")
                elif len(password) < 6:
                    st.error("❌ Password must be at least 6 characters")
                else:
                    success = create_medical_staff(username, password, role, full_name, email)
                    if success:
                        st.success(f"✅ Medical staff account created successfully for {full_name}")
                        st.rerun()
                    else:
                        st.error("❌ Username already exists")
    
    with tab3:
        st.subheader("⚙️ Manage Users")
        st.warning("⚠️ Use with caution: These actions cannot be undone")
        
        users = get_all_users()
        if not users:
            st.info("No users to manage")
            return
        
        # Create a list of users excluding the current admin for safety
        manageable_users = [u for u in users if u['username'] != 'admin']
        
        if not manageable_users:
            st.info("No manageable users found")
            return
        
        for user in manageable_users:
            user_dict = dict(user)
            
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                
                with col1:
                    st.write(f"**{user_dict['full_name']}**")
                    st.write(f"Username: `{user_dict['username']}`")
                    st.write(f"Role: {user_dict['role']}")
                
                with col2:
                    st.write(f"Email: {user_dict['email'] or 'N/A'}")
                    st.write(f"Patient ID: {user_dict['patient_id'] or 'N/A'}")
                
                with col3:
                    # Role change for non-admin users
                    if user_dict['role'] != 'Patient':
                        new_role = st.selectbox(
                            "Change Role",
                            ["Doctor", "Technician", "Administrator"],
                            index=["Doctor", "Technician", "Administrator"].index(user_dict['role']),
                            key=f"role_{user_dict['id']}"
                        )
                        if new_role != user_dict['role']:
                            if st.button("Update Role", key=f"update_{user_dict['id']}"):
                                success, message = update_user_role(user_dict['id'], new_role)
                                if success:
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)
                    else:
                        st.write("Patient Account")
                
                with col4:
                    # Delete user button
                    if st.button("🗑️ Delete", key=f"delete_{user_dict['id']}", type="secondary"):
                        # Confirm deletion
                        if st.checkbox(f"Confirm deletion of {user_dict['username']}", key=f"confirm_{user_dict['id']}"):
                            success, message = delete_user(user_dict['id'])
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                
                st.divider()


if __name__ == "__main__":
    main()