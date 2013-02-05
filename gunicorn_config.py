# see http://gunicorn.org/configure.html                                                                                                                                          

import os
#import multiprocessing                                                                                                                                                           

__pwd = os.path.abspath(__file__)


# Serving                                                                                                                                                                         

# This needs to be high (>10) in order to support multiple stats calls                                                                                                            
# from the browser                                                                                                                                                                
workers = 5 #multiprocessing.cpu_count() * 2 + 1                                                                                                                                 
timeout = 120
bind = "127.0.0.1:5008"

# Logging                                                                                                                                                                         

loglevel = 'debug'
