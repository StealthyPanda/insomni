import streamlit as st
import pandas as pd
import eda

#--------------------------------------------------------------------------------------------------------------------------
#misc setup stuff
st.set_page_config(
    layout = 'wide',
    page_title = 'Insomni • Preprocessing',
    page_icon = '🌠'
)

st.title('Preprocessing')
st.header('', divider='violet')
st.write('')
st.write('')
st.write('')

if 'efn' not in st.session_state:
    st.session_state['efn'] = 0

st.session_state['allgood'] = False

#--------------------------------------------------------------------------------------------------------------------------


#--------------------------------------------------------------------------------------------------------------------------
#main display section
if 'daframe' not in st.session_state:
    st.write('Upload data in the sidebar to get started!')
    exit()

originalframe : pd.DataFrame = st.session_state['daframe']

mainpart, sidepart = st.columns([7, 3])
botmain, botside = st.columns([7, 3])

if 'colchanges' not in st.session_state:
    displayframe = mainpart.data_editor(
        originalframe,
        use_container_width=True,
        key = f"editedframe{st.session_state['efn']}",
        num_rows='fixed', #TODO: Figure out how to make it dynamic, cuz dynamic changes are not showing up in the damn dataframe automatically,only in the frontend
    )
else:
    displayframe = mainpart.data_editor(
        st.session_state['colchanges'],
        use_container_width=True,
        key = f"editedframe{st.session_state['efn']}",
        num_rows='fixed',
    )

nnulls = displayframe.isnull().sum().sum()


#sidepart stuff
st.session_state['nonulls'] = (nnulls == 0)
if nnulls > 0:
    botmain.warning(f'There are **{displayframe.isnull().sum().sum()}** null values remaining in the dataframe.')
else:
    botmain.success('No null values in the dataframe!')
#--------------------------------------------------------------------------------------------------------------------------


ops = sidepart.tabs([
    'Clean Column Names',
    'Drop Nulls',
    'Cast Types',
    'Fill Nulls',
    'Normalise',
    'Noise',
])





#--------------------------------------------------------------------------------------------------------------------------
#column ops

def updatenames():
    global displayframe
    cleaned = eda.cleancolumnnames(list(displayframe.columns))
    if 'colchanges' not in st.session_state:
        st.session_state['colchanges'] = displayframe.copy()
    for i, each in enumerate(displayframe.columns):
        if not st.session_state['unsc'][i]:
            cleaned[i] = each
    st.session_state['colchanges'].columns = cleaned
    # sidepart.write(cleaned)
    changes = {}
    for each in range(len(displayframe.columns)):
        changes[originalframe.columns[each]] = displayframe.columns[each]
    sidepart.info('Updated names!')

def dropnulls():
    global displayframe
    mask = st.session_state['dnsc']
    cols = []
    for i, x in enumerate(displayframe.columns):
        if mask[i]:cols.append(x)
    newframe, ndrops = eda.dropnulls(displayframe, cols)
    st.session_state['colchanges'] = newframe
    sidepart.info(f'Dropped `{ndrops}` rows.')


types = {
    'integer' : pd.Int64Dtype.type,
    'float' : pd.Float64Dtype.type,
    'string' : pd.StringDtype.type,
    'datetime' : pd.DatetimeTZDtype.type
}

ntechs = [
    'zfact', 'max', 'mean', 'mode', 'l1', 'l2'
]

def castfield():
    try:
        newframe = displayframe.astype({
            st.session_state['ctc'] : types[st.session_state['ctt']]
        })
    except pd.errors.IntCastingNaNError:
        ops[2].error('Couldn\'t cast due to NULL values...')
        return
    except TypeError:
        ops[2].error('Invalid type to convert to...')
        return
    st.session_state['colchanges'] = newframe
    ops[2].info('Updated field type')


def fillnulls():
    cols = []
    for i, each in enumerate(displayframe.columns):
        if st.session_state['fnsc'][i]:
            cols.append(each)
    st.session_state['colchanges'], s, f = eda.fillmissing(displayframe, st.session_state['defval'], cols)
    ops[3].info(f'Filled null values; **{s}** successful fills and **{f}** failed fills.')


def normaliseframe():
    global displayframe
    mask = st.session_state['nsc']
    cols = []
    for i, x in enumerate(displayframe.columns):
        if mask[i]:cols.append(x)
    try:
        newframe = eda.normalise(displayframe, cols, st.session_state['nt'])
    except TypeError:
        ops[4].info('Cannot normalise given set of fields!')
        return
    st.session_state['colchanges'] = newframe
    ops[4].info('Fields normalised!')

