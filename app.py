import joblib
import streamlit as st
import pandas as pd
import re
# Wczytanie modelu
model = joblib.load("best_model.pkl")
tab1, tab2 = st.tabs(["Główna", "Szacowane tempa"])


def seconds_to_hms(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours}h {minutes}m {secs}s"


with tab1:
    st.title("🏁Szacowanie czasu ukończenia wyścigu🏁")
        # Szukamy płci
    user_input = st.text_area("Napisz coś o sobie, np. 'Jestem kobietą, mam 28 lat, a moje średnie tempo to 5:00'")
    imiona_meskie = {'adam', 'marek', 'jan', 'piotr', 'pawel', 'krzysztof', 'lukasz', 'andrzej', 'mikolaj'}
    imiona_damskie = {'anna', 'katarzyna', 'magda', 'ewa', 'agata', 'marta', 'agnieszka', 'joanna'}
    def parse_input(text):
        gender = None
        
        # 1. Sprawdź słowa kluczowe "kobieta", "mężczyzna" itp.
        if re.search(r'\bkobiet\w*\b', text, re.I):
            gender = 'K'  # kobieta
        elif re.search(r'\bmężczyzn\w*\b', text, re.I) or re.search(r'\bmężczyzna\b', text, re.I):
            gender = 'M'  # mężczyzna

        # 2. Jeśli nie znaleziono płci, spróbuj na podstawie imienia
        if not gender:
            text_lower = text.lower()
            for imie in imiona_meskie:
                if re.search(r'\b' + re.escape(imie) + r'\b', text_lower):
                    gender = 'M'
                    break
            if not gender:
                for imie in imiona_damskie:
                    if re.search(r'\b' + re.escape(imie) + r'\b', text_lower):
                        gender = 'K'
                        break

        
        # Szukamy wieku (liczba 1-3 cyfrowa)
        age_match = re.search(r'(\d{1,3})\s*lat', text)
        age = int(age_match.group(1)) if age_match else None

        # Szukamy tempa - format mm:ss lub mm,ss
        pace_match = re.search(r'(\d{1,2})[:.,](\d{2})', text)
        pace = None
        if pace_match:
            minutes = int(pace_match.group(1))
            seconds = int(pace_match.group(2))
            pace = minutes + seconds / 60  # tempo w minutach dziesiętnych

        return gender, age, pace

    gender, age, pace = parse_input(user_input)

    st.write(f"Płeć: {gender}, Wiek: {age}, Tempo: {pace}")


    if gender and age and pace:
        # zakładam, że model potrzebuje Płeć zakodowanej jako liczba
        gender_num = 0 if gender == 'M' else 1

        data = pd.DataFrame({
            "Płeć": [gender_num],
            "Kategoria wiekowa": [age],
            "5 km Tempo": [pace]
        })

        predicted_time = model.predict(data)[0]
        st.write(f"Przewidywany czas ukończenia wyścigu: {seconds_to_hms(predicted_time)}✅")

    else:
        st.write("Proszę podaj wszystkie wymagane informacje w opisie.")
with tab2:
    st.title(" Przykłady średnich temp")
    data = {
        'Zwierzę': ['👟 Człowiek (średnie tempo)', '🐇 Królik', '🦌 Gazela', '🦅 Sokół w locie', '🐢 Żółw'],
        'Tempo (min/km)': ['5:00', '3:00', '2:00', '0:50', '30:00'],
        'Prędkość (km/h)': [12, 20, 30, 70, 1.2]
    }

    df = pd.DataFrame(data)

    st.table(df)