Run `docker system prune -a --volumes` to remove all unused images, stopped containers, networks, and volumes.

This command permanently deletes data. Volume data cannot be recovered. Back up any volume that holds a database or other important files first.

The command only removes containers that are stopped. It also keeps images that a running container uses. To remove everything, stop all containers first.

1. Stop all containers: `docker stop $(docker ps -aq)`
2. Remove everything unused: `docker system prune -a --volumes -f`
3. Remove the build cache: `docker builder prune -a -f`
4. Check the result: `docker system df`

The `-f` flag skips the confirmation prompt. Leave it out if you want to confirm first.

If named volumes remain, run `docker volume prune -a -f`. Docker 23 and later remove only anonymous volumes (volumes with no name) with `--volumes`. Older versions remove all unused volumes.

To delete each type separately, use these commands:

```
docker rm -f $(docker ps -aq)
docker rmi -f $(docker images -aq)
docker volume rm $(docker volume ls -q)
```

If a command prints "requires at least 1 argument", that list is empty. Nothing of that type exists, so skip the command.

On Docker Desktop for Mac or Windows, the disk image file can stay large after cleanup. Use the Troubleshoot menu and select "Clean / Purge data" to reset it. You can also reduce the disk image size in Settings under Resources.
