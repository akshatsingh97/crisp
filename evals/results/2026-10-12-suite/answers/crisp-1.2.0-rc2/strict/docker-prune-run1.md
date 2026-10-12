Run `docker system prune -a --volumes` to remove all unused data. It cannot be undone, and it only removes items that no running container uses.

Warning: this command deletes data for good. Volumes can hold databases and uploads. Back up any volume that you need before you continue.

1. Run `docker system prune -a --volumes`.
2. Type `y` to confirm. Add `-f` to skip the prompt.

The command removes these items:
- Stopped containers
- Unused networks
- All images that no container uses
- Unused volumes
- Build cache

In Docker Engine 23.0 and later, `--volumes` removes only anonymous volumes (volumes without a name). To remove named volumes too, run `docker volume prune -a`.

Remove everything, including running containers:

1. Stop all containers: `docker stop $(docker ps -aq)`
2. Remove all containers: `docker rm -f $(docker ps -aq)`
3. Remove all images: `docker rmi -f $(docker images -aq)`
4. Remove all volumes: `docker volume rm $(docker volume ls -q)`
5. Remove build cache: `docker builder prune -a -f`

If a list is empty, the command prints a usage error. This is safe to ignore.

Check the result with `docker system df`. This shows how much space Docker still uses.

If you want to keep some data, use narrower commands:
- `docker container prune` removes stopped containers only.
- `docker image prune -a` removes unused images only.
- `docker volume prune` removes unused volumes only.

On Docker Desktop for Mac or Windows, the disk file can stay large after a prune. Use the Docker Desktop "Clean / Purge data" option, or reduce the disk image size in Settings, to return the space to your host.
