set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]
set dotenv-load := true

# Available recipes
[private]
default:
    just --list

[doc("Build Django app image")]
[group("build")]
build *ARGS:
    @echo "Building Django app image"
    @docker build -t django-app:latest -f Docker/Dockerfile {{ ARGS }} .

[doc("Run Django app container")]
[group("operations")]
run *ARGS:
    @docker run --rm -p 8000:8000 --env-file .env django-app:latest {{ ARGS }}

[doc("Explore docker image with Dive")]
[group("operations")]
dive *ARGS:
    @echo "Exploring docker image"
    @docker run -ti --rm -v /var/run/docker.sock:/var/run/docker.sock wagoodman/dive {{ ARGS }}
