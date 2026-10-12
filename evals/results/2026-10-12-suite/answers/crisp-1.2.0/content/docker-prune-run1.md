Run `docker system prune -a --volumes -f` to remove all unused images, containers, networks, and volumes.

This command deletes data and you cannot undo it. Volumes can hold databases and other data you need. Check what exists first with `docker volume ls`.

Note that `prune` only removes unused items. It skips running containers and the images and volumes they use. To remove everything, stop and delete all containers first.

**Full wipe, step by step**

1. Stop all running containers:
   ```bash
   docker stop $(docker ps -aq)
   ```
2. Remove all containers:
   ```bash
   docker rm $(docker ps -aq)
   ```
3. Remove all images:
   ```bash
   docker rmi -f $(docker images -aq)
   ```
4. Remove all volumes:
   ```bash
   docker volume rm $(docker volume ls -q)
   ```
5. Remove the build cache and unused networks:
   ```bash
   docker builder prune -a -f
   docker network prune -f
   ```

If a list is empty, the command prints a usage error. This is harmless, so skip that step.

**Safer options**

- Remove only stopped containers, dangling images, and unused networks: `docker system prune`
- Remove only dangling images (untagged layers): `docker image prune`
- Remove only unused volumes: `docker volume prune`

**Check the result**

Run `docker system df` before and after. It shows how much space images, containers, volumes, and build cache use.

On Docker Desktop for Mac or Windows, the disk image file may not shrink after cleanup. Use the Docker Desktop troubleshooting or disk settings to reclaim the space.
