import streamlit as st
import pandas as pd
import joblib
import openai
import json
import os
from dotenv import load_dotenv

# Wczytaj klucz API z .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Wczytanie modelu ML
model = joblib.load("best_model.pkl")

# Funkcja pomocnicza: zamiana sekund na h:m:s
def seconds_to_hms(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours}h {minutes}m {secs}s"


def extract_data_with_gpt(user_text):
    system_prompt = (
        "Jesteś asystentem, który z tekstu naturalnego użytkownika wyciąga dane "
        "potrzebne do szacowania wyniku biegu. Z tekstu wyodrębnij płeć ('M' lub 'K'), "
        "wiek (jako liczba całkowita) oraz średnie tempo (w minutach jako float, np. 5.3 oznacza 5 minut 18 sekund). "
        "Zwróć wyłącznie dane w formacie JSON: {\"gender\": \"M\", \"age\": 30, \"pace\": 5.3}."
    )

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ],
            temperature=0
        )
        content = response.choices[0].message.content
        parsed = json.loads(content)
        return parsed["gender"], int(parsed["age"]), float(parsed["pace"])
    except Exception as e:
        st.error(f"Błąd w interpretacji danych: {e}")
        return None, None, None

# UI Streamlit
tab1, tab2 = st.tabs(["Główna", "Szacowane tempa"])

with tab1:
    st.title("🏁Szacowanie czasu ukończenia wyścigu 🧠")

    user_input = st.text_area(
        "Napisz coś o sobie, np. 'Jestem kobietą, mam 28 lat, a moje średnie tempo to 5:00'"
    )
    submit_button = st.button("📊 Zatwierdź i oblicz")

    if submit_button and user_input.strip():
        with st.spinner("Analizuję Twój tekst za pomocą AI..."):
            gender, age, pace = extract_data_with_gpt(user_input)

        st.write(f"**Płeć:** {gender}  \n**Wiek:** {age}  \n**Tempo (min/km):** {pace}")

        if gender and age and pace:
            gender_num = 0 if gender == 'M' else 1

            data = pd.DataFrame({
                "Płeć": [gender_num],
                "Kategoria wiekowa": [age],
                "5 km Tempo": [pace]
            })

            predicted_time = model.predict(data)[0]
            st.success(f"⏱️ Przewidywany czas ukończenia wyścigu: {seconds_to_hms(predicted_time)}")
        else:
            st.warning("Nie udało się poprawnie odczytać wszystkich danych. Spróbuj inaczej sformułować opis.")

with tab2:
    st.title("🏃‍♂️ Przykładowe średnie tempa")
    data = {
        'Zwierzę': ['👟 Człowiek (średnie tempo)', '🐇 Królik', '🦌 Gazela', '🦅 Sokół w locie', '🐢 Żółw'],
        'Tempo (min/km)': ['5:00', '3:00', '2:00', '0:50', '30:00'],
        'Prędkość (km/h)': [12, 20, 30, 70, 1.2]
    }
    df = pd.DataFrame(data)
    st.table(df)