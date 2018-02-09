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
        
        
    @staticmethod    
    def multi_var_plot(input_df, display_vars = None, var_x_axis = None, method = 'sum', title = None, \
                       axis = None, legend_on = False, figsize = (10,10), \
                       kind = 'line', colormap = 'Paired', custom_legend = None):

        if display_vars == None:
            raise ValueError('Display variables not specified')
        if var_x_axis == None:
            raise ValueError('Variable on X axis not specified')
        #if one of the axis uses index, we need to generate that variable
        if var_x_axis == 'index_var':
            input_df['index_var'] = input_df.index    
        if method == 'sum':
            display_vars_grouped = input_df.groupby(var_x_axis)[display_vars].sum()
        elif method == 'count':
            display_vars_grouped = input_df.groupby(var_x_axis)[display_vars].count()
        elif method == 'median':
            display_vars_grouped = input_df.groupby(var_x_axis)[display_vars].median()
        elif method == 'mean':
            display_vars_grouped = input_df.groupby(var_x_axis)[display_vars].mean()      
        else:
            raise NameError('Wrong Method')

        temp_plot = display_vars_grouped.plot(ax = axis, kind = kind, colormap = colormap, \
                                   figsize = figsize, legend = legend_on, rot = 45)
        if legend_on:
            legend_ = temp_plot.legend(loc = 'center left', bbox_to_anchor = (1, 0.5), fontsize = 'small')
            if custom_legend != None:        
                for legend_index in custom_legend:
                    legend_.get_texts()[custom_legend[legend_index]].set_text(legend_index)  
        temp_plot.set_xlabel('')
        temp_plot.set_ylabel('')

        if title != None:
            temp_plot.set_title(str(title))
            temp_plot.title.set_position([0.5, 1.05])
        return temp_plot






    @staticmethod
    def generic_subplot(input_df, subplot_dim, subplot_type, subplot_spec, super_title = None, \
                          output_path = os.getcwd(), minor_locator = \
                          mdate.WeekdayLocator(byweekday=MO, interval=2), \
                          major_locator = mdate.MonthLocator(), location_empty_subplot = []):
        f,axes = plt.subplots(nrows = subplot_dim[0], ncols = subplot_dim[1], figsize = (15,10), sharex = 'all')
        max_num_plot = subplot_dim[0] * subplot_dim[1]
        if len(subplot_spec) + len(location_empty_subplot) > max_num_plot:
            raise ValueError('Capacity of subplots exceeded.')
        for locations in location_empty_subplot:
            if locations[0]>subplot_dim[0] or locations[1]>subplot_dim[1]:
                raise ValueError('location of empty subplot out side index')
            elif locations[0]<0 or locations[1]<0:
                raise ValueError('location index has to be non-negative')
        plot_counter = 0 #point to the current plot spec to plot
        empty_plot_counter = 0 #point to the current empty to skip
        for i in range(subplot_dim[0]):
            for j in range(subplot_dim[1]): 
                if plot_counter <  len(subplot_spec):
                    #check if the subplot is meant to be empty
                    if empty_plot_counter >= len(location_empty_subplot) or \
                    location_empty_subplot[empty_plot_counter] != [i,j]: 
                        axes[i,j].xaxis.set_major_locator(major_locator)
                        axes[i,j].xaxis.set_minor_locator(minor_locator)
                        plot_spec = subplot_spec[plot_counter]
                        plot_spec.update(dict(axis = axes[i,j]))
                        plot_counter += 1
                        if subplot_type == 'multi_var_plot':
                            multi_var_plot(input_df, **plot_spec)           
                        else:
                            raise ValueError('Wrong Plotting Method')
                    elif empty_plot_counter<len(location_empty_subplot):
                        empty_plot_counter += 1
                        axes[i,j].axis('off')          
        plt.tight_layout()   
        f.autofmt_xdate()
        f.set_figheight(8)
        f.set_figwidth(10)
        f.subplots_adjust(wspace=0.3,hspace=0.5)
        f.suptitle(super_title,fontsize='large')
        f.savefig('{}\{}.png'.format(output_path,super_title),bbox_inches='tight')



