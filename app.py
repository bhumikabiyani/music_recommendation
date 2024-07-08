import pickle
import streamlit as st
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Spotify API credentials
CLIENT_ID = "8e5a55baee364ceeb746d9ceb56963f2"
CLIENT_SECRET = "83b131b4f96c4f418d107372a09f71e7"

# Initialize the Spotify client
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Function to get album cover URL and Spotify track URL for a song
def get_song_urls(song_name, artist_name):
    search_query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=search_query, type="track")

    if results and results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        album_cover_url = track["album"]["images"][0]["url"]
        spotify_track_url = track["external_urls"]["spotify"]
        return album_cover_url, spotify_track_url
    else:
        return "https://i.postimg.cc/0QNxYz4V/social.png", ""  # Default image and empty URL if not found

# Function to recommend similar songs
def recommend(song, num_recommendations):
    try:
        index = music[music['Song Name'].str.lower() == song.lower()].index[0]
    except IndexError:
        st.error("Song not found in the dataset.")
        return [], [], []

    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_music_names = []
    recommended_music_posters = []
    recommended_music_urls = []

    for i in distances[1:num_recommendations+1]:  # Get top N recommendations based on user input
        artist = music.iloc[i[0]]['Artist Name']
        poster_url, track_url = get_song_urls(music.iloc[i[0]]['Song Name'], artist)
        recommended_music_posters.append(poster_url)
        recommended_music_names.append(music.iloc[i[0]]['Song Name'])
        recommended_music_urls.append(track_url)

    return recommended_music_names, recommended_music_posters, recommended_music_urls

# Page configuration
st.set_page_config(page_title="Music Recommender System", page_icon=":musical_note:", layout="wide")

# Load the dataset and similarity matrix
music = pd.read_pickle("song_dataset.pkl")
with open('count_vectorizer.pkl', 'rb') as f:
    similarity = pickle.load(f)

# CSS styling with gradient background
st.markdown(
    """
    <style>
    .main {
        background: linear-gradient(to right, #cfd9df, #e2ebf0, #a6c0fe, #f68084, #a6c0fe, #a2a2a1);
        background-size: cover;
        background-position: center;
        padding: 20px;
    }
    .stTextInput > div > div > input {
        background-color: white;  /* Change input bar background to white */
        color: black;  /* Change text color inside input to black */
        text-align: center;  /* Center-align text in input */
    }
    .stNumberInput > div > div > input {
        background-color: white;  /* Change input bar background to white */
        color: black;  /* Change text color inside input to black */
        text-align: center;  /* Center-align text in input */
    }
    .stButton > button {
        background-color: #4CAF50;
        color: white;
    }
    .stButton > button:hover {
        background-color: #45a049;
    }
    .song-box {
        background-color: rgba(255, 255, 255, 0.8);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        color: black;
        display: inline-block; /* Display as inline-block to center in columns */
    }
    h1, h2, h3, h4, h5, h6, p, .stSelectbox, .stButton {
        color: black; /* Ensure all text color is black */
        text-align: center; /* Center-align headers and text */
    }
    .song-image {
        cursor: pointer;
    }
    </style>
    """, 
    unsafe_allow_html=True
)

# Streamlit app content
st.title('🎵 Music Recommender System')
st.markdown("### Discover new music based on your favorite tracks!")

# Center-align the dropdown and number input
music_list = music['Song Name'].values
selected_song = st.selectbox(
    "Type or select a song from the dropdown",
    music_list,
    index=0,
    key="song_select"
)

# Number input to specify the number of recommendations
num_recommendations = st.number_input(
    "Number of recommendations you want",
    min_value=1,
    max_value=20,
    value=5,
    step=1,
    key="num_recommendations"
)

# Button to show recommendations
if st.button('Show Recommendation'):
    recommended_music_names, recommended_music_posters, recommended_music_urls = recommend(selected_song, num_recommendations)
    
    if recommended_music_names:
        st.markdown("### Recommended Songs:")
        cols = st.columns(num_recommendations)
        for col, name, poster, url in zip(cols, recommended_music_names, recommended_music_posters, recommended_music_urls):
            with col:
                st.markdown(f"<div class='song-box'><h4>{name}</h4><a href='{url}' target='_blank'><img src='{poster}' class='song-image' width='100%'></a></div>", unsafe_allow_html=True)
    else:
        st.write("No recommendations available.")
