import seaborn as sns
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
from typing import Tuple, List


#----------------------------------------------------------------------------------------------------
#setup stuff
st.set_page_config(
    layout = 'wide',
    page_title = 'Insomni • Plots',
    page_icon = '📈'
)

st.title('Plots')
st.subheader('', divider='rainbow')

def removedata():
    del st.session_state['daframe']

if 'daframe' in st.session_state:
    st.sidebar.button('Remove dataset', on_click=removedata, use_container_width=True)
else:
    st.error('##### Viable dataset not yet found; Upload and fix a dataset in the sidebar.')
    exit()

# if :

# if ('allgood' not in st.session_state) or (not st.session_state['allgood']) or ('daframe' not in st.session_state):

finalframe : pd.DataFrame = st.session_state['daframe']

st.sidebar.subheader('Columns for the plot:', divider='red')
if not st.sidebar.checkbox('*All fields*'):
    # selectedcols = [st.sidebar.checkbox(f'`{x}`') for x in finalframe.columns]
    selectedcols = st.sidebar.multiselect('Select columns to plot:', finalframe.columns)
else:
    # selectedcols = [True for _ in finalframe.columns]
    selectedcols = finalframe.columns

fields = selectedcols
# for i, each in enumerate(selectedcols):
#     if each : fields.append(finalframe.columns[i])

if len(fields) == 0:
    st.markdown('###### *Select columns from the sidebar to add to plot*')
    exit()


#----------------------------------------------------------------------------------------------------


# st.dataframe(eda.assigntypes(finalframe))

nnumeric = sum([int(pd.api.types.is_numeric_dtype(finalframe[x])) for x in fields])

# st.write(nnumeric)


plots = ['hist', 'density']


if nnumeric >= 2:
    plots.append('bar')
    plots.append('pie')
    plots.append('violin')
    plots.append('box')
    plots.append('scatter')
    plots.append('scatterline')
    plots.append('line')
    plots.append('area')
    plots.append('pair')
    plots.append('heatmap')
    plots.append('map')

# st.write(plots)


#----------------------------------------------------------------------------------------------------
#doing the plotting

