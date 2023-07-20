import pandas as pd
import streamlit as st
import plotly.express as px
from PIL import Image
import nltk
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import country_converter as coco
from IPython.display import display
import plotly.graph_objects as go
import numpy as np
import warnings
warnings.filterwarnings('ignore')
import plotly.figure_factory as ff

st.set_page_config(page_title="Salary Datas")
st.header('Data Science Salary')
st.subheader('Python project by Kiran Shrestha')

# # load dataframe
excel_file= 'salary.xlsx'
sheet_name='ds_salaries.csv'

#creating data frames
df=pd.read_excel(excel_file,
               sheet_name= 'ds_salaries.csv',
               usecols='A:K',
               header=0)

df_CompanySize=pd.read_excel(excel_file,
               sheet_name='ds_salaries.csv',
               usecols= 'L:M',
               header=0)

df_CompanySize.dropna(inplace=True)

#displaying data frames
st.dataframe(df)


# --- STREAMLIT SELECTION
job_title = df['job_title'].unique().tolist()
salary = df['salary'].unique().tolist()

salary_selection = st.slider('Salary:',
                        min_value= min(salary),
                        max_value= max(salary),
                        value=(min(salary),max(salary)))

job_title_selection = st.multiselect('job_title:',
                                    job_title,
                                    default=job_title)

mask = (df['salary'].between(*salary_selection)) & (df['job_title'].isin(job_title_selection))
number_of_result = df[mask].shape[0]
st.markdown(f'*Available Results: {number_of_result}*')

#creating pie chart



pie_chart = px.pie(df_CompanySize,
                   title= 'Company Size',
                   values='Count',
                   names= 'Company_size'
                   )

st.plotly_chart(pie_chart)

st.dataframe(df_CompanySize)

#creating bar chart
df_group = df['employment_type'].value_counts()
emp_type = ['Full-Time', 'Part-Time', 'Contract', 'Freelance']


bar_chart = px.bar(x = emp_type, y = df_group.values, 
       color = df_group.index, text = df_group.values, 
       color_discrete_sequence = ['#F63366']*len(df_group),
       title = 'Employment Type Distribution')

bar_chart.update_layout(xaxis_title='Employment Type', yaxis_title='Count', title='Employment Type Distribution')

st.plotly_chart(bar_chart)

#employee location on map
country = coco.convert(names = df['employee_residence'], to = "ISO3")
df['employee_residence'] = country
residence = df['employee_residence'].value_counts()
fig = px.choropleth(locations = residence.index,
                    color = residence.values,
                    color_continuous_scale=px.colors.sequential.YlGn,
                    title = 'Employee Loaction On Map')
st.plotly_chart(fig)

#comparision of employee residence and company location
top_15_emp_locations = residence[:15]
fig = px.bar(y = top_15_emp_locations.values, x = top_15_emp_locations.index, 
            color = top_15_emp_locations.index, text = top_15_emp_locations.values,
            title = 'Top 15 Locations of Employees')

fig.update_layout( xaxis_title = "Location of Employees", yaxis_title = "count")
st.plotly_chart(fig)

country = coco.convert(names=df['company_location'], to="ISO3")
df['company_location'] = country
company_location = df['company_location'].value_counts()
top_15_company_location = company_location[:15]

fig = go.Figure(data = [
    go.Bar(name = 'Employee Residence', 
           x = top_15_emp_locations.index, y = top_15_emp_locations.values,
           text = top_15_emp_locations.values),
    go.Bar(name = 'Company Location', x = top_15_company_location.index, 
           y = top_15_company_location.values, text = top_15_company_location.values)])

fig.update_layout(barmode = 'group', xaxis_tickangle = -45,
                  title='Comparison of Employee Residence and Company Location')

st.plotly_chart(fig)

#salary in usd
fig = px.box(y = df['salary_in_usd'], title = 'Salary in USD')
st.plotly_chart(fig)

#work year distribution
work_year = df['work_year'].value_counts()
fig = px.pie(values = work_year.values, names = work_year.index, 
            title = 'Work year distribution')
st.plotly_chart(fig)

#remote ratio
remote_type = ['Fully Remote', 'Partially Remote', 'No Remote Work']

