import streamlit as st
import requests
from geopy.geocoders import Nominatim

# --- Styling for Chat Bubbles ---
st.markdown("""
<style>
.user-bubble {
    background-color: #DCF8C6;
    padding: 10px;
    border-radius: 10px;
    margin: 5px 0px;
    text-align: right;
}
.bot-bubble {
    background-color: #E6E6E6;
    padding: 10px;
    border-radius: 10px;
    margin: 5px 0px;
    text-align: left;
}
</style>
""", unsafe_allow_html=True)

# --- Disease Info Database (sample of 20, you can expand to 100+) ---
disease_info = {
    "covid": {
        "symptoms": ["fever", "cough", "tiredness", "loss of taste", "loss of smell"],
        "prevention": "Wear masks, wash hands, maintain distance, get vaccinated",
        "treatment": "Rest, hydration, paracetamol for fever, consult a doctor if severe",
        "synonyms": {
            "fever": ["high temperature", "temperature rise", "hot"],
            "loss of smell": ["smell lost", "cannot smell", "anosmia"],
            "loss of taste": ["taste lost", "cannot taste", "ageusia"],
            "tiredness": ["fatigue", "exhausted", "weakness"]
        }
    },
    "malaria": {
        "symptoms": ["fever", "chills", "sweating", "headache"],
        "prevention": "Use mosquito nets, avoid stagnant water, take preventive medicines",
        "treatment": "Antimalarial tablets – only on doctor’s advice",
        "synonyms": {
            "fever": ["high temperature", "hot", "pyrexia"],
            "chills": ["shivering", "cold feeling"],
            "headache": ["migraine", "head pain"]
        }
    },
    "dengue": {
        "symptoms": ["high fever", "rash", "joint pain", "nausea"],
        "prevention": "Avoid mosquito bites, use repellents, keep surroundings clean",
        "treatment": "Paracetamol, rest, hydration, monitor platelets",
        "synonyms": {
            "fever": ["high temperature", "hot"],
            "joint pain": ["painful joints", "arthralgia"],
            "nausea": ["vomiting", "queasy"]
        }
    },
    "diabetes": {
        "symptoms": ["frequent urination", "thirst", "fatigue", "slow wound healing"],
        "prevention": "Exercise regularly, maintain healthy diet, monitor sugar levels",
        "treatment": "Oral medicines (metformin, sulfonylureas), insulin if needed",
        "synonyms": {
            "fatigue": ["tiredness", "exhaustion", "weakness"]
        }
    },
    "asthma": {
        "symptoms": ["breathing difficulty", "wheezing", "chest tightness"],
        "prevention": "Avoid smoke, dust, allergens; use inhalers as prescribed",
        "treatment": "Bronchodilator inhalers (salbutamol), corticosteroid inhalers",
        "synonyms": {
            "breathing difficulty": ["shortness of breath", "dyspnea"]
        }
    },
    # ... continue adding up to 100 diseases
}

# --- Emergency Cases ---
emergency_cases = {
    "Severe chest pain": "🚨 May indicate a heart attack. Call emergency services immediately!",
    "Severe breathing difficulty": "🚨 Possible asthma attack, severe pneumonia, or COVID. Seek urgent medical help!",
    "Unconsciousness": "🚨 Medical emergency. Call ambulance immediately!",
    "Heavy bleeding": "🚨 Apply pressure, do not wait – go to hospital urgently!",
    "Seizure": "🚨 Ensure safety, lay person on their side, seek immediate medical care!"
}

# --- Chat History ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("🩺 AI-Driven Public Health Chatbot 🤖")

# --- User Query Section ---
user_input = st.text_input("Type your question or symptoms:", key="user_input")

if user_input:
    st.session_state.chat_history.append(("user", user_input))
    query = user_input.lower()
    matched_disease = None

    # --- Symptom Matching with Synonyms ---
    for disease, info in disease_info.items():
        for symptom in info["symptoms"]:
            synonyms = info.get("synonyms", {}).get(symptom, [])
            if symptom in query or any(syn in query for syn in synonyms):
                matched_disease = disease
                break
        if matched_disease:
            break

    # --- Generate Response ---
    if matched_disease:
        info = disease_info[matched_disease]
        response = (
            f"**{matched_disease.capitalize()}**\n\n"
            f"🧾 Symptoms: {', '.join(info['symptoms'])}\n\n"
            f"🛡 Prevention: {info['prevention']}\n\n"
            f"💊 Suggested Care: {info['treatment']}\n\n"
            f"*Disclaimer: This is only an AI-based guess. Please consult a doctor for proper diagnosis.*"
        )
    else:
        response = "Sorry, I couldn't identify the disease. Please consult a doctor for proper guidance."

    st.session_state.chat_history.append(("bot", response))

# --- Display Chat Bubbles ---
for sender, msg in st.session_state.chat_history:
    if sender == "user":
        st.markdown(f"<div class='user-bubble'>{msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-bubble'>{msg}</div>", unsafe_allow_html=True)

# --- Nearby Hospitals Finder ---
st.subheader("🏥 Find Nearby Hospitals (Free)")
location_input = st.text_input("Enter your city or address to find nearby hospitals:", key="hospital_input")

if location_input:
    try:
        geolocator = Nominatim(user_agent="health_chatbot")
        location = geolocator.geocode(location_input)
        if location:
            st.write(f"Searching hospitals near: {location.address}")
            overpass_url = "http://overpass-api.de/api/interpreter"
            query = f"""
            [out:json];
            node
              ["amenity"="hospital"]
              (around:5000,{location.latitude},{location.longitude});
            out;
            """
            response = requests.get(overpass_url, params={'data': query})
            data = response.json()
            if data['elements']:
                st.write("Here are some nearby hospitals:")
                for element in data['elements'][:10]:
                    name = element['tags'].get('name', 'Unknown Hospital')
                    st.markdown(f"- **{name}**")
            else:
                st.write("No hospitals found nearby.")
        else:
            st.write("Invalid location. Please try again.")
    except Exception as e:
        st.error(f"Error fetching hospitals: {e}")

# --- Emergency Assistance ---
st.subheader("🚑 Emergency Assistance")
selected_emergency = st.selectbox("Select an emergency situation:", ["None"] + list(emergency_cases.keys()))
if selected_emergency != "None":
    st.error(emergency_cases[selected_emergency])