with ops[0]:
    ops[0].write('Select columns to clean:')
    if not ops[0].checkbox('_All fields_', key = 'afcc', value = True):
        selcols = [ops[0].checkbox(f'`{x}`', key = f'cbcc_{i}') for i, x in enumerate(displayframe.columns)]
    else:
        selcols = [True for _ in range(len(displayframe.columns))]
    st.session_state['unsc'] = selcols
    ops[0].button('Update names', use_container_width=True, on_click=updatenames)


with ops[1]:
    ops[1].write('Select columns to drop nulls from:')
    if not ops[1].checkbox('_All fields_', key = 'afdn', value = True):
        selcols = [ops[1].checkbox(f'`{x}`', key = f'cbdn_{i}') for i, x in enumerate(displayframe.columns)]
    else:
        selcols = [True for _ in range(len(displayframe.columns))]
    st.session_state['dnsc'] = selcols
    ops[1].button('Drop null valued rows', use_container_width=True, on_click=dropnulls)


with ops[2]:
    field = ops[2].selectbox('Select a field', displayframe.columns, index = None)
    if field is not None:
        ops[2].info(f"'`{field}`' field is of type  '`{displayframe[field].dtype}`'")
    castto = ops[2].selectbox('Cast to...', types.keys(), index = None)
    if (field is not None) and (castto is not None):
        st.session_state['ctc'] = field
        st.session_state['ctt'] = castto
        ops[2].button('Cast', use_container_width=True, on_click=castfield)

with ops[3]:
    left, right = ops[3].columns(2)

    left.write('Select columns to fill nulls in:')
    
    if not left.checkbox('_All fields_', key = 'affn', value = True):
        selcols = [left.checkbox(f'`{x}`', key = f'cbfn_{i}') for i, x in enumerate(displayframe.columns)]
    else:
        selcols = [True for _ in range(len(displayframe.columns))]
    st.session_state['fnsc'] = selcols

    choice = right.selectbox('Value type', ['number', 'string', 'date/time'])

    if choice == 'number':
        st.session_state['defval'] = right.number_input('Enter default value')
    elif choice == 'string':
        st.session_state['defval'] = right.text_input('Enter default value')
    elif choice == 'date/time':
        st.session_state['defval'] = right.date_input('Enter default value')

    ops[3].button('Fill null values', use_container_width=True, on_click=fillnulls)



with ops[4]:
    left, right = ops[4].columns(2)

    left.write('Select columns to normalise:')
    
    if not left.checkbox('_All fields_', key = 'nfn', value = True):
        selcols = [left.checkbox(f'`{x}`', key = f'cbn_{i}') for i, x in enumerate(displayframe.columns)]
    else:
        selcols = [True for _ in range(len(displayframe.columns))]
    st.session_state['nsc'] = selcols

    choice = right.selectbox('Technique', ntechs)
    st.session_state['nt'] = choice

    ops[4].button('Normalise', use_container_width=True, on_click=normaliseframe)

#--------------------------------------------------------------------------------------------------------------------------




#--------------------------------------------------------------------------------------------------------------------------
#updating the dataframe



def savebutton():
    st.session_state['daframe'] = displayframe
    sidepart.info('Dataframe changes saved!')

def resetbutton():
    st.session_state['efn'] += 1
    if 'colchanges' in st.session_state:
        del st.session_state['colchanges']
    sidepart.info('Dataframe reset!')

def revertbutton():
    st.session_state['daframe'] = st.session_state['originalframecopy'].copy()
    st.session_state['efn'] += 1
    sidepart.info('Dataframe reverted to original!')


sbc, rbc = botside.columns(2)
sbc.button('Save changes', on_click=savebutton, use_container_width=True)
rbc.button('Reset changes', on_click=resetbutton, use_container_width=True)
botside.button('Revert to original file', on_click=revertbutton, use_container_width=True)

#--------------------------------------------------------------------------------------------------------------------------


#--------------------------------------------------------------------------------------------------------------------------
#final checks

if st.session_state['nonulls']:
    st.session_state['allgood'] = True
    botmain.success('**Dataset is all clean and set for plotting!**')



#--------------------------------------------------------------------------------------------------------------------------
