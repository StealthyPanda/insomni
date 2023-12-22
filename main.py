import streamlit as st
import pandas as pd
from io import StringIO
# import matplotlib.pyplot as plt
# import seaborn as sns
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource
import numpy as np
from eda import assigntypes
from plots import histogramnormal, histogramdistribution



#--------------------------------------------------------------------------------------------------------------------------
#misc setup stuff
st.set_page_config(layout = 'wide')
st.markdown('# Insomni🌌')
st.write('')
st.write('')
st.write('')

leftcol, gap, rightcol = st.columns([8, 1, 8])

rowsthresh = 5000

#--------------------------------------------------------------------------------------------------------------------------


#--------------------------------------------------------------------------------------------------------------------------
#importing file stuff

rawfile = None
rawfile = st.sidebar.file_uploader( 
    'Import a dataset (*.csv)',
    key = 'datafile',
    # help = 'Upload a dataset'
)

@st.cache_data
def filefetcher(rawfile):

    if rawfile is None:
        st.markdown('##### Start by uploading a dataset to work on in the sidebar!')
        exit()
    try:
        stringio = StringIO(rawfile.getvalue().decode('UTF-8'))
        rawframe = pd.read_csv(stringio, engine ='c')

        nrows = len(rawframe)
        largeset = nrows > 1000
    except Exception as e:
        st.sidebar.write("Unable to parse the CSV file! Full error:")
        st.sidebar.write(e)
        exit()
    
    return rawframe, nrows, largeset

rawframe, nrows, largeset = filefetcher(rawfile)
#--------------------------------------------------------------------------------------------------------------------------


#--------------------------------------------------------------------------------------------------------------------------
#Displaying the main frame
leftcol.markdown('### Original Dataset')
leftcol.markdown(f'#### Loaded `{nrows}` rows and `{len(rawframe.columns)}` columns')
displayframe = leftcol.data_editor(rawframe, key = 'displayframe', use_container_width = True)

leftcol.markdown('### Metadata')
leftcol.markdown('##### Field Types')
leftcol.dataframe(assigntypes(displayframe))


leftcol.markdown('##### Numerical Fields')
leftcol.markdown('General stats of the numerical fields of the dataset')
described = displayframe.describe()
leftcol.dataframe(described.loc[list(filter(lambda x:x[-1] != '%', described.index)), :])
#--------------------------------------------------------------------------------------------------------------------------



#--------------------------------------------------------------------------------------------------------------------------
#right column stuff begins here; setting the correct number of tabs and range of rows
field = rightcol.selectbox('Select a data field', displayframe.columns)
isnum = pd.api.types.is_numeric_dtype(displayframe[field].dtype)
if largeset:
    lower, upper = rightcol.slider(
        'Range of rows (max 1000)',
        0, nrows,
        (0, rowsthresh),
        step = 1
    )
    rightcol.markdown(f'##### `{upper - lower}` rows selected')
    if (upper - lower) > rowsthresh:
        rightcol.markdown(f'### Maximum no. of rows allowed on this page is {rowsthresh}!')
        exit()
    displayframe = displayframe.loc[lower:upper, :]

tabs = ['Histogram (discrete)']
if isnum: tabs.append('Distribution (bins)')

plottabs = rightcol.tabs(tabs)
#--------------------------------------------------------------------------------------------------------------------------




#--------------------------------------------------------------------------------------------------------------------------
#basic plots

#histplot stuff
hplot = histogramnormal(displayframe[field], label = field)
hplot.title = f'`{field}` column histogram'
hplot.height = 400


#plotting the distribution if it is a numerical field
if isnum:
    with plottabs[1]:
        nbins = plottabs[1].number_input(
            'No. of bins',
            min_value = 2,
            value = 2,
            step = 1
        )
        dplot = histogramdistribution(displayframe[field], nbins = nbins, label = field)
        dplot.title = f'`{field}` column distribution'
        dplot.height = 400
        plottabs[1].bokeh_chart(dplot, use_container_width = True)
        


#plotting the histogram
with plottabs[0]:
    if len(displayframe[field].unique()) > 100:
        if ('forceshowplot' in st.session_state):
            if not st.session_state['forceshowplot']:
                plottabs[0].markdown('#### This plot contains too many unique values on x axis')
        else:
            plottabs[0].markdown('#### This plot contains too many unique values on x axis')
            
        if plottabs[0].checkbox('Show anyway', help = 'Plotting may take a while', key = 'forceshowplot'):
            plottabs[0].bokeh_chart(hplot, use_container_width = True)
    else:
        plottabs[0].bokeh_chart(hplot, use_container_width = True)
#--------------------------------------------------------------------------------------------------------------------------




#--------------------------------------------------------------------------------------------------------------------------
#general info about the field

info = displayframe[field].describe()
info = pd.DataFrame([info], columns = info.index)

rightcol.dataframe(info, use_container_width = False)
#--------------------------------------------------------------------------------------------------------------------------





