import json
import os
import re

from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

with open("config.json") as f:
    config = json.load(f)
root_path = config.get("root_path")
dest_path = config.get("dest_path")

if not root_path:
    root_path = input("Enter the path to the music folder: ")

if not dest_path:
    dest_path = input("Enter the path to the destination folder: ")


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
    "Pop": r"(pop\b|(ping))|(alt\s|-z)|(\bglitch)|(indietronica)|(shonen)",
    "Dance": r"(dance\b)|(\bedm\b)|(\bdisco)|(step\b)",
    "Rap": r"(\brap)|(g-|\sfunk)",
    "R&B": r"(\br&b\b)|(blues)|((\b|-)soul)|(rythm)",
    "Trap": r"(\btrap\b|(run))|((\b|-)drill)",
    "Japanese": r"(\banime\b)|(\bjapan)|(otacore)|(j-.+)",
    "Electronic": r"(\bsynth)|(chill(synth)|(wave))|(\belectro)|(liquid\b)|(big\sroom)|(\broom)|(weirdcore)|(dubstep)|"
                  r"(tronic)|(chicago)|(complextro)",
    "Hip Hop": r"(\bhip\shop\b)",
    "Instrumental": r"(\binstrumental\b)|(\bbackground\b)|(\bsoundtrack\b)"
                    r"|(acoustic\b)|(video game music)|(vgm)|(\blo(-|\s)?fi\b)"
                    r"|(\bacoustic\b)|(\bpiano)|(\bguitar\b)|(scorecore)",
    "Indie": r"(\bindie)",
    "Jazz": r"(jazz)|(sax)",
    "Rock": r"(\brock(\b|-|\s))|(indietronica)|(shonen)",
    "Eurobeat": r"(\beurobeat)",
    "Classic": r"(\bclassic)|(mpb\b)|(\bcountry)|(carnatic)|(folk\b)|(bhangra)",
    "Metal": r"(\bmetal)",
    "Soundtracks": r"(score(\s|\b|(core)))|(filmi)|(movie(\b|-))|(.+wood)"
}

for file in files:
    tag = EasyID3(file)
    genre = tag.get("genre")
    if genre:
        genres.append(genre[0])

genres = set(genres)
genre_map = {}
misc_genres = []

for genre in genres:
    mainstreams = []
    for mainstream_genre in regex_dictionary:
        if re.findall(regex_dictionary[mainstream_genre], genre):
            mainstreams.append(mainstream_genre)
            print(f"{genre} matches {mainstream_genre}")

    if not mainstreams:
        mainstreams = ["Misc"]
        misc_genres.append(genre)

    genre_map[genre] = mainstreams

file_map = {}
for genre in list(regex_dictionary.keys()) + ["Misc"]:
    print(f"Generating file for: {genre}")
    file_map[genre] = open(os.path.join(dest_path, f"{genre}.m3u8"), "w", encoding="utf-8", newline="\n")
    file_map[genre].write("#EXTM3U\n")
    file_map[genre].write("#EXTENC:UTF-8\n")
    file_map[genre].write(f"#PLAYLIST:{genre} By Mahas1\n")
    file_map[genre].write(f"#EXTGENRE:{genre}\n\n")
# genre categorization has been done


for file in files:
    tag = EasyID3(file)
    tag2 = MP3(file)
    title = tag.get("title")[0]
    artist = tag.get("artist", "None")[0]

    genre = tag.get("genre", ["misc"])[0]
    supergenres = genre_map.get(genre, ["Misc"])
    print("Sorting:", title)
    print("Genre:", genre)
    for supergenre in supergenres:
        print("Found Genre:", supergenre)
        file_obj = file_map.get(supergenre)
        if not file_obj:
            print(f"File object for {title} not found")
            continue
        file_obj.write(f"#EXTINF:{int(tag2.info.length)},{artist} - {title}\n"
                       f"{file}\n\n")
        file_obj.flush()
    print()


print("Misc genres")
for i in misc_genres:
    print("--|", i)
