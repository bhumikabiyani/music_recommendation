from dotenv import load_dotenv
import os
import json
import base64
from requests import post, get
import csv
import time
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

client_id = ""
client_secret = ""


def get_token():
    try:
        auth_string = client_id + ":" + client_secret
        auth_bytes = auth_string.encode("utf-8")
        auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

        url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization": "Basic " + auth_base64,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"grant_type": "client_credentials"}
        result = post(url, headers=headers, data=data)
        json_result = json.loads(result.content)
        token = json_result["access_token"]
        return token
    except Exception as e:
        print(f"Error getting token: {e}")
        return None


def get_auth_header(token):
    return {"Authorization": "Bearer " + token}


def search_for_artist(token, artist_name):
    try:
        url = "https://api.spotify.com/v1/search"
        headers = get_auth_header(token)
        query = f"?q={artist_name}&type=artist&limit=1"
        query_url = url + query
        result = get(query_url, headers=headers)
        json_result = json.loads(result.content)["artists"]["items"]
        if len(json_result) == 0:
            print(f"Artist '{artist_name}' not found")
            return None
        return json_result[0]
    except Exception as e:
        print(f"Error searching for artist '{artist_name}': {e}")
        return None


def get_song_by_artist(token, artist_id):
    try:
        url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=IN"
        headers = get_auth_header(token)
        result = get(url, headers=headers)
        json_result = json.loads(result.content)["tracks"]
        return json_result
    except Exception as e:
        print(f"Error getting songs for artist ID '{artist_id}': {e}")
        return []


def get_artist_genres(token, artist_id):
    try:
        url = f"https://api.spotify.com/v1/artists/{artist_id}"
        headers = get_auth_header(token)
        result = get(url, headers=headers)
        json_result = json.loads(result.content)
        return json_result.get("genres", [])
    except Exception as e:
        print(f"Error getting genres for artist ID '{artist_id}': {e}")
        return []


def save_songs_to_csv(songs_data, file_name="songs.csv"):
    try:
        with open(file_name, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "Song Name",
                    "Artist Name",
                    "Release Date",
                    "Genres",
                    "Tracks",
                    "Popularity",
                    "Album Name",
                    "Album Type",
                    "Song Duration (ms)",
                ]
            )
            for song in songs_data:
                writer.writerow(song)
    except Exception as e:
        print(f"Error saving songs to CSV: {e}")


def collect_song_data(token, artist_name):
    artist = search_for_artist(token, artist_name)
    if artist:
        try:
            artist_id = artist["id"]
            artist_name = artist["name"]
            artist_genres = get_artist_genres(token, artist_id)
            songs = get_song_by_artist(token, artist_id)

            song_data = []
            for song in songs:
                try:
                    album_id = song["album"]["id"]
                    album_tracks_url = (
                        f"https://api.spotify.com/v1/albums/{album_id}/tracks"
                    )
                    headers = get_auth_header(token)
                    album_tracks_result = get(album_tracks_url, headers=headers)
                    album_tracks = json.loads(album_tracks_result.content)["items"]
                    song["album"]["tracks"] = {"items": album_tracks}

                    song_data.append(
                        [
                            song["name"],
                            artist_name,
                            song["album"]["release_date"],
                            ", ".join(artist_genres),
                            ", ".join(
                                [
                                    track["name"]
                                    for track in song["album"]["tracks"]["items"]
                                ]
                            ),
                            song["popularity"],
                            song["album"]["name"],
                            song["album"]["album_type"],
                            song["duration_ms"],
                        ]
                    )
                except Exception as e:
                    print(f"Error processing song '{song['name']}': {e}")
            return song_data
        except Exception as e:
            print(f"Error collecting song data for artist '{artist_name}': {e}")
            return []
    else:
        return []


