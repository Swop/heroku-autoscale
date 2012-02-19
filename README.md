# heroku-autoscale


## An autoscaling python script for Heorku
This script use [Heroku official python API](https://github.com/heroku/heroku.py) to automatically scale your Heroku app depending on the dinho's load.

**You first need to install Heroku API before playing with this script.**

---
### First: Install heroku API
Follow the instruction from the [Heroku official python API GitHub page](https://github.com/heroku/heroku.py) to install Heroku library.

The idea is to use Python's PIP to enable the lib in the whole system.

### Then: Configuring & using heroku-autoscale
Heroku-autoscale was created as a non-standalone library. It just scale your app on demand, depending on the parameters you set and just for one time.

If you plan to autoscale your app without any human intervention (by using a CRON job for example), just call the autoscalling function inside an infinite loop.

    import time
    while(True):
        herokuapp.autoscale()
        time.sleep(5)


### Finally: Let's have some fun!
Launch heroku-autoscale, forget about manually scale your app!

**Just don't forget to monitor your website…** Even if I do my best to make this script work, you should keep an eye to the performance of your app, and take control if needed before your app crash due to an auto-scaling error…

---
Have fun!

[**Swop**](https://github.com/Swop)