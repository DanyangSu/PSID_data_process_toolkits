# -*- coding: utf-8 -*-

import pandas as pd
import re
import numpy as np
from tabulate import tabulate
import matplotlib.pyplot as plt



"""
Extend pd.DataFrame class.
"""
class mortgage_pd(pd.DataFrame):
    
    """
    Scans the data and set any string that match the regular expression pattern
    By default, it sets as empty string cells that contains only NA, NAN, N/A, and whitespces (case insensitive)
    IN:
        regex_string = '': user defined regular expression. Should begin with '|^' and end with '$'
    OUT:
        mortgage_pd DataFrame type
    """
    def set_missing(self,regex_string = ''):
        regex_str = '^ *NAN? *$|^ *n/a *$' + regex_string
        na_pattern = re.compile(regex_str,re.I)
        regex_na = lambda x: na_pattern.sub('',str(x))
        return mortgage_pd(self.applymap(regex_na))
        
    
    """
    Classify Mortgages based on income-to-loan ratio.
    OUT:
        out_cat: pd.Series of categorical values    
    """
    def set_category(self):
        inc_loan_ratio = self.mortgage_in_thousands/self.family_income
        med = inc_loan_ratio.median()
        null_input = inc_loan_ratio.isnull()
        flag_risky = (inc_loan_ratio<=med) & ~null_input
        flag_secure = (inc_loan_ratio>med) & ~null_input
        out_cat = pd.Series(['' for i in range(len(inc_loan_ratio))])
        out_cat[null_input] = 'NA'
        out_cat[flag_risky] = 'Risky' 
        out_cat[flag_secure] = 'Secure'
        return out_cat
        
       
    """
    Convert columns specified by var_list to numeric.
    If columns contain non-numeric values, raise exception
    IN:
        var_list: list of strings. Must be column name of the DataFrame object
    MODIFY:
        Change data types of columns to numeric
    """
    def type_num(self,var_list=[]):
        for i in var_list:
            self[i] = pd.to_numeric(self[i])
        
    
    """
    Calculate the relative absolute deviation from median in a series. 
    IN:
        series: numeric column of the data
    OUT:
        flag: pd.Series that takes -1 if outlier, 1 if regular, np.nan if missing
    """
    def MAD(self,series):
        med = series.median()
        mad = abs(series-med).median()
        if mad>0.1:
            score = abs(series-med)/mad
            cut_off_flag = score>np.nanpercentile(score,99)
        else:
            cut_off_flag = abs(series-med)>1
        flag = cut_off_flag*-1
        flag[~cut_off_flag] = 1
        flag[series.isnull()] = np.nan
        return flag
        
      
    """
    Call MAD function. For each numeric column specifed in the var_list, check for outliers.
    Allows for category-by-category check (e.g. find outliers for each county).
    IN:
        var_list: list of strings. Must be column name of the DataFrame object
        method='MAD': method to be used. Currently only support the method defined by the MAD function
        flag_add_col = False: add columns to the self object if True
        category = None: list of strings. Must be column name of the DataFrame object. Used for category-by-category check.
    OUT:
        out_dict: dictionary. column names specificed in var_list with the associated row index of the outliers
    MODIFY:
        If flag_add_col = True, add columns to the self object for each column name specified in the var_list.
        Naming rule is variable names + '_' + method names (e.g. mortgage_in_thousands_MAD).
    """
    def check_outlier(self,var_list,method='MAD',flag_add_col = False, category = None):
        out_dict = dict()
        print_mat = []       
        for i in var_list:
            if method == 'MAD':
                if category == None:
                    out_lier = self.MAD(self[i])
                else:
                    group_series = self.groupby(category)[i]
                    group_func = lambda col: self.MAD(col)
                    out_lier = group_series.transform(group_func)
            else:
                raise NameError('Wrong Algorithm')
            if flag_add_col:
                self[i+'_'+method] = out_lier
            out_dict[i+'_'+method] = self.index[out_lier==-1] 
            print_mat.append([sum(out_lier==-1)/(sum(out_lier==1)+sum(out_lier==-1))*100])
        print(tabulate(zip(var_list,print_mat),headers = ['Columns','Outlier Percentage']))
        return out_dict
        
    
    """
    Check missingness of columns as specified by var_list. Display percentage of missing entries.
    IN:
        var_list: list of strings. Must be column name of the DataFrame object
    OUT:
        out_dict: dictionary. column names specificed in var_list with the associated row index of missing values
    """
    def check_missing(self,var_list):
        out_dict = dict()
        print_mat = []
        for i in var_list:
            null_var = self[i].isnull()
            out_dict[i] = self.index[null_var]
            print_mat.append([sum(null_var)/len(null_var)*100])
        print(tabulate(zip(var_list,print_mat),headers = ['Columns','Missing Percentage']))
        return out_dict
        
     
    """
    Check whether the data is uniquely identified by the list of columns specified in var_list.
    Display Duplicated Percentage as percentage of duplicated rows in the data.
    Display Unique Duplicated Percentage as percentage of unique duplicated entries of all unique entries.
    IN:
        var_list: list of strings. Must be column name of the DataFrame object
        keep_flag=True: if False, drops duplicates from self except for the first instance.
    OUT:
        out_data: mortgage_pd Dataframe with duplicated rows.
    MODIFY:
        Drops duplicates from self except for the first instance if keep_flag=True
    """
    def check_unique(self,var_list=None, keep_flag=True):
        if var_list == None:
            var_list = list(self.columns.values)
        flag_duplicate = self.duplicated(subset=var_list,keep=False)
        flag_unique_duplicate = self.duplicated(subset=var_list,keep='first')
        total_unique = len(flag_duplicate)-sum(flag_unique_duplicate)
        num_unique_duplicate = sum(flag_duplicate) - sum(flag_unique_duplicate)
        print_mat = [sum(flag_duplicate)/len(flag_duplicate)*100,num_unique_duplicate/total_unique*100]
        if len(var_list) == len(list(self.columns.values)):
            print_list = ['All Variables']
        else:
            print_list = var_list
        print('Identifier:'+','.join(print_list))
        print(tabulate([['Duplicate Percentage','Unique Duplicate Percentage'],print_mat]))
        out_data = mortgage_pd(self[flag_duplicate].copy())
        if keep_flag==False:
            print(keep_flag)
            self.drop_duplicates(subset = var_list,keep='first',inplace=True)
        return out_data
    

    """
    Display summary statistics of variables listed in var_list
    IN:
        var_list: list of strings. Must be column name of the DataFrame object
    """
    def sum_stats(self,var_list):
        print_mat = []
        for i in var_list:
            print_mat.append([i,self[i].mean(),self[i].std(),self[i].median(),self[i].min(),self[i].max()])
        print(tabulate(print_mat,headers = ['Columns','Mean','Std.','Median', 'Min','Max']))        

        
    """
    Plot the bar chart from the numeric data series by groups
    IN:
        var_name: variable name being studied. Must be numeric (e.g. mortgage_in_thousands)
        group_verti: category along the Y-axis
        group_horiz: category along the X-axis
        title=None: title string
        top_n=10: in case there are too many categories, pick only the top n, and sum the rest as others. Default value is 10 (Note it also performs summation if we use mean of median)
        other_var=True: if true, and the number of categories is greater than top_n, include the 'Other' group in the plot
        axis=None: used to position the plot in the subplot
        legend_on=False: show legend if True
        wid=0.6: width of the plot
        figs=(7,5): figsize of the plot
        stack=True: True if bars stack in bar chart
        dic=None: import user defined index to ensure uniform ordering across different plots
    OUT:
        temp_plot: plot handle
        out_dic: export orded index as user defined index 
    """
    def my_plot(self,var_name,group_verti,group_horiz,method='sum',title=None,top_n=10,other_var=True,axis=None,legend_on=False,wid=0.6,figs=(7,5),stack=True,dic=None):
        group_list = [group_verti,group_horiz]
        if method == 'sum':
            var_by_group = self.groupby(group_list)[var_name].sum()
        elif method == 'count':
            var_by_group = self.groupby(group_list)[var_name].count()
        elif method == 'median':
            var_by_group = self.groupby(group_list)[var_name].median()
        elif method == 'mean':
            var_by_group = self.groupby(group_list)[var_name].mean()      
        else:
            raise NameError('Wrong Method')
        var_by_group = var_by_group.unstack(level=1) #convert to matrix to be plotted
        top_n = min(top_n,len(var_by_group))
        var_by_group['total'] = var_by_group.sum(axis=1) #used for ordering
        if dic==None:
            var_by_group.sort_values(by='total',ascending=False,inplace=True)
            sorter = list(var_by_group.index)
            out_dic = dict(zip(sorter,range(len(sorter))))
            out_dic['Other'] = len(sorter)
        else:
            var_by_group['custom_index'] = list(var_by_group.index) #used to map user defined ordering
            var_by_group['custom_rank'] = var_by_group.custom_index.map(dic)
            var_by_group.sort_values(by='custom_rank',ascending=True,inplace=True)
            var_by_group.drop(['custom_rank','custom_index'],axis=1,inplace=True)
            out_dic = dic           
        remain_group = var_by_group.tail(len(var_by_group) - top_n)
        remain_total = remain_group.sum(axis=0)
        out_group = var_by_group.head(top_n).copy()
        if len(remain_group)>0 and other_var: #if the Other group is needed
            out_group.loc['Other'] = remain_total 
        out_group = out_group.drop(['total'],axis=1).transpose()   
        temp_plot = out_group.plot(ax=axis,kind='bar',stacked=stack,colormap='Paired',width=wid,figsize=figs,legend=legend_on)
        if legend_on:
            temp_plot.legend(loc='center left',bbox_to_anchor=(1,0.5),fontsize='small')
        temp_plot.set_xlabel(str.upper(group_horiz))
        temp_plot.set_ylabel(str.upper(method))
        if title != None:
            temp_plot.set_title(str(title))
            temp_plot.title.set_position([0.5,1.05])
        return temp_plot,out_dic
                
     
    """
    Call my_plot. Generate 2 by 2 subplots.
    IN:
        verti: category along the Y-axis
        horiz: category along the X-axis 
        super_title: the overall title of the plot
        out_path='': export path for the plot
    EXPORT:
        f: plot
    """
    def my_subplot(self,horiz,verti,super_title,out_path='',var_investigate='mortgage_in_thousands'):
        f,axes = plt.subplots(nrows=2,ncols=2,figsize=(20,20))
        _,in_dic = self.my_plot(var_investigate,group_horiz=horiz,group_verti=verti, \
                                method='sum',top_n=10,title='Total in Thousands',other_var=True,axis=axes[0,0],legend_on=False)
        self.my_plot(var_investigate,group_horiz=horiz,group_verti=verti, \
                                method='sum',top_n=10,title='Total in Thousands Top Categories',other_var=False,axis=axes[0,1],legend_on=True,dic=in_dic)
        self.my_plot(var_investigate,group_horiz=horiz,group_verti=verti, \
                                method='count',top_n=10,title='Total Incidence',other_var=False,axis=axes[1,0],legend_on=False,dic=in_dic)
        self.my_plot(var_investigate,group_horiz=horiz,group_verti=verti, \
                                method='mean',top_n=10,title='Median in Thousands',other_var=False,axis=axes[1,1],legend_on=False,stack=False,dic=in_dic)
        f.set_figheight(8)
        f.set_figwidth(10)
        f.subplots_adjust(wspace=0.3,hspace=0.5)
        f.suptitle(super_title,fontsize='large')
        if out_path=='':
            f.savefig('{}.png'.format(super_title),bbox_inches='tight')    
        else:
            f.savefig('{}\\{}.png'.format(out_path,super_title),bbox_inches='tight')
        
     

        
            

"""
Generate data for analysis
"""
class mortgage_data(object):
    
    """
    Read the loan data and the institution data.
    IN:
        in_path='': directory of data
    MODIFY:
        Add self.loan_data and self.insti_data attributes
    """
    def __init__(self,in_path=''):
        path_str = ''
        if in_path != '':
            path_str = in_path + '\\'
        self.ind_data = mortgage_pd(pd.read_csv(path_str+"PSID_1968_2013_Individual.csv",low_memory=False,skipinitialspace=True,keep_default_na=False))
        self.fam_data = mortgage_pd(pd.read_csv(path_str+"PSID_1968_2013_family.csv",low_memory=False,skipinitialspace=True,keep_default_na=False))
        
        
    """
    Generate merge_data.
    """
    def mortgage_init(self):
        merge_data = mortgage_pd(pd.merge(self.ind_data,self.fam_data,how='left',on=['As_of_Year','Agency_Code','Respondent_ID']))
        self.merge_data = merge_data.set_missing()
        numeric_list = ['family_income','mortgage_in_thousands','Number_of_People','Total_Family_Debt','Welfare_Receipt']    
        self.merge_data.type_num(numeric_list)
        self.merge_data['mortgage_type'] = self.merge_data.set_category()
    