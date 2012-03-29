# heroku-autoscale


## An autoscaling python script for Heorku
This python daemon use [Heroku official python API](https://github.com/heroku/heroku.py) and [New Relic API](http://newrelic.com/) to automatically scale your Heroku app depending on the dinho's load.

**You first need to install Heroku API before playing with this script.**

---
### First: Install heroku API
Follow the instruction from the [Heroku official python API GitHub page](https://github.com/heroku/heroku.py) to install Heroku library.

The idea is to use Python's PIP to enable the lib in the whole system.

---
### Then: Configuring & using heroku-autoscale
Heroku-autoscale was created as a standalone daemon. It just scale your app automatically, depending on the parameters you set and the performance of your app facing the traffic.

#### Edit your config.ini file
The daemon will autoscale your app depending on some parameters you can tweak in a `config.ini` file (you can copy the sample file `config.sample.ini` and fill it with your parameters) :

	[HEROKU_INFOS]
	api_key: MY_HEROKY_API_KEY
	app_name: MY_APP_NAME
	
	[NEWRELIC_INFOS]
	api_key: MY_NEWRELIC_API_KEY
	account_id: MY_NEWRELIC_ACCOUNT_ID
	app_id: MY_NEWRELIC_APP_ID
	
	[AUTOSCALE_SETTINGS]
	min_dynos: 1
	max_dynos: 10
	apdex_low: 0.5
	apdex_high: 0.8
	check_frequency: 5

**Heroku parameters:**

* `api_key`: Your Heroku API key
* `app_name`: The name of the Heroku application you want to auto-scale

**New Relic parameters:**

* `api_key`: Your New Relic API key
* `account_id`: Your New Relic account ID
* `app_id`: The ID of the New Relic App you want to supervise

**Autoscale parameters:**

* `min_dynos`: The autoscale app will not scale down the Heroku app under that number of dynos
* `man_dynos`: The autoscale app will not scale up the Heroku app over that number of dynos
* `apdex_low`: If the measured apdex score is below this number, the Heroku app will be scaled up
* `apdex_high`: If the measured apdex score is over this number, the Heroku app will be scaled down
* `check_frequency`: The check frequency

#### *Optional* - Edit and install the daemon init.d script
This script was designed to be used as a daemon. You must want to have an `init.d` script to manage the daemon.

An `init.d` script had allready been written for you: `heroku-autoscale`

Start by editing this file and change the path of the daemon script:

	[...]
	# !! CHANGE THIS LINE WITH YOUR REAL DEAMON'S PATH !!
	DAEMON_EXEC="/home/sylvain/Projets/Heroku/heroku-autoscale/HerokuAutoscaleDaemon.py"
	[...]

And then, copy the script into the `init.d` folder:

	root# cp heroku-autoscale /etc/init.d
---
### Finally: Let's have some fun!
Launch heroku-autoscale, forget about manually scale your app!

**If you have installed the init.d script:**

	root# /etc/init.d/heroku-autoscale start
**Or if you wanna use the python script directly:**

	root# python HerokuAutoscaleDaemon.py

You can tweak some parameters, like the UID, GID, logfiles... by adding some args the the command. Type `python HerokuAutoscaleDaemon.py --help` to know how to use it.

---
**Just don't forget to monitor your website…** Even if I do my best to make this script work, you should keep an eye to the performance of your app, and take control if needed before your app crash due to an auto-scaling error…

---
Have fun!

[**Swop**](https://github.com/Swop)