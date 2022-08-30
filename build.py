import requests
import argparse
import re
import docker

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

def print_buildlogs(logs):
    for log in logs:
        if log.get("stream"):
            print(log.get("stream"), end="")
        if log.get("aux"):
            print(log.get("aux"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--repo', required=True, help="Dockerhub organization owner of image")
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


    client = docker.from_env()
    for version in unbuilt_versions:
        resp = requests.head(f"https://releases.hashicorp.com/terraform/{version}/terraform_{version}_linux_arm64.zip")
        if resp.status_code == 200:
            arch = "arm64"
        else:
            arch = "arm"

        build, build_logs = client.images.build(
            path=".",
            dockerfile="Dockerfile",
            tag=f"{args.repo}/{args.image}:{version}",
            rm=False,
            quiet=False,
            nocache=False,
            platform="linux/arm64/v8",
            buildargs={"VERSION":version, "ARCH":arch}
        )
        print_buildlogs(build_logs)

        for line in client.images.push(f"{args.repo}/{args.image}", tag=version, stream=True, decode=True):
            print(line)