def main():
    token = get_token()
    if not token:
        print("Failed to retrieve token, exiting.")
        return

    artist_names = [
        "The Weeknd",
        "Taylor Swift",
        "BTS",
        "Drake",
        "Billie Eilish",
        "Ed Sheeran",
        "Justin Bieber",
        "Ariana Grande",
        "Olivia Rodrigo",
        "Doja Cat",
        "Post Malone",
        "Dua Lipa",
        "Harry Styles",
        "Lil Nas X",
        "Bad Bunny",
        "J Balvin",
        "Cardi B",
        "Travis Scott",
        "Khalid",
        "Shawn Mendes",
        "Halsey",
        "The Kid LAROI",
        "Maroon 5",
        "Imagine Dragons",
        "Selena Gomez",
        "Camila Cabello",
        "Juice WRLD",
        "Megan Thee Stallion",
        "Sam Smith",
        "Sia",
        "Nicki Minaj",
        "Marshmello",
        "Calvin Harris",
        "Bruno Mars",
        "Lady Gaga",
        "Katy Perry",
        "Chris Brown",
        "Jason Derulo",
        "Alan Walker",
        "David Guetta",
        "Becky G",
        "Anitta",
        "Shakira",
        "Maluma",
        "Ricky Martin",
        "Enrique Iglesias",
        "Luis Fonsi",
        "Ozuna",
        "Karol G",
        "BLACKPINK",
        "EXO",
        "TWICE",
        "SEVENTEEN",
        "Stray Kids",
        "ITZY",
        "Red Velvet",
        "NCT 127",
        "TXT",
        "GOT7",
        "Monsta X",
        "Super Junior",
        "BigBang",
        "PSY",
        "IU",
        "Taeyeon",
        "Zico",
        "Dean",
        "Crush",
        "G-Dragon",
        "Jay Park",
        "Epik High",
        "BTS (Jimin)",
        "BTS (Jungkook)",
        "BTS (V)",
        "BTS (RM)",
        "BTS (Suga)",
        "BTS (J-Hope)",
        "BTS (Jin)",
        "aespa",
        "NCT DREAM",
        "Pentagon",
        "Everglow",
        "LOONA",
        "Dreamcatcher",
        "(G)I-DLE",
        "Mamamoo",
        "Apink",
        "Lovelyz",
        "OH MY GIRL",
        "Weki Meki",
        "Cherry Bullet",
        "Fromis_9",
        "Rocket Punch",
        "Weeekly",
        "IZ*ONE",
        "STAYC",
        "CIX",
        "TREASURE",
        "ENHYPEN",
        "TXT",
        "Future",
        "Lizzo",
        "DJ Khaled",
        "H.E.R.",
        "Roddy Ricch",
        "21 Savage",
        "Young Thug",
        "Lil Baby",
        "Pop Smoke",
        "Saweetie",
        "A Boogie wit da Hoodie",
        "Tyler, The Creator",
        "Machine Gun Kelly",
        "Jack Harlow",
        "Polo G",
        "Lil Durk",
        "NAV",
        "Quavo",
        "Offset",
        "Takeoff",
        "Big Sean",
        "Lil Uzi Vert",
        "Migos",
        "YG",
        "Trippie Redd",
        "Tory Lanez",
        "Playboi Carti",
        "Gunna",
        "DaBaby",
        "Blueface",
        "Lil Tjay",
        "Juicy J",
        "Kodak Black",
        "Rick Ross",
        "Meek Mill",
        "Fetty Wap",
        "Wiz Khalifa",
        "2 Chainz",
        "Ty Dolla $ign",
        "T-Pain",
        "Flo Rida",
        "A$AP Rocky",
        "A$AP Ferg",
        "Chance The Rapper",
        "Macklemore",
        "Logic",
        "NF",
        "XXXTENTACION",
        "Ski Mask the Slump God",
        "Rich The Kid",
        "YBN Cordae",
        "BlocBoy JB",
        "Lil Skies",
        "Swae Lee",
        "Rae Sremmurd",
        "Bryson Tiller",
        "PnB Rock",
        "Tinashe",
        "Ella Mai",
        "Summer Walker",
        "Kehlani",
        "Jhené Aiko",
        "Teyana Taylor",
        "SZA",
        "FKA twigs",
        "Solange",
        "Normani",
        "Halsey",
        "Charlie Puth",
        "Bazzi",
        "Lauv",
        "Conan Gray",
        "Troye Sivan",
        "Shawn Mendes",
        "Alec Benjamin",
        "Rex Orange County",
        "Surfaces",
        "Jeremy Zucker",
        "Chelsea Cutler",
        "blackbear",
        "Quinn XCII",
        "Benny Blanco",
        "Jonas Blue",
        "Kygo",
        "Zedd",
        "The Chainsmokers",
        "DJ Snake",
        "Avicii",
        "Martin Garrix",
        "Marshmello",
        "Alesso",
        "Steve Aoki",
        "Diplo",
        "Skrillex",
        "Deadmau5",
        "Calvin Harris",
        "David Guetta",
        "Afrojack",
        "Tiesto",
        "Armin van Buuren",
        "Dimitri Vegas & Like Mike",
        "Hardwell",
        "Alan Walker",
        "KSHMR",
        "Yellow Claw",
        "Don Diablo",
        "Oliver Heldens",
        "Lost Frequencies",
        "Robin Schulz",
        "Galantis",
        "Nicky Romero",
        "Arijit Singh",
        "Shreya Ghoshal",
        "Sunidhi Chauhan",
        "Armaan Malik",
        "Badshah",
        "Neha Kakkar",
        "Atif Aslam",
        "Lata Mangeshkar",
        "Kishore Kumar",
        "Asha Bhosle",
        "Kumar Sanu",
        "Udit Narayan",
        "Alka Yagnik",
        "Sonu Nigam",
        "Mohit Chauhan",
        "Jubin Nautiyal",
        "Palak Muchhal",
        "Yo Yo Honey Singh",
        "Papon",
        "Mika Singh",
        "Shaan",
        "Ankit Tiwari",
        "Benny Dayal",
        "Neeti Mohan",
        "Vishal Dadlani",
        "Himesh Reshammiya",
        "KK",
        "Shankar Mahadevan",
        "Javed Ali",
        "Sukhwinder Singh",
        "Monali Thakur",
        "Harshdeep Kaur",
        "Shilpa Rao",
        "Arijit Singh",
        "Amit Trivedi",
        "Rahat Fateh Ali Khan",
        "Dhvani Bhanushali",
        "Siddharth Slathia",
        "Anirudh Ravichander",
        "Jonita Gandhi",
        "Shalmali Kholgade",
        "Tulsi Kumar",
        "Kanika Kapoor",
        "Asees Kaur",
        "Armaan Malik",
        "Anupam Roy",
        "Arijit Singh",
        "B Praak",
        "Divya Kumar",
        "Gippy Grewal",
        "Hardy Sandhu",
        "Harrdy Sandhu",
        "Arijit Singh",
        "Jasleen Royal",
        "Kailash Kher",
        "Madhushree",
        "Manoj Tiwari",
        "Mamta Sharma",
        "Neha Bhasin",
        "Nikhil D'Souza",
        "Palak Muchhal",
        "Papon",
        "Payal Dev",
        "Prakriti Kakar",
        "Rahul Vaidya",
        "Rashmeet Kaur",
        "Richa Sharma",
        "Shilpa Rao",
        "Shreya Ghoshal",
        "Sneha Khanwalkar",
        "Sona Mohapatra",
        "Sonu Kakkar",
        "Sunidhi Chauhan",
        "Swanand Kirkire",
        "Vishal-Shekhar",
        "Zubeen Garg",
        "Arijit Singh",
        "Darshan Raval",
        "Guru Randhawa",
        "Ritviz",
        "Nucleya",
        "Sachet-Parampara",
        "Tanishk Bagchi",
        "Pritam",
        "Mithoon",
        "Vishal Mishra",
        "Anu Malik",
        "A. R. Rahman",
        "Ilaiyaraaja",
        "R. D. Burman",
        "S. D. Burman",
        "Shankar-Ehsaan-Loy",
        "Salim-Sulaiman",
        "Devi Sri Prasad",
        "M. M. Keeravani",
        "Ghantasala",
        "K. J. Yesudas",
        "P. Susheela",
        "S. P. Balasubrahmanyam",
        "Vani Jairam",
        "K. S. Chithra",
        "S. Janaki",
        "Haricharan",
        "Shankar Mahadevan",
        "Harris Jayaraj",
        "Yuvan Shankar Raja",
        "D. Imman",
        "G. V. Prakash Kumar",
        "Vijay Yesudas",
        "Sid Sriram",
        "Shreya Ghoshal",
        "Chinmayi",
        "Shweta Mohan",
        "Saindhavi",
        "L. R. Eswari",
        "Bombay Jayashri",
        "Rajesh Krishnan",
        "Armaan Malik",
        "Neha Kakkar",
        "Arijit Singh",
        "Sreerama Chandra",
        "Anuradha Paudwal",
        "Jagjit Singh",
        "Chitra",
        "Sonu Nigam",
        "Kumar Sanu",
        "Alka Yagnik",
        "Udit Narayan",
        "Asha Bhosle",
        "Shankar Mahadevan",
        "Kailash Kher",
        "Sunidhi Chauhan",
        "Arijit Singh",
        "Rahat Fateh Ali Khan",
        "Arijit Singh",
        "Jubin Nautiyal",
        "Palak Muchhal",
        "Papon",
        "Neha Kakkar",
        "Amit Trivedi",
        "Shankar Mahadevan",
        "Shaan",
        "KK",
        "Shreya Ghoshal",
        "Sukhwinder Singh",
        "Harshdeep Kaur",
        "Monali Thakur",
        "Dhvani Bhanushali",
        "Shilpa Rao",
    ]
    all_songs_data = []
    total_artists = len(artist_names)

    with ThreadPoolExecutor(max_workers=10) as executor, tqdm(
        total=total_artists, desc="Collecting song data"
    ) as pbar:
        future_to_artist = {
            executor.submit(collect_song_data, token, artist_name): artist_name
            for artist_name in artist_names
        }
        for future in as_completed(future_to_artist):
            artist_name = future_to_artist[future]
            try:
                artist_songs_data = future.result()
                all_songs_data.extend(artist_songs_data)
            except Exception as e:
                print(f"Error collecting data for artist '{artist_name}': {e}")
            pbar.update(1)

    save_songs_to_csv(all_songs_data)


if __name__ == "__main__":
    main()
