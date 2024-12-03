import streamlit as st
import base64

from sql_agent import crew as sql_crew
from YT_agent import crew as yt_crew
from pdf_search import crew as pdf_crew
from travel_recommendation import create_vacation_tasks

def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background_image(image_path):
    img = get_img_as_base64(image_path)
    page_bg_img = f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/jpeg;base64,{img}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)

def set_logo(logo_path):
    logo = get_img_as_base64(logo_path)
    st.markdown(f'<img src="data:image/png;base64,{logo}" style="height: 80px; width: auto; margin-left: 20px; margin-top: 10px;">', unsafe_allow_html=True)


def main_page():

    set_background_image("images/BG_Img.png")
    #set_logo("images/hcltech.jpg")
    st.title("Welcome to Crew AI Multi-Tool App")
    st.write("Choose an app to explore:")
    
    st.markdown(
        """
        <style>
        .home-button {
            display: block;
            margin: 0 auto;
            text-align: center;
            width: 80%;  /* Adjust width if needed */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="home-button">', unsafe_allow_html=True)
    if st.button("SQL Query Explorer"):
        st.session_state.page = "SQL"
    if st.button("YouTube Blog Writer"):
        st.session_state.page = "YT"
    if st.button("PDF Query Navigator"):
        st.session_state.page = "PDF"
    if st.button("Vacation Planner"):
        st.session_state.page = "VACATION"
    st.markdown('</div>', unsafe_allow_html=True)

def sql_page():
    set_background_image("images/BG_Img.png") 
    st.title("SQL Query Explorer")
    st.write("This app lets you query a database and receive meaningful insights.")

    custom_query = st.text_input("Enter your custom query:", placeholder="e.g., Who is the main chair on the advisory board?")

    st.subheader("Frequently Asked Questions")
    faq_questions = [
        "What are the Awards won by Karl Berry?",
        "What are the different categories of movies?",
        "Who is the main chair on the advisor board?",
        "Tell me about the film CAROL TEXAS?"
    ]

    selected_faq_query = None
    col1, col2 = st.columns(2)
    for i, faq in enumerate(faq_questions):
        col = col1 if i % 2 == 0 else col2
        if col.button(faq):
            selected_faq_query = faq

    query_to_process = selected_faq_query or custom_query.strip()

    if query_to_process:
        st.write(f"Processing your query: *{query_to_process}*")
        with st.spinner("Running your query..."):
            try:
                inputs = {"query": query_to_process}
                result = sql_crew.kickoff(inputs=inputs)
                output = result.raw
                st.subheader("Query Result")
                st.write(output)

            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Enter a custom query or select a question to proceed.")
    
    if st.button("Back to Home"):
        st.session_state.page = "Main"

def yt_page():
    set_background_image("images/BG_Img.png") 
    st.title("YouTube Blog Writer")
    st.write("This app lets you write Blogs based on the YouTube video content")

    custom_query = st.text_input("Enter your favorite YouTube video:", placeholder="e.g., What is BERT?")

    st.subheader("Frequently Asked Questions")
    faq_questions = [
        "Named Entity Recognition (NER): NLP Tutorial For Beginners - S1 E12",
        "What is BERT? | Deep Learning Tutorial 46 (Tensorflow, Keras & Python)",
        "Machine Learning Tutorial Python - 8 Logistic Regression (Multiclass Classification)",
        "AI Engineer Roadmap | How I'd Learn AI in 2024"
    ]

    selected_faq_query = None
    col1, col2 = st.columns(2)
    for i, faq in enumerate(faq_questions):
        col = col1 if i % 2 == 0 else col2
        if col.button(faq):
            selected_faq_query = faq

    query_to_process = selected_faq_query or custom_query.strip()

    if query_to_process:
        st.write(f"Processing your query: *{query_to_process}*")
        with st.spinner("Running your query..."):
            try:
                inputs = {"query": query_to_process}
                result = yt_crew.kickoff(inputs=inputs)
                output = result.raw
                st.subheader("Query Result")
                st.write(output)

            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Enter a custom query or select a question to proceed.")

    if st.button("Back to Home"):
        st.session_state.page = "Main"

def pdf_page():
    set_background_image("images/BG_Img.png") 
    st.title("PDF Query Navigator")
    st.write("This app lets you navigate through the PDF documents and answer your questions")

    custom_query = st.text_input("Enter your Question:", placeholder="e.g., What is NLP?")

    st.subheader("Frequently Asked Questions")
    faq_questions = [
        "What is Spacy?",
        "What is NLTK?",
        "What is Tokenization?",
        "What is Stemming?"
    ]

    selected_faq_query = None
    col1, col2 = st.columns(2)
    for i, faq in enumerate(faq_questions):
        col = col1 if i % 2 == 0 else col2
        if col.button(faq):
            selected_faq_query = faq

    query_to_process = selected_faq_query or custom_query.strip()

    if query_to_process:
        st.write(f"Processing your query: *{query_to_process}*")
        with st.spinner("Running your query..."):
            try:
                inputs = {"query": query_to_process}
                result = pdf_crew.kickoff(inputs=inputs)
                output = result.raw
                st.subheader("Query Result")
                st.write(output)

            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Enter a custom query or select a question to proceed.")

   
    if st.button("Back to Home"):
        st.session_state.page = "Main"

def vacation_page():
    set_background_image("images/BG_Img.png") 
    st.title("Vacation Planner")
    st.write("Plan your perfect vacation with personalized recommendations!")

    st.subheader("Enter Your Vacation Preferences")
    custom_destination = st.text_input("Destination", placeholder="e.g., Tokyo")
    custom_budget = st.number_input("Budget (in USD)", min_value=0, step=500, value=800)
    custom_duration = st.text_input("Duration", placeholder="e.g., 10 days")
    custom_interests = st.multiselect(
                                    "Interests",
                    ["art", "food", "history", "adventure", "nature", "relaxation"],
                    default=[]
        )

    submit_button = st.button("Submit")

    if submit_button:
        if custom_destination and custom_budget and custom_duration and custom_interests:
            st.write(f"Planning your vacation to {custom_destination} for {custom_duration} with a budget of ${custom_budget} and interests in {', '.join(custom_interests)}.")
            with st.spinner("Generating your personalized vacation plan..."):
                try:
                    crew = create_vacation_tasks(
                        destination=custom_destination,
                        budget=custom_budget,
                        duration=custom_duration,
                        interests=custom_interests
                    )

                    result = crew.kickoff()
                    st.subheader("Your Vacation Plan:")
                    st.write(result.raw)

                except Exception as e:
                    st.error(f"An error occurred: {e}")
    else:
        st.warning("Please provide complete details for your vacation.")
   
    if st.button("Back to Home"):
        st.session_state.page = "Main"


def app():
    if 'page' not in st.session_state:
        st.session_state.page = "Main"

    if st.session_state.page == "Main":
        main_page()
    elif st.session_state.page == "SQL":
        sql_page()
    elif st.session_state.page == "YT":
        yt_page()
    elif st.session_state.page == "PDF":
        pdf_page()
    elif st.session_state.page == "VACATION":
        vacation_page()

if __name__ == "__main__":
    app()