fig = px.bar(x = remote_type, y = df['remote_ratio'].value_counts().values,
       color = remote_type, text = df['remote_ratio'].value_counts().values,
       title = 'Remote Ratio Distribution')

fig.update_layout( xaxis_title = "Remote Type", yaxis_title = "count")
st.plotly_chart(fig)


#Remote Ratio by Work Year
remote_year = df.groupby(['work_year','remote_ratio']).size()
ratio_2020 = np.round(remote_year[2020].values/remote_year[2020].values.sum(),2)
ratio_2021 = np.round(remote_year[2021].values/remote_year[2021].values.sum(),2)
ratio_2022 = np.round(remote_year[2022].values/remote_year[2022].values.sum(),2)
ratio_2023 = np.round(remote_year[2023].values/remote_year[2023].values.sum(),2)

fig = go.Figure()
categories = ['No Remote Work', 'Partially Remote', 'Fully Remote']
fig.add_trace(go.Scatterpolar(
            r = ratio_2020, theta = categories, 
            fill = 'toself', name = '2020 remote ratio'))

fig.add_trace(go.Scatterpolar(
            r = ratio_2021, theta = categories,
            fill = 'toself', name = '2021 remote ratio'))

fig.add_trace(go.Scatterpolar(
            r = ratio_2022, theta = categories,
            fill = 'toself', name = '2022 remote ratio'))

fig.add_trace(go.Scatterpolar(
            r = ratio_2023, theta = categories,
            fill = 'toself', name = '2023 remote ratio'))
fig.update_layout(title='Remote Work Ratio by Year')  # Add the title

st.plotly_chart(fig)

#salary based on work year

work_2020 = df.loc[(df['work_year'] == 2020)]
work_2021 = df.loc[(df['work_year'] == 2021)]
work_2022 = df.loc[(df['work_year'] == 2022)]
work_2023 = df.loc[(df['work_year'] == 2023)]
 
hist_data = [work_2020['salary_in_usd'], work_2021['salary_in_usd'], 
            work_2022['salary_in_usd'], work_2023['salary_in_usd']]
group_labels = ['2020 salary', '2021 salary', '2022 salary', '2023 salary']

year_salary = pd.DataFrame(columns = ['2020', '2021', '2022', '2023'])
year_salary['2020'] = work_2020.groupby('work_year').mean('salary_in_usd')['salary_in_usd'].values
year_salary['2021'] = work_2021.groupby('work_year').mean('salary_in_usd')['salary_in_usd'].values
year_salary['2022'] = work_2022.groupby('work_year').mean('salary_in_usd')['salary_in_usd'].values
year_salary['2023'] = work_2023.groupby('work_year').mean('salary_in_usd')['salary_in_usd'].values

fig1 = ff.create_distplot(hist_data, group_labels, show_hist = False)
fig2 = go.Figure(data=px.bar(x = year_salary.columns, 
                            y = year_salary.values.tolist()[0],
                            color = year_salary.columns,
                            title = 'Mean Salary by Work Year'))

fig1.update_layout(title = 'Salary Distribution based on Work Year')
fig2.update_layout(xaxis_title = "Work Year", yaxis_title = "Mean Salary (k)")
st.plotly_chart(fig1)
st.plotly_chart(fig2)

#top 25 highest salary by designation
salary_designation = df.groupby(['salary_in_usd', 'job_title']).size().reset_index()
salary_designation = salary_designation[-25:]
fig = px.bar(x = salary_designation['job_title'], y = salary_designation['salary_in_usd'],
            text = salary_designation['salary_in_usd'], color = salary_designation['salary_in_usd'])

fig.update_layout( xaxis_title = "Job Designation", yaxis_title = "Salaries ")
fig.update_layout(xaxis_tickangle = -45, 
                  title = 'Top 25 Highest Salary by Designation')
st.plotly_chart(fig)

#aVERAGE SALARY BASED ON COMPANY LOCATION
salary_location = df.groupby(['salary_in_usd', 'company_location']).size().reset_index()
means = salary_location.groupby('company_location').mean().reset_index()

fig = px.choropleth(locations = means['company_location'], color = means['salary_in_usd'],
                    title = 'Average Salary by Company Location')
st.plotly_chart(fig)
