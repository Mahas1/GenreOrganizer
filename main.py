import os
import re
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

root_path = r"/Volumes/Windows/Users/mahas/Music/Plex Music"
dest_path = r""

if not root_path:
    root_path = input("Enter the path to the music folder: ").strip()

if not dest_path:
    dest_path = input("Enter the path to the destination folder: ").strip()


def list_files(root_path, files=[], endswith=".mp3"):
    list = os.listdir(root_path)
    folders = [x for x in list if os.path.isdir(os.path.join(root_path, x))]
    file_entries = [
        os.path.join(root_path, x) for x in list
        if os.path.isfile(os.path.join(root_path, x)) and x.endswith(endswith)
    ]
    files.extend(file_entries)
    for folder in folders:
        files = list_files(os.path.join(root_path, folder), files)
    return files


files = list_files(root_path)
genres = []

regex_dictionary = {
    "Pop": r"(pop\b|(ping))|(alt\s|-z)|(\bglitch)",
    "Rock": r"(\brock\b)",
    "Dance": r"(dance\b)|(\bedm\b)|(\bdisco)|(step\b)",
    "Rap": r"(\brap)|(g-|\sfunk)",
    "R&B": r"(\br&b\b)|(blues)|(neo\ssoul)|(rythm)",
    "Trap": r"(\btrap\b|(run))",
    "Japanese": r"(\banime\b)|(\bjapan)|(otacore)|(j-.+)",
    "Electronic": r"(\bsynth)|(chill(synth)|(wave))|(\belectro)|(liquid\b)|(big\sroom)",
    "Hip Hop": r"(\bhip\shop\b)",
    "Instrumental": r"(\binstrumental\b)|(\bbackground\b)|(\bsoundtrack\b)"
                    r"|(acoustic\b)|(video game music)|(vgm)|(\blo-|\sfi\b)"
                    r"|(\bacoustic\b)|(\bpiano)|(\bguitar\b)",
    "Indie": r"(\bindie\b)",
    "Jazz": r"(jazz)|(sax)",
    "Rock and Roll": r"(\brock-|\sand-|\sroll\b)",
    "Eurobeat": r"(\beurobeat)",
    "Classic": r"(\bclassic)|(mpb\b)|(\bcountry)|(carnatic)|(folk\b)",
    "Metal": r"(\bmetal)",
}

for file in files:
    tag = EasyID3(file)
    genre = tag.get("genre")
    if genre:
        genres.append(genre[0])

genres = set(genres)
genre_map = {}

for genre in genres:
    matched = False
    for mainstream_genre in regex_dictionary:
        if re.findall(regex_dictionary[mainstream_genre], genre):
            genre_map[genre] = mainstream_genre
            matched = True
    if not matched:
        genre_map[genre] = "Misc"

file_map = {}
for genre in set(genre_map.values()):
    file_map[genre] = open(os.path.join(dest_path, f"{genre}.m3u8"), "w", encoding="utf-8", newline="\n")
    file_map[genre].write("#EXTM3U\n")
    file_map[genre].write("#EXTENC:UTF-8\n")
    file_map[genre].write(f"#PLAYLIST:{genre} By Mahasvan\n")
    file_map[genre].write(f"#EXTGENRE:{genre}\n\n")

# genre categorization has been done

for file in files:
    tag = EasyID3(file)
    tag2 = MP3(file)
    title = tag.get("title")[0]
    artist = tag.get("artist", "None")[0]

    genre = tag.get("genre", ["Misc"])[0]
    supergenre = genre_map.get(genre, "Misc")
    file_obj = file_map.get(supergenre)
    print("Sorting:", title)
    print("Found Genre:", supergenre)
    file_obj.write(f"#EXTINF:{int(tag2.info.length)},{artist} - {title}\n"
                   f"{file}\n\n")
    file_obj.flush()
    print()
