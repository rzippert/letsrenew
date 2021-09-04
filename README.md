# letsrenew

letsrenew is a python script that is able to retrieve a certificate from a host, identify some of its basic information and most importantly, verify how long it will still be valid. It is useful to actively monitor for automatic renewal failures in your infrastructure, even if you need to check multiple layers of SSL termination (you can request a specific host from an arbitrary address, as well as query custom ports).

## requirements

Probably ''python3-openssl'' should be installed on your system. The provided binary has everything bundled.
To use the build script you need ''pyinstaller'' and ''fpm''.

## instructions

The provided ''build.sh'' script should give you both a binary version as well as a debian package inside a ''dist'' directory.

## usage
```
usage: letsrenew [-h] [-a ADDRESS] [-p PORT] [-j] [-l ALERT] hostname

Actively tracks short lived certificates (like those from Let's Encrypt) for renewal failures.

positional arguments:
  hostname              Hostname that will be requested from the webserver.

optional arguments:
  -h, --help            show this help message and exit
  -a ADDRESS, --address ADDRESS
                        Alternate address to connect (don't resolve the hostname).
  -p PORT, --port PORT  Alternate port to connect to.
  -j, --json            Output in JSON fromat.
  -l ALERT, --alert ALERT
                        Output only on alerts. Specify it as the validity threshold in days. 0 for
                        Always output (default).

Author: Renato Zippert
```

## massrenew

With this script you can monitor multiple certificates easily and customize your report. I'm providing here an example of a very simple script that will check if the remaining validity of the certs is 29 days or lower (a time when it typically should have been renewed in Let's Encrypt terms). This way you can detect the failure quickly and act on it:

```
#!/bin/bash

function checktotelegram () {
	CHECKRESULT="$(letsrenew $@)"
	if [[ "$(echo $CHECKRESULT | wc -l)" -ne 0 ]]
	then
		echo $CHECKRESULT | telegram-send --stdin
	fi
}

checktotelegram "example.com" -a "10.0.0.1" -l 29
checktotelegram "ex.example.com" -a "10.0.0.1" -l 29
checktotelegram "another.com" -a "somethingelse.com" -l 29
checktotelegram "wikipedia.org" -l 29
checktotelegram "eff.org" -l 29
checktotelegram "acme.sh" -l 29
checktotelegram "letsencrypt.org" -l 29
```

## licence

Copyright (C) 2021 Renato Rodrigues Zippert

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/>.
