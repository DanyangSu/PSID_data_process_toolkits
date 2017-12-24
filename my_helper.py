#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os.path
import os
import urllib.request as request
import sys

"""
This is my general utility class
"""
class utility(object):
    
    """
    Initialization
    """
    def __init__(self):
        pass
    
    
    """
    Download files from the internet. By default, the file will be downloaded 
    to the cwd, and will have the same name
    IN:
        download_dir: target dir, by default is cwd
        file_name: target file name, by default is the same name
        url: source file link
    NOTE:
        Contains a nested function called reporthook
    """
    @staticmethod
    def download(url,download_dir=os.getcwd(),file_name=None):
        
        
        """
        Nested fucntion of download: Display progress bar
        IN: 
            blocknum: current number of file blocks downloaded
            blocksize: size of each block
            totalsize: total size of the file
        """
        def reporthook(blocknum,blocksize,totalsize):
            readsofar = blocknum * blocksize
            if totalsize > 0:
                percent = readsofar * 1e2 / totalsize
                s = "\r%5.1f%% %*d / %d" % (
                    percent, len(str(totalsize)), readsofar, totalsize)
                sys.stdout.write(s)
                if readsofar >= totalsize: # near the end
                    sys.stdout.write("\n")
                    print("File downloaded")
            else: # total size is unknown
                sys.stderr.write("read %d\n" % (readsofar,))
                
                
        print("Begin file downloading...")
        if file_name==None:
            file_name = url.rsplit('/',1)[-1]
        request.urlretrieve(url,os.path.join(download_dir,file_name),reporthook)
        