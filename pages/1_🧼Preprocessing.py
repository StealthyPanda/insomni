import streamlit as st
import pandas as pd
import eda
from typing import List, Tuple

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

def removedata():
    del st.session_state['daframe']

if 'daframe' in st.session_state:
    st.sidebar.button('Remove dataset', on_click=removedata, use_container_width=True)

#--------------------------------------------------------------------------------------------------------------------------


#--------------------------------------------------------------------------------------------------------------------------
#main display section
if 'daframe' not in st.session_state:
    st.markdown('##### Start by uploading a dataset to work on in the sidebar.')
    exit()

originalframe : pd.DataFrame = st.session_state['daframe']

mainpart, sidepart = st.columns([7, 3])
botmain, botside = st.columns([7, 3])

# if 'colchanges' not in st.session_state:
displayframe = mainpart.data_editor(
    originalframe if 'colchanges' not in st.session_state else st.session_state['colchanges'],
    use_container_width=True,
    key = f"editedframe{st.session_state['efn']}",
    num_rows='dynamic',
    # height=700,
)

nnulls = displayframe.isnull().sum().sum()


#sidepart stuff
st.session_state['nonulls'] = (nnulls == 0)
if nnulls > 0:
    botmain.warning(f'There are **{displayframe.isnull().sum().sum()}** null values remaining in the dataframe.')
else:
    botmain.success('No null values in the dataframe!')
#--------------------------------------------------------------------------------------------------------------------------

sidepart.markdown('*Tip: use Shift + scroll to view all the operations below*')
ops = sidepart.tabs([
    'Clean Column Names',
    'Drop Nulls',
    'Cast Types',
    'Fill Nulls',
    'Normalise',
    'Noise',
    'Remove Columns',
    'Encode/Categorise',
])





#--------------------------------------------------------------------------------------------------------------------------
#column ops

def updatenames():
    global displayframe
    if 'colchanges' not in st.session_state:
        st.session_state['colchanges'] = displayframe.copy()
    cleaned = []
    for each in displayframe.columns:
        if each in st.session_state['ccnc']:
            cleaned.append(eda.cleancolumnnames([each])[0])
        else:
            cleaned.append(each)

    st.session_state['colchanges'].columns = cleaned
    sidepart.info('Updated names!')

def dropnulls():
    global displayframe
    mask = st.session_state['dnsc']
    newframe, ndrops = eda.dropnulls(displayframe, mask)
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
    cols = st.session_state['fnsc']
    st.session_state['colchanges'], s, f = eda.fillmissing(displayframe, st.session_state['defval'], cols)
    ops[3].info(f'Filled null values; **{s}** successful fills and **{f}** failed fills.')


def normaliseframe():
    global displayframe
    try:
        newframe = eda.normalise(displayframe, st.session_state['ntsc'], st.session_state['ntc'])
    except TypeError:
        ops[4].error('Cannot normalise given set of fields!')
        return
    st.session_state['colchanges'] = newframe
    ops[4].info('Fields normalised!')

def getcolumnsold(parent : st.container, colprompt : str, frame : pd.DataFrame, keyheader : str) -> Tuple[List[str], st.container]:
    cols = list(frame.columns)
    lcols = len(cols)

    selected = []

    left, right = parent.columns(2)
    left.write(colprompt)
    selcols = [True for _ in range(len(frame.columns))]

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
    if not parent.checkbox('*All fields*', key = f'{keyheader}_afcb'):
        options = parent.multiselect(colprompt, frame.columns, key = f'{keyheader}_multisel')
        return (options, None)
    else:
        return (frame.columns, None)


def removenoise():
    global displayframe

    tols = st.session_state['tols']

    if type(tols) == str:
        tols = int(tols[0])
        tolsframe = displayframe.describe().loc['std']
        tolsframe = tolsframe.multiply(tols)
        tols = tolsframe.to_dict()

    try:
        frame, n = eda.reducenoise(displayframe, tols, st.session_state['noisec'])
    except ValueError:
        ops[5].error('Couldnt perform noise reduction on the set of columns!')
        return
    
    st.session_state['colchanges'] = frame
    ops[5].info(f'Dropped **{n}** rows successfully!')





def removecolumns():
    global displayframe
    try:
        newframe = displayframe.drop(columns=st.session_state['rcc'])
    except:
        ops[6].error('Couldnt remove specified columns')
        return
    
    st.session_state['colchanges'] = newframe
    ops[6].info(f'Successfully dropped **{(st.session_state["rcc"])}**!')


