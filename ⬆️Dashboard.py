import streamlit as st
import pandas as pd
from io import StringIO
from eda import assigntypes
import plotly.express as px
import plotly.figure_factory as ff
import seaborn as sns
import os


#--------------------------------------------------------------------------------------------------------------------------
#misc setup stuff
st.set_page_config(
    layout = 'wide',
    page_title = 'Insomni',
    page_icon = '🌃'
)
st.title('Insomni 🌃')
st.write('EDA with no code!')
# st.divider()
st.write('')
st.write('')

leftcol, gap, rightcol = st.columns([8, 1, 8])

rowsthresh = 5000
xuniques = 30

st.session_state['rowsthresh'] = rowsthresh
st.session_state['xuniques'] = xuniques
#--------------------------------------------------------------------------------------------------------------------------


#--------------------------------------------------------------------------------------------------------------------------
#importing file stuff
rawframe = None

snsgdn = sns.get_dataset_names()
snsgdn += ['uber']

#uber data
@st.cache_data
def loaduber():
    path = "uber-raw-data-sep14.csv.gz"
    if not os.path.isfile(path):
        path = f"https://github.com/streamlit/demo-uber-nyc-pickups/raw/main/{path}"

    data = pd.read_csv(
        path,
        nrows=10000,  # approx. 1% of data
        names=[
            "date/time",
            "lat",
            "lon",
        ],  # specify names directly since they don't change
        skiprows=1,  # don't read header since names specified directly
        usecols=[0, 1, 2],  # doesn't load last column, constant value "B02512"
        parse_dates=[
            "date/time"
        ],  # set as datetime instead of converting after the fact
    )

    return data




@st.cache_data
def filefetcher(rawfile):
    try:
        stringio = StringIO(rawfile.getvalue().decode('UTF-8'))
        rawframe = pd.read_csv(stringio, engine ='c')
    except Exception as e:
        st.sidebar.write("Unable to parse the CSV file! Full error:")
        st.sidebar.write(e)
        exit()
    return rawframe


def removedata():
    del st.session_state['daframe']

if 'daframe' in st.session_state:
    rawframe = st.session_state['daframe']
    st.sidebar.button('Remove dataset', on_click=removedata, use_container_width=True)
else:
    rawfile = st.sidebar.file_uploader( 
        'Upload a dataset',
        type = 'csv',
        key = 'datafile',
        # help = 'Upload a dataset'
    )
    st.sidebar.header('OR')
    sample = st.sidebar.selectbox('Choose a sample dataset', snsgdn, index = None)


    if (rawfile is None) and (sample is None):
        st.markdown('##### Start by uploading a dataset to work on in the sidebar.')
        exit()
    elif rawfile is not None:
        rawframe = filefetcher(rawfile)
    else:
        if sample == 'uber':
            with st.spinner('Loading Uber Dataset'):
                rawframe = loaduber()
        else:
            rawframe = sns.load_dataset(sample)

nrows = len(rawframe)
largeset = nrows > rowsthresh
#--------------------------------------------------------------------------------------------------------------------------





#--------------------------------------------------------------------------------------------------------------------------
#Displaying the main frame
leftcol.header('Original Dataset', divider='blue')
leftcol.markdown(f'#### Loaded `{nrows}` rows and `{len(rawframe.columns)}` columns')
displayframe = leftcol.data_editor(rawframe, key = 'displayframe', use_container_width = True)
#--------------------------------------------------------------------------------------------------------------------------





#--------------------------------------------------------------------------------------------------------------------------
#Displaying stats and stuff on the right side
rightcol.header('Stats', divider='orange')
rightcol.markdown('##### Field Types')
rightcol.dataframe(assigntypes(displayframe), use_container_width = True)

rightcol.markdown('##### Numerical Fields')
rightcol.markdown('General stats of the numerical fields of the dataset')
described = displayframe.describe()
described = described.loc[list(filter(lambda x:x[-1] != '%', described.index)), :]

if len(described.columns) < 5:
    described = described.transpose()

rightcol.dataframe(described, use_container_width = True)
#--------------------------------------------------------------------------------------------------------------------------


#adding some gap between the sections
st.write('')
st.write('')
st.write('')
st.header('Fieldwise Analysis', divider='rainbow')
botleft, gap, botright = st.columns([5, 0.5, 12])


#--------------------------------------------------------------------------------------------------------------------------
#bottom section

field = botleft.selectbox('Select a data field', displayframe.columns)
isnum = pd.api.types.is_numeric_dtype(displayframe[field].dtype)
if largeset:
    lower, upper = botleft.slider(
        f'Range of rows (max {rowsthresh})',
        0, nrows,
        (0, rowsthresh),
        step = 1
    )
    botleft.markdown(f'##### `{upper - lower}` rows selected')
    if (upper - lower) > rowsthresh:
        botleft.markdown(f'### Maximum no. of rows allowed on this page is {rowsthresh}!')
        exit()
    displayframe = displayframe.loc[lower:upper, :]

tabs = ['Histogram (discrete)']
if isnum:
    tabs.append('Distribution (bins)')
    tabs.append('Scatter')


plottabs = botright.tabs(tabs)
#--------------------------------------------------------------------------------------------------------------------------




#--------------------------------------------------------------------------------------------------------------------------
#basic plots (bottom right stuff)

histplot = px.histogram(displayframe, x = field)
histplot.update_layout(
    title_text = f'Histogram for `{field}` column'
)

#plotting the histogram
with plottabs[0]:
    if len(displayframe[field].unique()) > xuniques:
        if ('forceshowplot' not in st.session_state) or (not st.session_state['forceshowplot']):
            plottabs[0].markdown(f'#### This plot contains too many unique values on x axis (> {xuniques})')
        if plottabs[0].checkbox('Show anyway', help = 'Plotting may take a while', key = 'forceshowplot'):
            plottabs[0].plotly_chart(histplot, use_container_width=True)
    else:
        plottabs[0].plotly_chart(histplot, use_container_width=True)


#plotting the distribution if it is a numerical field
if isnum:
    with plottabs[1]:
        distplot = ff.create_distplot([displayframe[field][displayframe[field].notnull()]], [field])
        distplot.update_layout(
            title_text = f'Distplot for `{field}` column',
            yaxis_title = 'frequency',
            xaxis_title = 'value',
        )
        plottabs[1].plotly_chart(distplot, use_container_width = True)
    with plottabs[2]:
        splot = px.scatter(displayframe, x=displayframe.index, y=field, title=f'Scatter plot for `{field}` column')
        plottabs[2].plotly_chart(splot, use_container_width=True)


#--------------------------------------------------------------------------------------------------------------------------




#--------------------------------------------------------------------------------------------------------------------------
#general info about the field (bottom left stuff)

column = displayframe[field]
column = column.loc[column.notnull()]

info = pd.DataFrame(column.describe())
# info = pd.DataFrame([info], columns = info.index)
info = info.transpose()

botleft.dataframe(info, use_container_width = True)

botleft.write('')
botleft.write('')
botleft.write('')
botleft.write('')
botleft.subheader('Next : Preprocessing', divider='green')
botleft.write('Go to preprocessing in the sidebar to move onto the next step!')
#--------------------------------------------------------------------------------------------------------------------------


#--------------------------------------------------------------------------------------------------------------------------
#updating the dataframe
st.session_state['daframe'] = displayframe
if 'originalframecopy' not in st.session_state:
    st.session_state['originalframecopy'] = displayframe.copy()
#--------------------------------------------------------------------------------------------------------------------------