def getcolumnsold(parent : st.container, colprompt : str, cols : List[str], keyheader : str) -> Tuple[List[str], st.container]:
    # cols = list(frame.columns)
    lcols = len(cols)

    selected = []

    left, right = parent.columns(2)
    left.write(colprompt)
    selcols = [True for _ in range(lcols)]

    if lcols <= 6:
        if not left.checkbox('_All fields_', key = keyheader, value = True):
            selcols = [left.checkbox(f'`{x}`', key = f'{keyheader}cbn_{i}') for i, x in enumerate(cols)]
        for i, each in enumerate(selcols):
            if each:selected.append(cols[i])
        return selected, right
    else:
        right.write('')
        right.write('')
        right.write('')
        if not left.checkbox('_All fields_', key = keyheader, value = True):
            selcolsleft = [left.checkbox(f'`{x}`', key = f'{keyheader}lcbn_{i}') for i, x in enumerate(cols[:len(cols)//2])]
            selcolsright = [right.checkbox(f'`{x}`', key = f'{keyheader}rcbn_{i}') for i, x in enumerate(cols[len(cols)//2:])]
            selcols = selcolsleft + selcolsright
        for i, each in enumerate(selcols):
            if each:selected.append(cols[i])
        return selected, None


def getcolumns(parent : st.container, colprompt : str, frame : pd.DataFrame, keyheader : str) -> Tuple[List[str], st.container]:
    if not parent.checkbox('*All fields*', key = f'{keyheader}_afcb', value = True):
        options = parent.multiselect(colprompt, frame.columns, key = f'{keyheader}_multisel')
        return (options, None)
    else:
        return (frame.columns, None)


def plothist(parent : st.container):
    global fields, finalframe
    main, ops = parent.columns([10, 2])
    xsel = ops.selectbox('x axis', fields, key = 'hx')
    ysel = ops.selectbox('y axis', fields, key = 'phy', index = None)
    csel = ops.selectbox('color', fields, key = 'phc', index = None)
    try:
        fig = px.histogram(
            finalframe,
            xsel, ysel, csel
        )
        main.plotly_chart(
            fig,
            use_container_width = True
        )
    except Exception:
        main.error('Cannot plot using given fields!')
        return

def plotbar(parent : st.container):
    global fields, finalframe
    main, ops = parent.columns([10, 2])
    xsel = ops.selectbox('x axis', fields, key = 'bx')
    ysel = ops.selectbox('y axis', fields, key = 'pby', index = None)
    csel = ops.selectbox('color', fields, key = 'pbc', index = None)
    try:
        fig = px.bar(
            finalframe,
            xsel, ysel, csel
        )
        main.plotly_chart(
            fig,
            use_container_width = True
        )
    except Exception:
        main.error('Cannot plot using given fields!')
        return

def plotpie(parent : st.container):
    global fields, finalframe
    main, ops = parent.columns([10, 2])
    xsel = ops.selectbox('names', fields, key = 'ppx')
    ysel = ops.selectbox('values', fields, key = 'ppy', index = None)
    csel = ops.selectbox('colors', fields, key = 'ppc', index = None)
    try:
        fig = px.pie(
            finalframe,
            xsel, ysel, csel
        )
        main.plotly_chart(
            fig,
            use_container_width = True
        )
    except Exception:
        main.error('Cannot plot using given fields!')
        return

def plotmap(parent : st.container):
    global fields, finalframe

    main, ops = parent.columns([10, 2])
    xsel = ops.selectbox('latitude', fields, key = 'mmx', index = None)
    ysel = ops.selectbox('longitude', fields, key = 'mmy', index = None)
    csel = ops.selectbox('color', fields, key = 'mmc', index = None)
    # csel = ops.color_picker('')
    ssel = ops.selectbox('size', fields, key = 'mms', index = None)

    if xsel and ysel:
        try:
            main.map(
                finalframe, latitude = xsel, longitude = ysel, color = csel, size = ssel
            )
        except Exception:
            main.error('Cannot plot using given fields!')
            return

def plotdist(parent : st.container):
    global fields, finalframe
    main, ops = parent.columns([10, 2])

    # ops.markdown('*Select fields to plot:*')
    # sfs = []

    # fs = [ops.checkbox(f) for f in fields]
    # for i, each in enumerate(fs):
    #     if each : sfs.append(fields[i])
    sfs = ops.multiselect('*Select fields to plot*', fields)

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
    try:
        fig = px.violin(
            finalframe, x = xsel, y = ysel, color = csel
        )
        main.plotly_chart(
            fig,
            use_container_width = True
        )
    except Exception:
        main.error('Cannot plot using given fields!')
        return

def plotbox(parent : st.container):
    global fields, finalframe
    main, ops = parent.columns([10, 2])
    xsel = ops.selectbox('x axis', fields, key = 'pbbx')
    ysel = ops.selectbox('y axis', fields, key = 'pbby', index = None)
    csel = ops.selectbox('color', fields, key = 'pbbc', index = None)
    try:
        fig = px.box(
            finalframe, xsel, ysel, csel
        )
        main.plotly_chart(
            fig,
            use_container_width = True
        )
    except Exception:
        main.error('Cannot plot using given fields!')
        return

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

def plotpairplot(parent : st.container):
    global fields, finalframe
    main, ops = parent.columns([10, 2])
    # xsel = ops.selectbox('x axis', fields, key = 'pslx')
    # ysel = ops.selectbox('y axis', fields, key = 'psly', index = None)
    csel = ops.selectbox('color', fields, key = 'pplc', index = None)
    try:
        fig = px.scatter_matrix(
            finalframe,#, xsel, ysel, csel,,
            dimensions = list(filter(lambda x:x != csel, fields)),
            color = csel 
        )
        main.plotly_chart(
            fig,
            use_container_width = True,
            # height = 10000
        )
    except TypeError:
        main.error('Cannot plot using given configuration!')
        return
    
def plotheatmap(parent : st.container):
    global fields, finalframe
    main, ops = parent.columns([10, 2])
    # xsel = ops.selectbox('x axis', fields, key = 'pslx')
    # ysel = ops.selectbox('y axis', fields, key = 'psly', index = None)
    # csel = ops.selectbox('color', fields, key = 'pplc', index = None)
    cols, leftover = getcolumns(ops, 'Select columns', finalframe, 'hmc')
    try:
        fig = px.imshow(
            finalframe.loc[:, cols],#, xsel, ysel, csel,,
            # color = csel 
        )
        main.plotly_chart(
            fig,
            use_container_width = True,
            # height = 10000
        )
    except TypeError:
        main.error('Cannot plot using given configuration!')
        return




plotdict = {
    'hist' : plothist,
    'bar' : plotbar,
    'pie' : plotpie,
    'density' : plotdist,
    'violin' : plotviolin,
    'box' : plotbox,
    'scatter' : plotscatter,
    'scatterline' : plotscatterline,
    'line' : plotline,
    'area' : plotarea,
    'pair' : plotpairplot,
    'heatmap' : plotheatmap,
    'map' : plotmap,
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
    'pair' : 'Pair',
    'heatmap' : 'Heatmap',
    'bar' : 'Bar',
    'pie' : 'Pie',
    'map' : 'GeoMap',
}


pex, bkh = st.tabs(['Plotly Express Plots', 'Bokeh Plots'])
plottabs = pex.tabs([f'{plotnames[x]} Plot' for x in plots])

for i, each in enumerate(plottabs):
    with each : plotdict[plots[i]](each)

bkh.markdown('**Coming soon...**')