def encodecolumns():
    global displayframe
    try:
        newframe, mapping = eda.categorise(displayframe, st.session_state['ecc'])
    except:
        ops[7].error('Couldn\'t encode specified columns')
        return
    
    # displayframe[newframe.columns[0]] = newframe
    for col in newframe.columns:
        displayframe[col] = newframe[col]
    st.session_state['colchanges'] = displayframe
    ops[7].info(f'Successfully encoded the columns **{(st.session_state["ecc"])}**!')
    ops[7].info('Mapping/encoding:')
    ops[7].write(mapping)







#Clean column names
with ops[0]:
    cols, right = getcolumns(
        ops[0], 'Select columns to clean:', displayframe, 'ccn'
    )

    st.session_state['ccnc'] = cols

    ops[0].button('Update names', use_container_width=True, on_click=updatenames)

#dropping nulls
with ops[1]:
    selcols, right = getcolumns(
        ops[1], 'Select columns to drop nulls:', displayframe, 'dn'
    )
    st.session_state['dnsc'] = selcols
    ops[1].button('Drop null valued rows', use_container_width=True, on_click=dropnulls)

#Casting types
with ops[2]:
    field = ops[2].selectbox('Select a field', displayframe.columns, index = None)
    if field is not None:
        ops[2].info(f"'`{field}`' field is of type  '`{displayframe[field].dtype}`'")
    castto = ops[2].selectbox('Cast to...', types.keys(), index = None)
    if (field is not None) and (castto is not None):
        st.session_state['ctc'] = field
        st.session_state['ctt'] = castto
        ops[2].button('Cast', use_container_width=True, on_click=castfield)


#filling null values
with ops[3]:
    selcols, right = getcolumns(
        ops[3], 'Fill nulls in:', displayframe, 'fn'
    )
    st.session_state['fnsc'] = selcols

    right = right if right is not None else ops[3]

    choice = right.selectbox('Value type', ['number', 'string', 'date/time'])

    if choice == 'number':
        st.session_state['defval'] = right.number_input('Enter default value')
    elif choice == 'string':
        st.session_state['defval'] = right.text_input('Enter default value')
    elif choice == 'date/time':
        st.session_state['defval'] = right.date_input('Enter default value')

    ops[3].button('Fill null values', use_container_width=True, on_click=fillnulls)


#normalising
with ops[4]:
    cols, right = getcolumns(
        ops[4], 'Columns to normalise:', displayframe, 'nt'
    )

    st.session_state['ntsc'] = cols

    if right is not None:
        st.session_state['ntc'] = right.selectbox('Technique', ntechs)
    else:
        st.session_state['ntc'] = ops[4].selectbox('Technique', ntechs)

    ops[4].button('Normalise', use_container_width=True, on_click=normaliseframe)



#noise
with ops[5]:
    cols, right = getcolumns(
        ops[5], 'Select columns to filter with:', displayframe, 'rn'
    )

    st.session_state['noisec'] = cols

    right = right if right is not None else ops[5]

    if right.checkbox(
        'Manual Tolerances',
        help = 'Set tolerance value for each individual field (normally standard deviation of each field)'
    ):
        tols = displayframe.describe().loc['std']
        tols.name = 'Tolerances'
        tols.index.name = 'Fields'
        tols = right.data_editor(
            tols, use_container_width=True, hide_index=False
        )

        st.session_state['tols'] = tols.to_dict()

    else:
        val = right.radio('Select tolerance:', ['1σ', '2σ', '3σ'], horizontal=True)
        st.session_state['tols'] = val
    
    ops[5].button('Reduce noise', use_container_width=True, on_click=removenoise)


#Remove columns
with ops[6]:
    cols, right = getcolumns(
        ops[6], 'Select columns to remove:', displayframe, 'rc'
    )

    st.session_state['rcc'] = cols
    ops[6].button('Remove columns', use_container_width=True, on_click=removecolumns)


#encoding columns
with ops[7]:
    cols, right = getcolumns(
        ops[7], 'Select columns to encode:', displayframe, 'ec'
    )

    st.session_state['ecc'] = cols
    ops[7].button('Encode columns', use_container_width=True, on_click=encodecolumns)




#--------------------------------------------------------------------------------------------------------------------------




#--------------------------------------------------------------------------------------------------------------------------
#updating the dataframe



def savebutton():
    st.session_state['daframe'] = displayframe.copy()
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
