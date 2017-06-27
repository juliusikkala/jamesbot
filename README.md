# JamesBot

JamesBot is a Telegram bot that listens to all of the chat messages, stores a
history of the messages to disk and does stuff with the intel it has gathered.

Right now, it doesn't do anything but log all messages.

## Features

- [ ] Impersonation (generating messages with a markov chain)
- [ ] Reporting (forward messages to authenticated clients)
- [ ] One-liners (respond with relevant one-liners)

## Usage

``` bash
$ ./jamesbot.py [config.cfg]
```

If no configuration file has been defined, the following locations will be
searched:

* ./jamesbot.cfg
* ~/.config/jamesbot.cfg
* /etc/jamesbot.cfg

Note that no configuration file is generated automatically; you will have to
create it yourself. Take a look at the supplied jamesbot.cfg for a template.

## Authors

- [juliusikkala][link-author]

## License

The version 3 of the GNU General Public License. Please see
[License File](COPYING) for more information.
