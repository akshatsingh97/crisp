Run `docker system prune -a --volumes` to remove all unused images, containers, networks, and volumes. This command deletes data permanently. Check what you need first.

"Unused" means not used by a running container. Stopped containers are removed first, so their images become unused too.

**Safe option (review first)**

1. Run `docker system df` to see how much space Docker uses.
2. Run `docker system prune -a --volumes`.
3. Type `y` at the prompt. Docker prints the total space reclaimed.

**Remove everything, including running containers**

Use this only if you want a full reset. It stops and deletes all containers, even running ones.

```bash
docker stop $(docker ps -aq)
docker rm -f $(docker ps -aq)
docker rmi -f $(docker images -aq)
docker volume rm $(docker volume ls -q)
docker system prune -a --volumes -f
```

**Remove one type only**

```bash
docker container prune    # stopped containers
docker image prune -a     # unused images
docker volume prune       # unused volumes
docker builder prune -a   # build cache
```

**Warnings**

- Volume deletion loses database data and other stored files. Back up any volume you need first.
- On Docker 23 and later, `docker volume prune` removes only anonymous volumes. Add `-a` to remove named volumes too.
- The next `docker pull` or `docker build` will download images again.

**Troubleshooting**

- If a command prints `"docker rm" requires at least 1 argument`, nothing of that type exists. Ignore it.
- If an image cannot be removed because a container uses it, remove that container first.
- On Docker Desktop (Mac or Windows), space may not return to the host after pruning. Use Settings, then Resources, then "Disk image size" or "Clean / Purge data" to shrink the disk image.
