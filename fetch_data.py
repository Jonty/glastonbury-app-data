import requests
import os
import json

FIREBASE_PROJECT = os.environ["FIREBASE_PROJECT"]
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
YEAR = os.environ["YEAR"]

response = requests.post(
    f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={GOOGLE_API_KEY}",
    json={"returnSecureToken": True},
)
token = response.json()
auth_headers = {"Authorization": "Bearer %s" % token["idToken"]}

for collection in (
    "notifications",
    "news",
    "info",
    "info_pages",
    "performances",
    "stages",
    "artists",
    "areas",
    "map_pois",
):  # Locations?
    data = {}
    next_page = ""

    while not data or next_page:
        print("Fetching %s%s" % (collection, next_page))
        response = requests.get(
            "https://firestore.googleapis.com/v1/projects/%s/databases/(default)/documents/%s/%s"
            % (FIREBASE_PROJECT, collection, next_page),
            headers=auth_headers,
        )
        if response.status_code != 200:
            raise Exception(response.content)

        response_json = response.json()
        if not data:
            data = response_json
        else:
            data["documents"].extend(response_json["documents"])

        next_page = ""
        if "nextPageToken" in response_json:
            next_page = "?pageToken=%s" % response_json["nextPageToken"]

    if "nextPageToken" in data:
        del data["nextPageToken"]

    print("Writing %s" % collection)
    path = f"data/{YEAR}/raw/"
    try:
        os.makedirs(path)
    except FileExistsError:
        pass

    with open(path + f"{collection}.json", "w") as f:
        json.dump(data, f, sort_keys=True, indent=4)
