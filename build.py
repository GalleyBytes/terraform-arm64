#!/usr/bin/env python3
import requests
import re
import os
import base64
import docker
from docker.errors import BuildError


def dockerhub_scrape_tags(url :str) -> list:
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

def ghcr_scrape_tags(host :str , org :str, package: str) -> list:
    headers = {}
    try:
        ghcr_auth = base64.b64encode(os.environ["GITHUB_TOKEN"].encode())
        headers["Authorization"] = f"Bearer {ghcr_auth.decode()}"
    except KeyError as e:
        print("Require GITHUB_TOKEN", e)
        exit(1)

    tags = []
    baseurl = f"https://{host}"
    query = f"/v2/{org}/{package}/tags/list?n=0"
    while True:
        url = f"{baseurl}{query}"
        print(url)
        tags_list_response = requests.get(url, headers=headers)
        if tags_list_response.status_code != 200:
            tags_list_json = tags_list_response.json()
            for err in  tags_list_json["errors"]:
                if err["code"] != "NAME_UNKNOWN":
                    print(tags_list_json)
                    exit(2)
        data = tags_list_response.json()
        if data.get("tags"):
            tags+=data["tags"]
        else:
            break
        if tags_list_response.headers.get("Link") is not None:
            if 'rel="next"' in tags_list_response.headers["Link"]:
                query = tags_list_response.headers["Link"].split(";")[0].lstrip("<").rstrip(">")
            else:
                break
        else:
            break
    return tags

def print_buildlogs(logs):
    for log in logs:
        if log.get("stream"):
            print(log.get("stream"), end="")
        if log.get("aux"):
            print(log.get("aux"))

def delete_local_image(client :docker.DockerClient, image :str) -> None:
    print(f"will remove {image}")
    try:
        client.images.remove(image)
    except BuildError as e:
        print(e)
        exit(1)

if __name__ == "__main__":
    host = "ghcr.io"
    org = "galleybytes"
    package = "terraform-arm64"

    versions = dockerhub_scrape_tags("https://registry.hub.docker.com/v2/repositories/hashicorp/terraform/tags/?page=1")
    built_versions = ghcr_scrape_tags(host, org, package)

    unbuilt_versions = []
    for v in versions:
        if v not in built_versions:
            if re.match("[0-9]+.[0-9]+.[0-9]+", v):
                if int(v.split(".")[0]) != 0 or int(v.split(".")[1]) >= 11:
                    unbuilt_versions.append(v)


    client = docker.from_env()
    for version in unbuilt_versions:
        resp = requests.head(f"https://releases.hashicorp.com/terraform/{version}/terraform_{version}_linux_arm64.zip")
        if resp.status_code == 200:
            arch = "arm64"
        else:
            arch = "arm"

        image = f"{host}/{org}/{package}"
        build, build_logs = client.images.build(
            path=".",
            dockerfile="Dockerfile",
            tag=f"{image}:{version}",
            rm=False,
            quiet=False,
            nocache=False,
            platform="linux/arm64/v8",
            buildargs={"VERSION":version, "ARCH":arch}
        )
        print_buildlogs(build_logs)

        for line in client.images.push(f"{image}", tag=version, stream=True, decode=True):
            print(line)
        delete_local_image(client, f"{image}:{version}")
