import streamlit as st 
import pandas as pd
import base64, random
import time,datetime
import pymysql
import os
import re
import sys
import os
import socket
import platform
import geocoder
import secrets
import io,random
import plotly.express as px 
import plotly.graph_objects as go
from utils import verify_company_name
from PyPDF2 import PdfReader
from utils import extract_text_from_pdf, extract_text_from_certificate, verify_name_in_text
from geopy.geocoders import Nominatim
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
from streamlit_tags import st_tags
from PIL import Image
from Courses import ds_course,web_course,android_course,ios_course,uiux_course,resume_videos,interview_videos
import nltk
nltk.download('stopwords')
print(sys.path)
def get_csv_download_link(df,filename,text):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    converter.close()
    fake_file_handle.close()
    return text

def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def course_recommender(course_list):
    st.subheader("**Courses & Certificates Recommendations 👨‍🎓**")
    c = 0
    rec_course = []

    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 5)
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
        if c == no_of_reco:
            break
    return rec_course


connection = pymysql.connect(host='localhost',user='root',password='root',db='cv')
cursor = connection.cursor()


def insert_data(sec_token,ip_add,host_name,dev_user,os_name_ver,latlong,city,state,country,act_name,act_mail,act_mob,name,email,res_score,timestamp,no_of_pages,reco_field,cand_level,skills,recommended_skills,courses,pdf_name):
    DB_table_name = 'user_data'
    insert_sql = "insert into " + DB_table_name + """
    values (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    rec_values = (str(sec_token),str(ip_add),host_name,dev_user,os_name_ver,str(latlong),city,state,country,act_name,act_mail,act_mob,name,email,str(res_score),timestamp,str(no_of_pages),reco_field,cand_level,skills,recommended_skills,courses,pdf_name)
    cursor.execute(insert_sql, rec_values)
    connection.commit()

def insertf_data(feed_name,feed_email,feed_score,comments,Timestamp):
    DBf_table_name = 'user_feedback'
    insertfeed_sql = "insert into " + DBf_table_name + """
    values (0,%s,%s,%s,%s,%s)"""
    rec_values = (feed_name, feed_email, feed_score, comments, Timestamp)
    cursor.execute(insertfeed_sql, rec_values)
    connection.commit()

st.set_page_config(
   page_title="An Efficient AI-Based Resume Analyser",
   page_icon='./Logo/ai.jpeg',
)


def run():
    
    img = Image.open('./Logo/resume.png')
    st.image(img)
    st.sidebar.markdown("# Choose Something...")
    activities = ["User", "Feedback", "About", "Admin"]
    choice = st.sidebar.selectbox("Choose among the given options:", activities)
    link = '<b>Built by <a href="https://www.linkedin.com/in/boobalan-e-023452253?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app" style="text-decoration: none; color: #FF0000;">E Boobalan</a></b>' 
    st.sidebar.markdown(link, unsafe_allow_html=True)
    st.sidebar.markdown('''
        <!-- site visitors -->

        <div id="sfcj6l979t71cbmcaud8gzy42kjn1qf98juy" hidden></div>
        <noscript>
            <a href="https://www.freecounterstat.com" title="hit counter">
                <img src="https://counter6.optistats.ovh/private/freecounterstat.php?c=j6l979t71cbmcaud8gzy42kjn1qf98ju" border="0" title="hit counter" alt="hit counter"> -->
            </a>
        </noscript>
    
        <p>Visitors <img src="https://counter6.optistats.ovh/private/freecounterstat.php?c=j6l979t71cbmcaud8gzy42kjn1qf98ju" title="Free Counter" Alt="web counter" width="60px"  border="0" /></p>
    
    ''', unsafe_allow_html=True)

    db_sql = """CREATE DATABASE IF NOT EXISTS CV;"""
    cursor.execute(db_sql)

    DB_table_name = 'user_data'
    table_sql = "CREATE TABLE IF NOT EXISTS " + DB_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                    sec_token varchar(20) NOT NULL,
                    ip_add varchar(50) NULL,
                    host_name varchar(50) NULL,
                    dev_user varchar(50) NULL,
                    os_name_ver varchar(50) NULL,
                    latlong varchar(50) NULL,
                    city varchar(50) NULL,
                    state varchar(50) NULL,
                    country varchar(50) NULL,
                    act_name varchar(50) NOT NULL,
                    act_mail varchar(50) NOT NULL,
                    act_mob varchar(20) NOT NULL,
                    Name varchar(500) NOT NULL,
                    Email_ID VARCHAR(500) NOT NULL,
                    resume_score VARCHAR(8) NOT NULL,
                    Timestamp VARCHAR(50) NOT NULL,
                    Page_no VARCHAR(5) NOT NULL,
                    Predicted_Field BLOB NOT NULL,
                    User_level BLOB NOT NULL,
                    Actual_skills BLOB NOT NULL,
                    Recommended_skills BLOB NOT NULL,
                    Recommended_courses BLOB NOT NULL,
                    pdf_name varchar(50) NOT NULL,
                    PRIMARY KEY (ID)
                    );
                """
    cursor.execute(table_sql)


    DBf_table_name = 'user_feedback'
    tablef_sql = "CREATE TABLE IF NOT EXISTS " + DBf_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                        feed_name varchar(50) NOT NULL,
                        feed_email VARCHAR(50) NOT NULL,
                        feed_score VARCHAR(5) NOT NULL,
                        comments VARCHAR(100) NULL,
                        Timestamp VARCHAR(50) NOT NULL,
                        PRIMARY KEY (ID)
                    );
                """
    cursor.execute(tablef_sql)

    if choice == 'User':
     
        act_name = st.text_input('Name*')
        act_mail = st.text_input('Mail*')
        act_mob  = st.text_input('Mobile Number*')
        sec_token = secrets.token_urlsafe(12)
        host_name = socket.gethostname()
        ip_add = socket.gethostbyname(host_name)
        dev_user = os.getlogin()
        os_name_ver = platform.system() + " " + platform.release()
        g = geocoder.ip('me')
        latlong = g.latlng
        geolocator = Nominatim(user_agent="http")
        location = geolocator.reverse(latlong, language='en',timeout=10)
        address = location.raw['address']
        cityy = address.get('city', '')
        statee = address.get('state', '')
        countryy = address.get('country', '')  
        city = cityy
        state = statee
        country = countryy


        st.markdown('''<h5 style='text-align: left; color: #021659;'> Upload Your Resume, And Get Smart Recommendations</h5>''',unsafe_allow_html=True)
        
        ## file upload in pdf format
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        if pdf_file is not None:
            with st.spinner('Please Wait processing Your Resume...'):
                time.sleep(4)
        
            ### saving the uploaded resume to folder
            save_image_path = './Uploaded_Resumes/'+pdf_file.name
            pdf_name = pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)

            ### parsing and extracting whole resume 
            resume_data = ResumeParser(save_image_path).get_extracted_data()
            if resume_data:
                
                ## Get the whole resume data into resume_text
                resume_text = pdf_reader(save_image_path)

        

                st.header("**Resume Analysis**")
                st.success("Hello "+ resume_data['name'])
                st.subheader("**Your Basic info**")
                try:
                    st.text('Name: '+resume_data['name'])
                    st.text('Email: ' + resume_data['email'])
                    st.text('Contact: ' + resume_data['mobile_number'])
                    st.text('Degree: '+str(resume_data['degree']))                    
                    st.text('Resume pages: '+str(resume_data['no_of_pages']))

                except:
                    pass

                cand_level = ''
                if resume_data['no_of_pages'] < 1:                
                    cand_level = "NA"
                    st.markdown( '''<h4 style='text-align: left; color: #d73b5c;'>You are at Fresher level!</h4>''',unsafe_allow_html=True)
                
                elif 'INTERNSHIP' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                elif 'INTERNSHIPS' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                elif 'Internship' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                elif 'Internships' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                
                elif 'EXPERIENCE' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                elif 'WORK EXPERIENCE' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                elif 'Experience' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                elif 'Work Experience' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                else:
                    cand_level = "Fresher"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at Fresher level!!''',unsafe_allow_html=True)


                st.subheader("**Skills Recommendation 💡**")
                
                keywords = st_tags(label='### Your Current Skills',
                text='See our skills recommendation below',value=resume_data['skills'],key = '1  ')

                ds_keyword = ['tensorflow','keras','pytorch','machine learning','deep Learning','flask','streamlit']
                web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress','javascript', 'angular js', 'C#', 'Asp.net', 'flask']
                android_keyword = ['android','android development','flutter','kotlin','xml','kivy']
                ios_keyword = ['ios','ios development','swift','cocoa','cocoa touch','xcode']
                uiux_keyword = ['ux','adobe xd','figma','zeplin','balsamiq','ui','prototyping','wireframes','storyframes','adobe photoshop','photoshop','editing','adobe illustrator','illustrator','adobe after effects','after effects','adobe premier pro','premier pro','adobe indesign','indesign','wireframe','solid','grasp','user research','user experience']
                n_any = ['english','communication','writing', 'microsoft office', 'leadership','customer management', 'social media']                
                recommended_skills = []
                reco_field = ''
                rec_course = ''

                for i in resume_data['skills']:
                    if i.lower() in ds_keyword:
                        print(i.lower())
                        reco_field = 'Data Science'
                        st.success("** Our analysis says you are looking for Data Science Jobs.**")
                        recommended_skills = ['Data Visualization','Predictive Analysis','Statistical Modeling','Data Mining','Clustering & Classification','Data Analytics','Quantitative Analysis','Web Scraping','ML Algorithms','Keras','Pytorch','Probability','Scikit-learn','Tensorflow',"Flask",'Streamlit']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '2')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job</h5>''',unsafe_allow_html=True)
                        rec_course = course_recommender(ds_course)
                        break    

                    elif i.lower() in web_keyword:
                        print(i.lower())
                        reco_field = 'Web Development'
                        st.success("** Our analysis says you are looking for Web Development Jobs **")
                        recommended_skills = ['React','Django','Node JS','React JS','php','laravel','Magento','wordpress','Javascript','Angular JS','c#','Flask','SDK']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '3')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)   
                        rec_course = course_recommender(web_course)
                        break

                    elif i.lower() in android_keyword:
                        print(i.lower())
                        reco_field = 'Android Development'
                        st.success("** Our analysis says you are looking for Android App Development Jobs **")
                        recommended_skills = ['Android','Android development','Flutter','Kotlin','XML','Java','Kivy','GIT','SDK','SQLite']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '4')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                        rec_course = course_recommender(android_course)
                        break

                    elif i.lower() in ios_keyword:
                        print(i.lower())
                        reco_field = 'IOS Development'
                        st.success("** Our analysis says you are looking for IOS App Development Jobs **")
                        recommended_skills = ['IOS','IOS Development','Swift','Cocoa','Cocoa Touch','Xcode','Objective-C','SQLite','Plist','StoreKit',"UI-Kit",'AV Foundation','Auto-Layout']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '5')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                        rec_course = course_recommender(ios_course)
                        break

                   
                    elif i.lower() in uiux_keyword:
                        print(i.lower())
                        reco_field = 'UI-UX Development'
                        st.success("** Our analysis says you are looking for UI-UX Development Jobs **")
                        recommended_skills = ['UI','User Experience','Adobe XD','Figma','Zeplin','Balsamiq','Prototyping','Wireframes','Storyframes','Adobe Photoshop','Editing','Illustrator','After Effects','Premier Pro','Indesign','Wireframe','Solid','Grasp','User Research']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '6')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                        rec_course = course_recommender(uiux_course)
                        break

                    elif i.lower() in n_any:
                        print(i.lower())
                        reco_field = 'NA'
                        st.warning("** Currently our tool only predicts and recommends for Data Science, Web, Android, IOS and UI/UX Development**")
                        recommended_skills = ['No Recommendations']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Currently No Recommendations',value=recommended_skills,key = '6')
                        st.markdown('''<h5 style='text-align: left; color: #092851;'>Maybe Available in Future Updates</h5>''',unsafe_allow_html=True)
                        rec_course = "Sorry! Not Available for this Field"
                        break

                st.subheader("**Resume Tips & Ideas **")
                resume_score = 0
            


                college_scores = {
                                    "Indian Institute of Science": 12,
                                    "Indian Institute of Technology": 12,
                                    "National Institute of Technology":11,
                                    "Anna University":10,
                                    "Government College of Technology":10,
                                    "Alagappa Chettiar College of Engineering":10,
                                    "Government college of engineering": 10,

                                    "Jadavpur University":9,
                                    "Amity University":9,
                                    "Jamia Millia Islamia":9, 
                                    "Siksha O Anusandhan":9,
                                    "Thapar Institute of Engineering and Technology":9,
                                    "Birla Institute of Technology & Science – Pilani":9,
                                    "Visvesvaraya National Institute of Technology":9,
                                    "Delhi Technological University":9,
                                    "Aligarh Muslim University":9,
                                    "Kalasalingam Academy of Research and Education":9,
                                    "Kalinga Institute of Industrial Technology":9,
                                    "Koneru Lakshmaiah Education Foundation University":9,
                                    "Chandigarh University, Mohali":9,
                                    "Malaviya National Institute of Technology":9,
                                    "Motilal Nehru National Institute of Technology":9,
                                    "Visvesvaraya Technological University":9,
                                    "Lovely Professional University":9,
                                    "Dr. B R Ambedkar National Institute of Technology":9, 
                                    "Birla Institute of Technology":9, 
                                    "Manipal Institute of Technology":9,
                                    "Sardar Vallabhbhai National Institute of Technology":9, 
                                    "Banasthali Vidyapith, Banasthali Rajasthan":9,
                                    "University of Petroleum and Energy Studies":9, 
                                    "Graphic Era University, Dehradun Uttarakhand":9,
                                    "M. S. Ramaiah Institute of Technology":9, 
                                    "Indraprastha Institute of Information Technology":9, 
                                    "Maulana Azad National Institute of Technology":9, 
                                    "Defence Institute of Advanced Technology":9, 
                                    "College of Engineering":9,
                                    "Guru Gobind Singh Indraprastha University":9,
                                    "Manipal University":9,
                                    "Jawaharlal Nehru Technological University":9, 
                                    "AU College of Engineering":9, 
                                    "Atal Bihari Vajpayee Indian Institute of Information Technology and Management":9, 
                                    "Netaji Subhas University of Technology ":9, 
                                    "Pandit Dwarka Prasad Mishra Indian Institute of Information Technology":9, 
                                    "B.M.S. College of Engineering":9, 
                                    "Punjab Engineering College":9,
                                    "R.V. College of Engineering":9,
                                    "SR University":9,
                                    "Panjab University":9,
                                    "Jaypee Institute of Information Technology":9, 
                                    "The Northcap University":9, 
                                    "Siddaganga Institute of Technology":9, 
                                    "C.V. Raman Global University":9, 
                                    "Vignan’s Foundation for Science, Technology and Research":9, 
                                    "PES University, Bengaluru Karnataka":9,
                                                                        
                                    "PSG College of Technology": 8,
                                    "Coimbatore Institute of Technology":8,
                                    "Thiagarajar College of Engineering":8,
                                    "Kumaraguru College of Technology":8,
                                    "Sri Ramakrishna Engineering College":8,
                                    "Karpagam College of Engineering":8,
                                    "Sri Krishna College of Engineering & Technology":8,
                                    "Kongu Engineering College":8,
                                    "Bannari Amman Institute of Technology":8,
                                    "Vel Tech Rangarajan Dr. Sagunthala R&D Institute of Science and Technology":8,
                                    "SSN College of Engineering":8,
                                    "Sri Sivasubramaniya Nadar College of Engineering":8,
                                    "Velammal Engineering College":8,
                                    "Sona College of Technology":8,
                                    "Sri Sai Ram Engineering College":8,
                                    "Vel Tech High Tech Dr. Rangarajan Dr. Sakunthala Engineering College":8,
                                    "St. Joseph's College of Engineering":8,
                                    "R.M.K. Engineering College":8,
                                    "Jeppiaar Engineering College":8,
                                    "Saveetha Engineering College":8,
                                    "Adhiyamaan College of Engineering":8,
                                    "Rajalakshmi Engineering College":8,
                                    "Sri Venkateswara College of Engineering":8,
                                    "Easwari Engineering College":8,
                                    "Velalar College of Engineering and Technology":8,
                                    "IFET College of Engineering":8,
                                    "National Engineering College":8,
                                    "Sri Shakthi Institute of Engineering & Technology":8,
                                    "Hindusthan College Of Engineering And Technology":8,
                                    "Dhanalakshmi Srinivasan Engineering College":8,
                                    "Paavai Engineering College":8,
                                    "Mepco Schlenk Engineering College":8,
                                    "Valliammai Engineering College":8,
                                    "Sethu Institute of Technology":8,
                                    "Sengunthar Engineering College":8,
                                    "St. Mother Theresa Engineering College":8,
                                    "Dr. Mahalingam College of Engineering and Technology":8,
                                    "Arunai Engineering College":8,
                                    "Thangavelu Engineering College (TEC)":8,
                                    "Parisutham Institute of Technology & Science":8,
                                    "Apollo Engineering College":8,
                                    "Arulmigu Meenakshi Amman College of Engineering":8,
                                    "Anjalai Ammal Mahalingam Engineering College":8,
                                    "Vetri Vinayaha College of Engineering and Technology":8,
                                    "St. Anne College of Engineering and Technology":8,
                                    "AVS Engineering College":8,
                                    "A.V.C College of Engineering":8,
                                    "M.Kumarasamy College of Engineering":8,
                                    "Muthayammal Engineering College":8,
                                    "Tagore Institute of Engineering and Technology":8,
                                    "Solamalai College of Engineering":8,
                                    "P.T.R College of Engineering and Technology":8,
                                    "Thiruvalluvar College of Engineering and Technology":8,
                                    "Sri Krishna Institute of Technology":8,
                                    "Arulmurugan College of Engineering":8,
                                    "Dhaanish Ahmed College of Engineering":8,
                                    "Infant Jesus College of Engineering and Technology":8,
                                    "Jayaraj Annapackiam CSI College of Engineering":8,
                                    "Jeppiaar Institute of Technology":8,
                                    "Jerusalem College of Engineering":8,
                                    "K.Ramakrishnan College of Engineering":8,
                                    "Kalasalingam Academy of Research and Education":8,
                                    "Kamban Engineering College":8,
                                    "Lord Jegannath College of Engineering and Technology":8,
                                    "Mahendra Engineering College":8,
                                    "Maharaja Engineering College":8,
                                    "Mangayarkarasi College of Engineering":8,
                                    "Mar Ephraem College of Engineering and Technology":8,
                                    "Mount Zion College of Engineering and Technology":8,
                                    "Nandha Engineering College":8,
                                    "P.B. College of Engineering":8,
                                    "P.S.N.A. College of Engineering and Technology":8,
                                    "Panimalar Engineering College":8,
                                    "Pavendar Bharathidasan College of Engineering and Technology":8,
                                    "R.M.D Engineering College":8,
                                    "Raja College of Engineering and Technology":8,
                                    "Ranganathan Engineering College":8,
                                    "RVS College of Engineering and Technology":8,
                                    "SAMS College of Engineering and Technology":8,
                                    "Sree Sastha Institute of Engineering and Technology":8,
                                    "Sri Krishna College of Technology":8,
                                    "Sri Muthukumaran Institute of Technology":8,
                                    "Sri Ramanujar Engineering College":8,
                                    "Sri Sai Ram Institute of Technology":8,
                                    "Sri Subramanya College of Engineering and Technology":8,
                                    "Sri Venkateswara Institute of Science and Technology":8,
                                    "St. Peter's College of Engineering and Technology":8,
                                    "VSB Engineering College":8,
                                    "PSV College of Engineering and Technology":8,
                                    "Parul Institute of Engineering and Technology":8
                                }

                education_missing = True

                if ',' in resume_text:
                    for resume_part in resume_text.split(","):
                        for college in college_scores.keys():
                            if college.lower() in resume_part.lower():
                                education_missing = False
                                resume_score += college_scores[college]
                                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+]  Awesome! You have added Education Details</h4>''', unsafe_allow_html=True)
                                break  
                        else:
                            continue
                        break

                if education_missing:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-]  Please add Education, Education Qualification Missing Your Not Eligible For Applying Jobs</h4>''', unsafe_allow_html=True)
                    st.error("No education Details found")
                    st.stop()


                if 'objective' or 'Summary' in resume_text.lower():
                    resume_score = resume_score+6
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Objective/Summary</h4>''',unsafe_allow_html=True)  
                elif 'objectives'  in resume_text.lower():
                    resume_score = resume_score+6
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Objective/Summary</h4>''',unsafe_allow_html=True)                         
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add your career objective, it will give your career intension to the Recruiters.</h4>''',unsafe_allow_html=True)
                    
                if 'internship'  in resume_text.lower():
                    resume_score = resume_score + 6
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Internships</h4>''',unsafe_allow_html=True)
                elif 'internships'  in resume_text.lower():
                    resume_score = resume_score + 6
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Internships</h4>''',unsafe_allow_html=True)
                
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Internships. It will help you to stand out from crowd</h4>''',unsafe_allow_html=True)

                if 'skill'  in resume_text.lower():
                    resume_score = resume_score + 7
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Skills</h4>''',unsafe_allow_html=True)
                elif 'skills'  in resume_text.lower():
                    resume_score = resume_score + 7
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Skills</h4>''',unsafe_allow_html=True)
                
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Skills. It will help you a lot</h4>''',unsafe_allow_html=True)

                if 'hobbie' in resume_text.lower():
                    resume_score = resume_score + 4
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Hobbies</h4>''',unsafe_allow_html=True)
                elif 'hobbies' in resume_text.lower():
                    resume_score = resume_score + 4
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Hobbies</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Hobbies. It will show your personality to the Recruiters and give the assurance that you are fit for this role or not.</h4>''',unsafe_allow_html=True)

                if 'interest'in resume_text.lower():
                    resume_score = resume_score + 5
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Interest</h4>''',unsafe_allow_html=True)
                elif 'interests'in resume_text.lower():
                    resume_score = resume_score + 5
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Interest</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Interest. It will show your interest other that job.</h4>''',unsafe_allow_html=True)

                if 'achievement' in resume_text.lower():
                    resume_score = resume_score + 13
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Achievements </h4>''',unsafe_allow_html=True)
                elif 'achievements' in resume_text.lower():
                    resume_score = resume_score + 13
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Achievements </h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Achievements. It will show that you are capable for the required position.</h4>''',unsafe_allow_html=True)

                if 'certification' in resume_text.lower():
                    resume_score = resume_score + 12
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Certifications </h4>''',unsafe_allow_html=True)
                elif 'certifications' in resume_text.lower():
                    resume_score = resume_score + 12
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Certifications </h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Certifications. It will show that you have done some specialization for the required position.</h4>''',unsafe_allow_html=True)

                if 'project' in resume_text.lower():
                    resume_score = resume_score + 19
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
                
                elif 'projects' in resume_text.lower():
                    resume_score = resume_score + 19
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Projects. It will show that you have done work related the required position or not.</h4>''',unsafe_allow_html=True)
                username = st.text_input("Enter your username:")
                if 'experience' in resume_text.lower() or 'experiences' in resume_text.lower():
                    st.markdown('<h5 style="text-align: left; color: #1ed760;">[+] Awesome! You have added your Experience</h5>', unsafe_allow_html=True)
                    st.markdown('<h5 style="text-align: left; color: #021659;">Upload Your Experience Certificate and Get Smart Recommendations</h5>', unsafe_allow_html=True)

                    certificate_file = st.file_uploader("Please Choose your Experience Certificate (PDF)", type=["pdf"])
                    if certificate_file is not None:
                        certificate_text = extract_text_from_certificate(certificate_file)

                        if username.lower() in certificate_text.lower():
                            st.success(f"Username '{username}' found in the certificate!")
                            company_name_pattern = r"Company\s*Name\s*[:-]?\s*([^\n]+)"
                            match = re.search(company_name_pattern, certificate_text, re.IGNORECASE)

                            if match:
                                extracted_company_name = match.group(1).strip()
                                st.write(f"Extracted Company Name: {extracted_company_name}")

                                if verify_company_name(extracted_company_name):
                                    st.success(f"Verified: '{extracted_company_name}' is a recognized company!")
                                    resume_score += 16
                                    st.write(f"Your resume score has been updated: {resume_score} points")
                                else:
                                    st.error(f"Company '{extracted_company_name}' is not recognized.")
                            else:
                                st.warning("Company name not found in the certificate.")
                        else:
                            st.error(f"Username '{username}' not found in the certificate. Please verify.")
                    else:
                        st.warning("Please upload a PDF file for your Experience Certificate.")
                else:
                    st.warning("No experience found in the resume. Please add your experiences.")

    

                st.subheader("**Resume Score 📝**")
                st.markdown(
                    """
                    <style>
                        .stProgress > div > div > div > div {
                            background-color: #d73b5c;
                        }
                    </style>""",
                    unsafe_allow_html=True,
                )

                my_bar = st.progress(0)
                score = 0
                for percent_complete in range(resume_score):
                    score +=1
                    time.sleep(0.1)
                    my_bar.progress(percent_complete + 1)

                st.success('** Your Resume Writing Score: ' + str(score)+'**')
                st.warning("** Note: This score is calculated based on the content that you have in your Resume. **")

                ts = time.time()
                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                timestamp = str(cur_date+'_'+cur_time)

               
                insert_data(str(sec_token), str(ip_add), (host_name), (dev_user), (os_name_ver), (latlong), (city), (state), (country), (act_name), (act_mail), (act_mob), resume_data['name'], resume_data['email'], str(resume_score), timestamp, str(resume_data['no_of_pages']), reco_field, cand_level, str(resume_data['skills']), str(recommended_skills), str(rec_course), pdf_name)

                st.header("**Bonus Video for Resume Writing Tips💡**")
                resume_vid = random.choice(resume_videos)
                st.video(resume_vid)

                st.header("**Bonus Video for Interview Tips💡**")
                interview_vid = random.choice(interview_videos)
                st.video(interview_vid)

              
                st.balloons()

            else:
                st.error('Something went wrong..')                


    elif choice == 'Feedback':   
        
      
        ts = time.time()
        cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        timestamp = str(cur_date+'_'+cur_time)

        with st.form("my_form"):
            st.write("Feedback form")            
            feed_name = st.text_input('Name')
            feed_email = st.text_input('Email')
            feed_score = st.slider('Rate Us From 1 - 5', 1, 5)
            comments = st.text_input('Comments')
            Timestamp = timestamp        
            submitted = st.form_submit_button("Submit")
            if submitted:
            
                insertf_data(feed_name,feed_email,feed_score,comments,Timestamp)    
               
                st.success("Thanks! Your Feedback was recorded.") 
                
                st.balloons()    

        query = 'select * from user_feedback'        
        plotfeed_data = pd.read_sql(query, connection)                        


      
        labels = plotfeed_data.feed_score.unique()
        values = plotfeed_data.feed_score.value_counts()


        st.subheader("**Past User Rating's**")
        fig = px.pie(values=values, names=labels, title="Chart of User Rating Score From 1 - 5", color_discrete_sequence=px.colors.sequential.Aggrnyl)
        st.plotly_chart(fig)


        cursor.execute('select feed_name, comments from user_feedback')
        plfeed_cmt_data = cursor.fetchall()

        st.subheader("**User Comment's**")
        dff = pd.DataFrame(plfeed_cmt_data, columns=['User', 'Comment'])
        st.dataframe(dff, width=1000)

    

    elif choice == 'About':   

        st.subheader("**About The Tool - An Efficient AI-Based Resume Analyzer**")

        st.markdown('''

        <p align='justify'>
            A tool which parses information from a resume using natural language processing and finds the keywords, cluster them onto sectors based on their keywords. And lastly show recommendations, predictions, analytics to the applicant based on keyword matching.
        </p>

        <p align="justify">
            <b>How to use it: -</b> <br/><br/>
            <b>User -</b> <br/>
            In the Side Bar choose yourself as user and fill the required fields and upload your resume in pdf format.<br/>
            Just sit back and relax our tool will do the magic on it's own.<br/><br/>
            <b>Feedback -</b> <br/>
            A place where user can suggest some feedback about the tool.<br/><br/>
            <b>Admin -</b> <br/>
            For login use <b>Admin</b> as username and <b>Admin@123</b> as password.<br/>
            It will load all the required stuffs and perform analysis.
        </p><br/><br/>

        <p align="justify">
            Built with 🤍 by 
            <a href="https://www.linkedin.com/in/boobalan-e-023452253?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app" style="text-decoration: none; color: red;">E Boobalan</a> through 
            <a href="https://gcebargur.ac.in/19/cse-aboutus" style="text-decoration: none; color: grey;">GCEB CSE FINAL YEAR</a>
        </p>

        ''',unsafe_allow_html=True)  


 
    else:
        st.success('Welcome to Admin Side')

      
        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')

        if st.button('Login'):
         
            if ad_user == 'Admin' and ad_password == 'Admin@123':
                
              
                cursor.execute('''SELECT ID, ip_add, resume_score, convert(Predicted_Field using utf8), convert(User_level using utf8), city, state, country from user_data''')
                datanalys = cursor.fetchall()
                plot_data = pd.DataFrame(datanalys, columns=['Idt', 'IP_add', 'resume_score', 'Predicted_Field', 'User_Level', 'City', 'State', 'Country'])
                
                values = plot_data.Idt.count()
                st.success("Welcome Boobalan ! Total %d " % values + " User's Have Used Our Tool : )")                
                
                cursor.execute('''SELECT ID, sec_token, ip_add, act_name, act_mail, act_mob, convert(Predicted_Field using utf8), Timestamp, Name, Email_ID, resume_score, Page_no, pdf_name, convert(User_level using utf8), convert(Actual_skills using utf8), convert(Recommended_skills using utf8), convert(Recommended_courses using utf8), city, state, country, latlong, os_name_ver, host_name, dev_user from user_data''')
                data = cursor.fetchall()                

                st.header("**User's Data**")
                df = pd.DataFrame(data, columns=['ID', 'Token', 'IP Address', 'Name', 'Mail', 'Mobile Number', 'Predicted Field', 'Timestamp',
                                                 'Predicted Name', 'Predicted Mail', 'Resume Score', 'Total Page',  'File Name',   
                                                 'User Level', 'Actual Skills', 'Recommended Skills', 'Recommended Course',
                                                 'City', 'State', 'Country', 'Lat Long', 'Server OS', 'Server Name', 'Server User',])
                
              
                st.dataframe(df)
                
                
                st.markdown(get_csv_download_link(df,'User_Data.csv','Download Report'), unsafe_allow_html=True)

                cursor.execute('''SELECT * from user_feedback''')
                data = cursor.fetchall()

                st.header("**User's Feedback Data**")
                df = pd.DataFrame(data, columns=['ID', 'Name', 'Email', 'Feedback Score', 'Comments', 'Timestamp'])
                st.dataframe(df)

                query = 'select * from user_feedback'
                plotfeed_data = pd.read_sql(query, connection)                        


               
                labels = plotfeed_data.feed_score.unique()
                values = plotfeed_data.feed_score.value_counts()
                
                
                st.subheader("**User Rating's**")
                fig = px.pie(values=values, names=labels, title="Chart of User Rating Score From 1 - 5 🤗", color_discrete_sequence=px.colors.sequential.Aggrnyl)
                st.plotly_chart(fig)

                               
                labels = plot_data.Predicted_Field.unique()
                values = plot_data.Predicted_Field.value_counts()

                
                st.subheader("**Pie-Chart for Predicted Field Recommendation**")
                fig = px.pie(df, values=values, names=labels, title='Predicted Field according to the Skills 👽', color_discrete_sequence=px.colors.sequential.Aggrnyl_r)
                st.plotly_chart(fig)

                                
                labels = plot_data.User_Level.unique()
                values = plot_data.User_Level.value_counts()

                st.subheader("**Pie-Chart for User's Experienced Level**")
                fig = px.pie(df, values=values, names=labels, title="Pie-Chart 📈 for User's 👨‍💻 Experienced Level", color_discrete_sequence=px.colors.sequential.RdBu)
                st.plotly_chart(fig)
                 
                labels = plot_data.resume_score.unique()                
                values = plot_data.resume_score.value_counts()

                st.subheader("**Pie-Chart for Resume Score**")
                fig = px.pie(df, values=values, names=labels, title='From 1 to 100 💯', color_discrete_sequence=px.colors.sequential.Agsunset)
                st.plotly_chart(fig)

                
                labels = plot_data.IP_add.unique()
                values = plot_data.IP_add.value_counts()

              
                st.subheader("**Pie-Chart for Users App Used Count**")
                fig = px.pie(df, values=values, names=labels, title='Usage Based On IP Address 👥', color_discrete_sequence=px.colors.sequential.matter_r)
                st.plotly_chart(fig)

                labels = plot_data.City.unique()
                values = plot_data.City.value_counts()

                st.subheader("**Pie-Chart for City**")
                fig = px.pie(df, values=values, names=labels, title='Usage Based On City 🌆', color_discrete_sequence=px.colors.sequential.Jet)
                st.plotly_chart(fig)
 
                labels = plot_data.State.unique()
                values = plot_data.State.value_counts()

                st.subheader("**Pie-Chart for State**")
                fig = px.pie(df, values=values, names=labels, title='Usage Based on State 🚉', color_discrete_sequence=px.colors.sequential.PuBu_r)
                st.plotly_chart(fig)

                labels = plot_data.Country.unique()
                values = plot_data.Country.value_counts()

                
                st.subheader("**Pie-Chart for Country**")
                fig = px.pie(df, values=values, names=labels, title='Usage Based on Country 🌏', color_discrete_sequence=px.colors.sequential.Purpor_r)
                st.plotly_chart(fig)

       
            else:
                st.error("Wrong ID & Password Provided")

run()
