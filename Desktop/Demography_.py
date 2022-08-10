import numpy as np
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt

#Load data
enroll = pd.read_csv('/Users/jinyaotian/Desktop/Enrollment.csv')

enroll.columns
enroll.head()
len(enroll)

#Select CHSNC Program data
df = enroll.loc[enroll['Tac Acad Plan'] == 'CHSNC']
df.reset_index(drop = True, inplace = True)

df.head()

# Question2: When they enrolled into a program, which course did they take first?
'''
Last Enrl Dt Stmp: Enrollment Date
Emplid: Student unique id number
Class Start Dt: official class start date, irrelevant to individual's enrollment date
'''
rank_df = df[['Emplid','Last Enrl Dt Stmp', 'Class Start Dt', 'Course', 'Course Sub Status']]

#Check data type
rank_df.info()
rank_df.head()

# change data-type
rank_df['Last Enrl Dt Stmp'] = pd.to_datetime(rank_df['Last Enrl Dt Stmp'])
rank_df['Class Start Dt'] = pd.to_datetime(rank_df['Class Start Dt'])

#Add new column to rank_df
first_course = ['Nan']*len(rank_df)
rank_df.insert(5, 'first_course', first_course, True)


# Emplid set: distinct student id, without duplicate
Id = list(set(rank_df['Emplid'].to_list()))

#Create a new dataframe, to restore: Student ID, the number of courses the student took, and their orders
dummy = ['Nan']*len(Id)
data = {'Emplid': Id, 'Num': [0]*len(Id), 'First': dummy, 'Second': dummy, 'Third': dummy,'Earliest':[None]*len(Id), 'Latest': [None]*len(Id)}
info_df = pd.DataFrame(data)
info_df.set_index('Emplid', inplace= True)

#Sort by 'Last Enrl Dt Stmp'
rank_df.sort_values(by=['Last Enrl Dt Stmp'],ascending= True, inplace = True)

for i in range(len(rank_df)):
    id = rank_df.loc[i, 'Emplid']
    if rank_df.loc[i,'Course'] not in [info_df.loc[id, 'First'], info_df.loc[id, 'Second'], info_df.loc[id, 'Third']]:
        if info_df.loc[id,'Num'] == 0:
            info_df.loc[id, 'First'] = rank_df.loc[i,'Course']
            info_df.loc[id, 'Earliest'] = rank_df.loc[i,'Last Enrl Dt Stmp']
        elif info_df.loc[id,'Num'] == 1:
            info_df.loc[id, 'Second'] = rank_df.loc[i, 'Course']
        else:
            info_df.loc[id, 'Third'] = rank_df.loc[i, 'Course']
            info_df.loc[id, 'Latest'] = rank_df.loc[i, 'Last Enrl Dt Stmp']
        info_df.loc[id, 'Num'] += 1
    else:
        continue

info_df['Earliest'] = info_df['Earliest'].astype('datetime64[ns]')
info_df['Latest'] = info_df['Latest'].astype('datetime64[ns]')
#Count
info_df.groupby(by = ['First']).count()

# to_csv
info_df.to_csv('/Users/jinyaotian/Desktop/info.csv')

'''
General Transition rate: Course1 -> Course2 -> Course3 
'''
tran_num = np.array([len(info_df),len(info_df.loc[info_df['Second'] != 'Nan']), len(info_df.loc[info_df['Third'] != 'Nan'])])
tran_ratio = np.array([1, tran_num[1]/tran_num[0], tran_num[2]/tran_num[1]])

'''
Transition rate by courses
'''
HS375_df = info_df.loc[info_df['First'] == 'HS375']

tran_num_by_cres = np.array([len(HS375_df),len(HS375_df.loc[HS375_df['Second'] != 'Nan']), len(HS375_df.loc[HS375_df['Third'] != 'Nan'])])
tran_ratio_by_cres = np.array([1, tran_num_by_cres[1]/tran_num_by_cres[0], tran_num_by_cres[2]/tran_num_by_cres[1]])


