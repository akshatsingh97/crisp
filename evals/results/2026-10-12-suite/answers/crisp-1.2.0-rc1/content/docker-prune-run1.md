Run `docker system prune -a --volumes` to remove all unused images, containers, networks, and volumes in one step.

This command is destructive. It deletes data and you cannot undo it. Volumes often hold database data. Check what you have first.

**Option 1: Remove only unused items**

1. Check disk use: `docker system df`
2. Run: `docker system prune -a --volumes`
3. Type `y` to confirm.

The `-a` flag removes all unused images, not only dangling ones. The `--volumes` flag also removes unused volumes. Docker keeps anything that a running container uses. Docker 23.0 and later prunes only anonymous volumes with `--volumes`. To remove named volumes too, add `-a` and use `docker volume prune -a`.

**Option 2: Remove everything, including running containers**

Use this only if you want a full reset.

1. Stop all containers: `docker stop $(docker ps -aq)`
2. Remove all containers: `docker rm $(docker ps -aq)`
3. Remove all images: `docker rmi -f $(docker images -aq)`
4. Remove all volumes: `docker volume rm $(docker volume ls -q)`

If a list is empty, the command prints a usage error. This is harmless. Skip that step.

**Option 3: Remove one type at a time**

- Containers that stopped: `docker container prune`
- Unused images: `docker image prune -a`
- Unused volumes: `docker volume prune`
- Build cache: `docker builder prune -a`

**Notes**

- Build cache can use many GB. `docker system prune` does not always clear it. Run `docker builder prune -a` to remove it.
- Add `-f` to any prune command to skip the confirmation prompt.
- On Docker Desktop for Mac or Windows, the virtual disk file may not shrink after cleanup. Use Settings, then Resources, then "Disk image size", or use "Clean / Purge data" to reclaim space.
- If a volume holds data you need, back it up first. For example, run a temporary container that mounts the volume and archives it with `tar`.
