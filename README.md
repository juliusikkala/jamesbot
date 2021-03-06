# JamesBot

JamesBot is a Telegram bot that wiretaps your channel, stores a history of the
messages to disk and does stuff with the intel it has gathered.

Note that this JamesBot is not related to the @JamesBot bot on Telegram.

Right now, it doesn't do anything but log all messages.

## Features

- [x] Impersonation (generating messages with a markov chain)
- [x] Smalltalk (sends generated messages on its own)
- [ ] Reporting (forward messages to authenticated clients)
- [ ] One-liners (respond with relevant one-liners)

## Usage

``` bash
$ ./jamesbot/main.py [config.cfg]
```

If no configuration file has been defined, the following locations will be
searched:

* ./jamesbot.cfg
* ~/.config/jamesbot.cfg
* /etc/jamesbot.cfg

Note that no configuration file is generated automatically; you will have to
create it yourself. Take a look at the supplied jamesbot.cfg for a template.

In every chat JamesBot is in, you will have to enable some features separately
if you want them. To enable recording, type `/recording start`. To enable
smalltalk, type `/smalltalk start`. If you want to stop them, replace `start`
with `stop`.

## Authors

- [Julius Ikkala](https://github.com/juliusikkala)

## License

The version 3 of the GNU General Public License. Please see
[License File](COPYING) for more information.
