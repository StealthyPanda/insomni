import streamlit as st
import plotly.express as px
import pandas as pd


#----------------------------------------------------------------------------------------------------
#setup stuff
st.set_page_config(
    layout = 'wide',
    page_title = 'Insomni • Analysis',
    page_icon = '🔍'
)

st.title('Analysis')
st.subheader('', divider='gray')

def removedata():
    del st.session_state['daframe']

if 'daframe' in st.session_state:
    st.sidebar.button('Remove dataset', on_click=removedata, use_container_width=True)
else:
    st.error('##### Viable dataset not yet found; Upload and fix a dataset in the sidebar.')
    exit()


finalframe : pd.DataFrame = st.session_state['daframe']

# st.sidebar.subheader('Columns for the plot:', divider='red')
# if not st.sidebar.checkbox('*All fields*'):
#     selectedcols = [st.sidebar.checkbox(f'`{x}`') for x in finalframe.columns]
# else:
#     selectedcols = [True for _ in finalframe.columns]

fields = list(filter(lambda x: pd.api.types.is_numeric_dtype(finalframe[x].dtype), finalframe.columns))
# for i, each in enumerate(selectedcols):
#     if each : fields.append(finalframe.columns[i])

# if len(fields) == 0:
#     st.markdown('###### *Select columns from the sidebar to add to plot*')
#     exit()


#----------------------------------------------------------------------------------------------------





left, gap, right = st.columns([6, 1, 6])


if 'csel' not in st.session_state : st.session_state['csel'] = None
if 'colsel' not in st.session_state : st.session_state['colsel'] = None


plotsize = 600
mainplot = px.scatter_matrix(
    finalframe, 
    dimensions = fields,
    height = plotsize,
    color = st.session_state['csel'],
    width = plotsize,
    title=f'Pair Plots for all numerical fields in the dataset'
)

left.subheader('Pair-wise analysis', divider='blue')
left.plotly_chart(mainplot, use_container_width=False)
left.selectbox('color', finalframe.columns, index = None, key = 'csel')


heatmap = px.imshow(
    finalframe.loc[:, fields].corr(), text_auto=True,
    title = 'Correlation matrix for all the numerical fields',
    height = 600,
    width= 600,
    color_continuous_scale = st.session_state['colsel']
)

right.subheader('Correlation matrix', divider = 'orange')
right.plotly_chart(heatmap)
right.selectbox('scale', px.colors.named_colorscales(), index = None, key = 'colsel')
