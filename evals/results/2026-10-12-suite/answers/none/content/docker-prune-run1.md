Run this command:

```
docker system prune -a --volumes
```

It deletes all stopped containers, all unused networks, all images not used by a container, all build cache, and all unused volumes. Docker asks you to confirm first. Add `-f` to skip the question.

**Warning:** Volume data is lost for good. Back up any database or other data you want to keep before you run it.

**Running containers are not removed.** To remove them too, stop and delete everything first:

```
docker stop $(docker ps -q)
docker rm -f $(docker ps -aq)
docker system prune -a --volumes -f
```

On recent Docker versions, `--volumes` removes only anonymous volumes by default. Add `--filter` or run `docker volume prune -a` to remove named volumes too.

To remove each type on its own:

```
docker container prune
docker image prune -a
docker volume prune -a
docker builder prune -a
```

Check how much space Docker uses before and after:

```
docker system df
```

If the disk is still full on Docker Desktop (Mac or Windows), the virtual disk file may not shrink. Use the Docker Desktop setting "Clean / Purge data" or lower the disk image size.
