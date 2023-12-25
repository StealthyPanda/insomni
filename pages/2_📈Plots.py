import seaborn as sns
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff


#----------------------------------------------------------------------------------------------------
#setup stuff
st.title('Plots')
st.subheader('', divider='rainbow')


if ('allgood' not in st.session_state) or (not st.session_state['allgood']):
    st.error('##### Viable dataset not yet found; Upload and fix a dataset in the sidebar.')
    exit()

finalframe : pd.DataFrame = st.session_state['daframe']

st.sidebar.subheader('Columns for the plot:', divider='red')
if not st.sidebar.checkbox('*All fields*'):
    selectedcols = [st.sidebar.checkbox(f'`{x}`') for x in finalframe.columns]
else:
    selectedcols = [True for _ in finalframe.columns]

fields = []
for i, each in enumerate(selectedcols):
    if each : fields.append(finalframe.columns[i])

if len(fields) == 0:
    st.markdown('###### *Select columns from the sidebar to add to plot*')
    exit()
#----------------------------------------------------------------------------------------------------


# st.dataframe(eda.assigntypes(finalframe))

nnumeric = sum([int(pd.api.types.is_numeric_dtype(finalframe[x])) for x in fields])

# st.write(nnumeric)


plots = ['hist', 'density']


if nnumeric >= 2:
    plots.append('violin')
    plots.append('box')
    plots.append('scatter')
    plots.append('scatterline')
    plots.append('line')
    plots.append('area')

# st.write(plots)


#----------------------------------------------------------------------------------------------------
#doing the plotting

def plothist(parent : st.container):
    global fields, finalframe
    main, ops = parent.columns([10, 2])
    xsel = ops.selectbox('x axis', fields, key = 'hx')
    ysel = ops.selectbox('y axis', fields, key = 'phy', index = None)
    csel = ops.selectbox('color', fields, key = 'phc', index = None)
    fig = px.histogram(
        finalframe,
        xsel, ysel, csel
    )
    main.plotly_chart(
        fig,
        use_container_width = True
    )

def plotdist(parent : st.container):
    global fields, finalframe
    main, ops = parent.columns([10, 2])

    ops.markdown('*Select fields to plot:*')
    sfs = []

    fs = [ops.checkbox(f) for f in fields]
    for i, each in enumerate(fs):
        if each : sfs.append(fields[i])

    if len(sfs) == 0:
        main.warning('No fields selected!')
        return
    
    binsize = ops.number_input('Bin size')

    try:
        fig = ff.create_distplot(
            [finalframe[f] for f in sfs],
            sfs, bin_size=binsize, 
        )
        main.plotly_chart(
            fig,
            use_container_width = True
        )
    except TypeError:
        main.error('Invalid set of fields! (Ensure only numeric fields are used.)')

def plotviolin(parent : st.container):
    global fields, finalframe
    main, ops = parent.columns([10, 2])
    xsel = ops.selectbox('x axis', fields, key = 'pvx')
    ysel = ops.selectbox('y axis', fields, key = 'pvy', index = None)
    csel = ops.selectbox('color', fields, key = 'pvc', index = None)
    fig = px.violin(
        finalframe, x = xsel, y = ysel, color = csel
    )
    main.plotly_chart(
        fig,
        use_container_width = True
    )

def plotbox(parent : st.container):
    global fields, finalframe
    main, ops = parent.columns([10, 2])
    xsel = ops.selectbox('x axis', fields, key = 'pbx')
    ysel = ops.selectbox('y axis', fields, key = 'pby', index = None)
    csel = ops.selectbox('color', fields, key = 'pbc', index = None)
    fig = px.box(
        finalframe, xsel, ysel, csel
    )
    main.plotly_chart(
        fig,
        use_container_width = True
    )

def plotscatter(parent : st.container):
    global fields, finalframe
    main, ops = parent.columns([10, 2])
    xsel = ops.selectbox('x axis', fields, key = 'psx')
    ysel = ops.selectbox('y axis', fields, key = 'psy', index = None)
    csel = ops.selectbox('color', fields, key = 'psc', index = None)
    ssel = ops.selectbox('size', fields, key = 'pss', index = None)
    try:
        fig = px.scatter(
            finalframe, xsel, ysel, csel, None, ssel
        )
        main.plotly_chart(
            fig,
            use_container_width = True
        )
    except TypeError:
        main.error('Cannot plot using given configuration!')
        return

def plotline(parent : st.container):
    global fields, finalframe
    main, ops = parent.columns([10, 2])
    xsel = ops.selectbox('x axis', fields, key = 'plx')
    ysel = ops.selectbox('y axis', fields, key = 'ply', index = None)
    csel = ops.selectbox('color', fields, key = 'plc', index = None)
    # ssel = ops.selectbox('size', fields, key = 'pss', index = None)
    try:
        fig = px.line(
            finalframe, xsel, ysel, None, csel
        )
        main.plotly_chart(
            fig,
            use_container_width = True
        )
    except TypeError:
        main.error('Cannot plot using given configuration!')
        return

def plotarea(parent : st.container):
    global fields, finalframe
    main, ops = parent.columns([10, 2])
    xsel = ops.selectbox('x axis', fields, key = 'pax')
    ysel = ops.selectbox('y axis', fields, key = 'pay', index = None)
    csel = ops.selectbox('color', fields, key = 'pac', index = None)
    # ssel = ops.selectbox('size', fields, key = 'pss', index = None)
    try:
        fig = px.area(
            finalframe, xsel, ysel, None, csel
        )
        main.plotly_chart(
            fig,
            use_container_width = True
        )
    except TypeError:
        main.error('Cannot plot using given configuration!')
        return

def plotscatterline(parent : st.container):
    global fields, finalframe
    main, ops = parent.columns([10, 2])
    xsel = ops.selectbox('x axis', fields, key = 'pslx')
    ysel = ops.selectbox('y axis', fields, key = 'psly', index = None)
    csel = ops.selectbox('color', fields, key = 'pslc', index = None)
    try:
        fig = px.scatter(
            finalframe, xsel, ysel, csel, 
        )
        main.plotly_chart(
            fig,
            use_container_width = True
        )
    except TypeError:
        main.error('Cannot plot using given configuration!')
        return





plotdict = {
    'hist' : plothist,
    'density' : plotdist,
    'violin' : plotviolin,
    'box' : plotbox,
    'scatter' : plotscatter,
    'scatterline' : plotscatterline,
    'line' : plotline,
    'area' : plotarea,
}

plotnames = {
    'hist' : 'Histogram',
    'density' : 'Distribution',
    'violin' : 'Violin',
    'box' : 'Box',
    'scatter' : 'Scatter',
    'scatterline' : 'Scatter Line',
    'line' : 'Line',
    'area' : 'Area',
}


pex, bkh = st.tabs(['Plotly Express Plots', 'Bokeh Plots'])
plottabs = pex.tabs([f'{plotnames[x]} Plot' for x in plots])

for i, each in enumerate(plottabs):
    with each : plotdict[plots[i]](each)

