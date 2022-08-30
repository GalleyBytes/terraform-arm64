import requests
import argparse
import re
from pprint import pprint

def terraform_versions(url):
    print(url)
    versions = []
    while True:
        resp = requests.get(f"{url}")
        data = resp.json()
        for item in data["results"]:
            if item["name"] not in versions:
                versions.append(item["name"])
        url = data.get("next")
        if not url:
            break
    return versions

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--repo', required=True, help="Github organization owner of image")
    parser.add_argument('-i', '--image', required=True, help="Container Image (no tags)")
    args = parser.parse_args()

    versions = terraform_versions("https://registry.hub.docker.com/v2/repositories/hashicorp/terraform/tags/?page=1")
    built_versions = terraform_versions(f"https://registry.hub.docker.com/v2/repositories/{args.repo}/{args.image}/tags/?page=1")

    unbuilt_versions = []
    for v in versions:
        if v not in built_versions:
            if re.match("[0-9]+.[0-9]+.[0-9]+", v):
                if int(v.split(".")[0]) != 0 or int(v.split(".")[1]) >= 11:
                    unbuilt_versions.append(v)
    print(unbuilt_versions)


    # TODO docker build and push


