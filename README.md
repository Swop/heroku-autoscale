# heroku-autoscale


## An autoscaling python script for Heroku
This python daemon use [Heroku official python API](https://github.com/heroku/heroku.py) and [Pingdom API](http://pingdom.com/services/api/) to automatically scale your Heroku app depending on the dyno's load.

**You first need to install Heroku API before playing with this script.**

---
### First: Install dependencies
#### Heroku API
Follow the instructions from the [Heroku official python API GitHub page](https://github.com/heroku/heroku.py) to install Heroku library.

The idea is to use Python's PIP to enable the lib in the whole system :

	sudo apt-get install python-pip
	sudo pip install heroku

#### Gnuplot & SimpleJSON
In order to use Pingdom API and to plot graphs, heroku-autoscale needs `python-simplejson` and `python-gnuplot`:

	sudo apt-get install python-simplejson python-gnuplot

---
### Then: Configuring & using heroku-autoscale
Heroku-autoscale was created as a standalone daemon. It just scale your app automatically, depending on the parameters you set and the performance of your app facing the traffic.

#### Edit your config.ini file
The daemon will autoscale your app depending on some parameters you can tweak in a `config.ini` file (you can copy the sample file `config.sample.ini` and fill it with your parameters).

First, copy the sample file into /etc:

	sudo mkdir -p /etc/heroku-autoscale/
	sudo cp ./config.sample.ini /etc/heroku-autoscale/config.ini

Then, edit your config file and fill it with yout parameters :

	sudo vim /etc/heroku-autoscale/config.ini


	[HEROKU_INFOS]
	api_key: MY_HEROKU_API_KEY
	app_name: MY_APP_NAME
	
	[PINGDOM_INFOS]
	api_key: MY_PINGDOM_API_KEY
	login: MY_PINGDOM_LOGIN
	password: MY_PINGDOM_PASSWORD
	check_id: MY_PINGDOM_CHECK_ID
	
	[AUTOSCALE_SETTINGS]
	min_dynos: 1
	max_dynos: 10
	response_time_low: 500
	response_time_high: 2000
	check_frequency: 5
	pingdom_check_period: 30
	response_time_trend_low: 0.5
	response_time_trend_high: 0.5
	plot: False
	graphs_folder: /tmp
	debug: False

**Heroku parameters:**

* `api_key`: Your Heroku API key
* `app_name`: The name of the Heroku application you want to auto-scale

**Pingdom parameters:**

* `api_key`: Your Pingdom API key
* `login`: Your Pingdom login (aka your email)
* `password`: Your Pingdom password
* `check_id`: The ID of the Pingdom check which monitor your application

**Autoscale parameters:**

* `min_dynos`: The autoscale app will not scale down the Heroku app under that number of dynos
* `man_dynos`: The autoscale app will not scale up the Heroku app over that number of dynos
* `response_time_low`: If the measured response time is below this number, the Heroku app will be scaled up
* `response_time_high`: If the measured response time is over this number, the Heroku app will be scaled down
* `check_frequency`: The check frequency
* `pingdom_check_period`: The period of time you want to use from Pingdom website
* `response_time_trend_low`: If the measured response time is between the `response_time_low` and the `response_time_high` bounds, the app will loose a dyno if the the coeficent of the linear regression model is under this value
* `response_time_trend_high`: If the measured response time is between the `response_time_low` and the `response_time_high` bounds, the app will gain a dyno if the the coeficent of the linear regression model is over this value
* `plot`: If enabled, each autoscale step will plot a graph with the response times, the average response time, the response time bounds and the linear regression model of the scatter graph
* `graphs_folder`: The destination of the plotted graphs
* `debug`: The Heroku app will not be scaleid but the scaling decisions will be made and logged (and eventually the graphs will be plotted). You must have installed `python-gnuplot` to use this feature

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
**Just don't forget to monitor your website…** Even if I do my best to make this script working, you should keep an eye on the performance of your app, and take control if needed before your app crash due to an auto-scaling error…

---
Have fun!

[**Swop**](https://github.com/Swop)