HS376_df = info_df.loc[info_df['First'] == 'HS376']

tran_num_by_cres_376 = np.array([len(HS376_df),len(HS376_df.loc[HS376_df['Second'] != 'Nan']), len(HS376_df.loc[HS376_df['Third'] != 'Nan'])])
tran_ratio_by_cres_376 = np.array([1, tran_num_by_cres_376[1]/tran_num_by_cres_376[0], tran_num_by_cres_376[2]/tran_num_by_cres_376[1]])

HS377_df = info_df.loc[info_df['First'] == 'HS377']

tran_num_by_cres_377 = np.array([len(HS377_df),len(HS377_df.loc[HS377_df['Second'] != 'Nan']), len(HS377_df.loc[HS377_df['Third'] != 'Nan'])])
tran_ratio_by_cres_377 = np.array([1, tran_num_by_cres_377[1]/tran_num_by_cres_377[0], tran_num_by_cres_377[2]/tran_num_by_cres_377[1]])

#tran_df
num_data = np.vstack((tran_num[1:],tran_num_by_cres[1:],tran_num_by_cres_376[1:],tran_num_by_cres_377[1:])).T
ratio_data = np.vstack((tran_ratio[1:],tran_ratio_by_cres[1:],tran_ratio_by_cres_376[1:],tran_ratio_by_cres_377[1:])).T
tran_df = pd.DataFrame({'Name': ['Total', 'HS 375','HS 376', 'HS 377'], 'Continued_2': ratio_data[0], 'Continued_3': ratio_data[1]})
tran_df.set_index('Name', inplace=True)
tran_df_transpose = tran_df.T

# to_csv
tran_df.to_csv('/Users/jinyaotian/Desktop/transition.csv')

tran_df_transpose.to_csv('/Users/jinyaotian/Desktop/transition_transpose.csv')


# Course level: How many attempts they have tried before passed the exam? (Analysis difficulty of course)

Columns = ['Emplid', 'Course', 'Course Sub Status', 'Last Enrl Dt Stmp', 'Did Not Sit', 'Failed', 'Passed', 'Took Exam']
# Question: 'Sit' means took the exam. So redundancy with column 'Took Exam'?
atp_df = df[Columns]

# 'HS375'
# Total number: 1204
# Distinct student: 1052
atp_375 = atp_df.loc[atp_df['Course'] == 'HS375']
atp_375 = atp_375[['Emplid','Did Not Sit', 'Failed', 'Passed', 'Took Exam']]

atp_375_exam = atp_375.loc[atp_375['Took Exam'] == 1]
# Number who took the exam: 852

# Group by
res_375 = atp_375_exam.groupby(['Emplid']).sum()

#output
res_375.to_csv('/Users/jinyaotian/Desktop/result375.csv')


# 'HS376'
# Total number: 920
# Distinct student: 796
atp_376 = atp_df.loc[atp_df['Course'] == 'HS376']
atp_376 = atp_376[['Emplid','Did Not Sit', 'Failed', 'Passed', 'Took Exam']]

atp_376_exam = atp_376.loc[atp_376['Took Exam'] == 1]
# Number who took the exam: 703

# Group by
res_376 = atp_376_exam.groupby(['Emplid']).sum()

#output
res_376.to_csv('/Users/jinyaotian/Desktop/result376.csv')

# 'HS377'
# Total number: 778
# Distinct student: 689
atp_377 = atp_df.loc[atp_df['Course'] == 'HS377']
atp_377 = atp_377[['Emplid','Did Not Sit', 'Failed', 'Passed', 'Took Exam']]

atp_377_exam = atp_377.loc[atp_377['Took Exam'] == 1]
# Number who took the exam: 654

# Group by
res_377 = atp_377_exam.groupby(['Emplid']).sum()

#output
res_377.to_csv('/Users/jinyaotian/Desktop/result377.csv')


# What proportion of students didn’t take the exam but have gone through all
# course material? Why is that? They are just for knowledge and don’t care about certificate?

df.columns