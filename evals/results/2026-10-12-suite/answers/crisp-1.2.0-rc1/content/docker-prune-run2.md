Run `docker system prune -a --volumes` to remove all unused Docker data. It keeps running containers and the images and volumes they use. This command deletes data that you cannot recover.

## Quick cleanup

1. Check current disk use:

   ```bash
   docker system df
   ```

2. Remove unused data:

   ```bash
   docker system prune -a --volumes
   ```

3. Type `y` when Docker asks for confirmation. Add `-f` to skip the prompt.

This command removes:
- All stopped containers
- All unused networks
- All images that no running container uses
- All build cache
- All unused volumes

On Docker 23 or later, `--volumes` may remove only anonymous volumes (volumes with no name). To remove unused named volumes too, run `docker volume prune -a`.

## Full wipe, including running containers

Warning: these commands stop and delete every container. Every volume loses its data. Back up any database or upload data first.

```bash
docker stop $(docker ps -aq)
docker rm -f $(docker ps -aq)
docker rmi -f $(docker images -aq)
docker volume rm $(docker volume ls -q)
docker builder prune -a -f
```

If a command prints "requires at least 1 argument", that list is empty. Skip that command.

## Remove one type only

- Stopped containers: `docker container prune`
- Dangling images (untagged layers): `docker image prune`
- All unused images: `docker image prune -a`
- Unused volumes: `docker volume prune`
- Build cache: `docker builder prune -a`

## If the space does not come back

- If you use Docker Desktop on Mac or Windows, the virtual disk file does not shrink on its own. Use Settings, then Resources, then "Disk image size", or use the "Clean / Purge data" option.
- If `docker volume rm` fails with "volume is in use", a container still uses it. Remove that container first.
- If `docker rmi` fails with "image is being used", remove the container that uses that image first.
