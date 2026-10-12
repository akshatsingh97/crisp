Run `docker system prune -a --volumes` to remove all unused images, containers, networks, and volumes. This command cannot be undone. It deletes data in volumes, such as databases.

Docker removes only unused items. A running container keeps its image, and its volumes stay.

To remove everything, including running containers, follow these steps:

1. Stop all containers: `docker stop $(docker ps -aq)`
2. Remove all containers: `docker rm $(docker ps -aq)`
3. Remove all images: `docker rmi -f $(docker images -aq)`
4. Remove all volumes: `docker volume rm $(docker volume ls -q)`
5. Remove the build cache: `docker builder prune -a -f`

Before you run these commands, check what will go. Use `docker ps -a`, `docker images`, and `docker volume ls`. Back up any volume that holds data you need.

To check how much space Docker uses, run `docker system df`.
