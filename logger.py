"""Define the Logger class.

This class allows to create objects that would be used as standard
and error output. Behind it are files so the message writen in it
will be writen in a file.

"""

from datetime import datetime

class Logger:
    
    """Represent a logger, meaning an object in which you can write.
    
    Attributes:
        path -- files's path to write
        file -- the file object
    
    Methods:
        write -- write in the file object
    
    Properties:
        now -- return the formated date and time
    
    """
    
    def __init__(self, path):
        self.path = path
        self.file = open(self.path, "a")
        self.__nl = True
    
    def write(self, message):
        """Write in the file."""
        if self.__nl:
            now = self.now
            self.file.write(now + " ")
        self.file.write(message)
        self.file.flush()
        
        self.__nl = message.endswith("\n")
    
    @property
    def now(self):
        """Return the date and time."""
        now = datetime.now()
        ret = "{0}-{1:02}-{2:02} {3:02}:{4:02}:{5:02}".format(
                now.year, now.month, now.day, now.hour, now.minute, now.second)
        return ret
    
    def flush(self):
        """Flush the file."""
        self.file.flush()

