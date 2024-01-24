import requests
import os
import sys
import ast

updater_version = "1.0.0"  # DO NOT CHANGE

url = "https://py9.dev/python/Projects/ApplicationBot/latest.txt"
github = "https://github.com/Proyo9/ApplicationBot"

def check(version, file):
    v1 = version.split(".")[0]
    v2 = version.split(".")[1]
    v3 = version.split(".")[2]
    r = requests.get(url)
    latest = r.text
    latest = latest.split(f"<{file}>")[1].split(f"</{file}>")[0].replace("\n", "")
    lv1 = latest.split(".")[0]
    lv2 = latest.split(".")[1]
    lv3 = latest.split(".")[2]
    onLatest = True
    if lv1 > v1:
        onLatest = False
    elif lv2 > v2:
        onLatest = False
    elif lv3 > v3:
        onLatest = False
    if onLatest:
        print(f"You are on the latest ({file}) version!")
    else:
        print(f"There is a new ({file}) version available!")
        print(f"Current version: {version}")
        print(f"Latest version: {latest}")
    return onLatest

def update(file):
    if file == "main":
        update_url = f"https://py9.dev/python/Projects/ApplicationBot/{file}.py"
        print("Updating...")
        r = requests.get(update_url)
        latest = r.text.replace("\n", "")
        with open(f"{file}.py", "w") as f:
            f.write(latest)
        print("Update complete!")
        print("Restarting...")
        os.system("python main.py")
        sys.exit()
    elif file == "bot_config":
        input("Unable to automatically update config!\nPlease go to https://github.com/Proyo9/ApplicationBot/blob/main/bot_config.py and add new config options to your config file.\nPress enter to continue...")
        os.system("python main.py")
        sys.exit()
    elif file == "updater":
        update_url = f"https://py9.dev/python/Projects/ApplicationBot/{file}.py"
        print("Updating Updater...")
        r = requests.get(update_url)
        latest = r.text.replace("\n", "")
        with open(f"{file}.py", "w") as f:
            f.write(latest)
        os.system("python main.py")
        sys.exit()
