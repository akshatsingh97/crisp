Run `docker system prune -a --volumes` to remove all unused Docker data. This deletes data that cannot be recovered. Volumes can hold databases and uploads, so back up anything you need first.

This command removes stopped containers, unused networks, unused images, build cache, and unused volumes. It keeps running containers and the images and volumes that they use.

Docker 23 and later remove only anonymous volumes with this command. To remove named volumes too, run `docker volume prune -a`.

To remove everything, including running containers, follow these steps:

1. Stop all containers: `docker stop $(docker ps -aq)`
2. Remove all containers: `docker rm -f $(docker ps -aq)`
3. Remove all images: `docker rmi -f $(docker images -aq)`
4. Remove all volumes: `docker volume rm $(docker volume ls -q)`
5. Remove the build cache: `docker builder prune -a`

If a list is empty, the command prints a usage error. This is safe to ignore.

To see how much space Docker uses before and after, run `docker system df`.

If you use Docker Desktop, the disk image file can stay large after you clean. In Docker Desktop, open Troubleshoot and select Clean / Purge data to reclaim the space.
