import os

import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
from datetime import date


def get_languages():
    """
        Program dillerini return ediyoruz.
    """
    return [
        "",
        "python", "javascript", "java", "c", "c++", "csharp", "go", "typescript",
        "rust", "ruby", "kotlin", "php", "swift", "dart", "shell", "scala",
        "r", "perl", "elixir", "haskell", "julia"
    ]

def fetch_tranding_patch(language,since="daily"):

    """Github trend sayfasına erişip ordan çektiğimiz html verisini parse ediyoruz"""

    url = f"https://github.com/trending/{language}?since={since}"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.text, "html.parser")

    projects = soup.find_all("article", class_="Box-row")
    return projects

def get_github_trends(language, since="daily"):

    data = []
    for project in fetch_tranding_patch():
        repo_title = project.find("h2").text
        repo_title = repo_title.split("/")

        organization_name = repo_title[0].strip()
        repo_name = repo_title[1].strip()

        language_tag = project.find("span", class_="d-inline-block ml-0 mr-3")
        language_name = language_tag.text.strip() if language_tag else "Unknown"

        for tag in project.find_all("a", class_="Link Link--muted d-inline-block mr-3"):
            href = tag.get("href")
            if "stargazer" in href:
                totally_stars = tag.text.strip().replace(",", "")
            elif "forks" in href:
                forks = tag.text.strip().replace(",", "")

        since_stars_tag = project.find("span", class_="d-inline-block float-sm-right")
        since_stars_raw = since_stars_tag.text.strip().replace(",", "") if since_stars_tag else ""
        since_parts = since_stars_raw.split()

        since_stars = since_parts[0]
        since_time_range = " ".join(since_parts[2:])

        time = date.today()

        current_data = {
            "Repositories Name": repo_name,
            "Organization Name": organization_name,
            "Language Name": language_name,
            "Totally stars": totally_stars,
            "Forks": forks,
            "Since Stars": since_stars,
            "Time Range": since_time_range,
            "Date Time": time

        }
        data.append(current_data)
        print(
            f"Language Name: {language_name}\nRepo Name:{repo_name}\nStars:{totally_stars}\nForks:{forks}\nSince Stars:{since_stars}\nTime Range: {since_time_range}\nDate Time:{time}")
    return data


def main():
    if os.path.exists("results.csv"):
        df = pd.read_csv("results.csv", encoding="utf-8-sig")
        print("Önceden kaydedilmiş veriler bulundu. 'results.csv' dosyası güncelleniyor...")
    else:
        df = pd.DataFrame(columns=[
            "Repositories Name", "Organization Name", "Language Name",
            "Totally stars", "Forks", "Since Stars", "Time Range", "Date Time"
        ])
    all_data = []
    for lang in get_languages():
        for period in ["daily", "weekly", "monthly"]:
            print(f"\n #Zaman Aralığı:{period} TRENDLERİ")
            try:
                trends = get_github_trends(language=lang, since=period)
                all_data.extend(trends)
                time.sleep(1)
            except Exception as e:
                print(f"Hata oluştu: {e}")

    if not all_data or len(all_data) == 0:
        print("Hiçbir yeni veri bulunamadı.")
        return

    new_df = pd.DataFrame(all_data)
    df = pd.concat([df, new_df], ignore_index=True)
    df.drop_duplicates(subset=["Repo_name", "Organization Name", "Language Name", "Date Time"], inplace=True)
    df.to_csv("results.csv", index=False, encoding="utf-8-sig")
    print("Veriler başarıyla kaydedildi.")

if __name__ == "__main__":
    main()