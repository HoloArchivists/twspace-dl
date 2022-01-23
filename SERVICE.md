## Service

There's an example service file [there](https://github.com/Ryu1845/twspace-dl/blob/main/twspace-dl@.service)
You'll have to modify different stuff depending on how you installed or not the script.

I'd be very grateful if someone made a PR with a bash script automating those ;)

### Cloned Repository

In that case, you'll have to modify the `WorkingDirectory` to where you cloned the repo.

### Pip

1. Change `WorkingDirectory` to where you want the spaces to be downloaded.
2. Find where your executable is by running `which twspace_dl` in your terminal.
3. Change the `/usr/bin/python twspace_dl` part to the path of your executable.

Now to install the service, you can either install it as a user service(recommended if on your personal desktop), or as a normal service.

### User

1. Copy the file you modified earlier to `~/.config/systemd/user`(create the systemd directory if it doesn't exist).
2. run

``` bash
systemctl --user daemon-reload
systemctl --user start twspace-dl@USER_ID.service
```

`USER_ID` is the part after `https://twitter.com/` in the url of a twitter profile (i.e `https://twitter.com/USER_ID`)

To keep it working after restarts run:

``` bash
systemctl --user enable twspace-dl@USER_ID.service
```

### System

1. Copy the file you modified earlier to `/etc/systemd/system`.
2. run

``` bash
sudo systemctl daemon-reload
sudo systemctl start twspace-dl@USER_ID.service
```

`USER_ID` is the part after `https://twitter.com/` in the url of a twitter profile (i.e `https://twitter.com/USER_ID`)

To keep it working after restarts run:

``` bash
sudo systemctl enable twspace-dl@USER_ID.service
```
