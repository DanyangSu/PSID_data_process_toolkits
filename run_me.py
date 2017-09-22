# -*- coding: utf-8 -*-
import imp
import my_PSID_class
from my_PSID_class import mortgage_pd
from my_PSID_class import mortgage_data
imp.reload(my_PSID_class)

#Set path
my_out_path = 'E:\\python_proj\\out' #set output dir
my_in_path = 'E:\\prthon_proj\\in' #set input dir

#Generate data
my_mortgage = mortgage_data(in_path=my_in_path)
my_mortgage.mortgage_init()
my_data = mortgage_pd(my_mortgage.merge_data.copy())
my_data_insti = mortgage_pd(my_mortgage.insti_data.copy())

#Qualify check
outlier_index = my_data.check_outlier(['mortgage_in_thousands','family_income'])
missing_index = my_data.check_missing(['mortgage_in_thousands','family_income', \
                                       'State_ID','County_Code','State','County', \
                                       'App_ID','Employer_ID', 'SSN_deidentified', 'Year_Mortgage'])
my_data.sum_stats(['mortgage_in_thousands','family_income'])
dup_data = my_data.check_unique(['App_ID','Employer_ID', 'SSN_deidentified', 'Year_Mortgage'])
outlier_index_county = my_data.check_outlier(['mortgage_in_thousands','family_income'],category=['State_County'])

#Visual
my_data.my_subplot(horiz='Year_Mortgage',verti='State',super_title='Mortgage across States between 1968-2013',out_path='',var_investigate='mortgage_in_thousands')

