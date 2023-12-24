import streamlit as st
import pandas as pd
import seaborn as sns

# file : pd.DataFrame = st.session_state['daframe']
# st.download_button('Download file', file.to_csv(index = False), f'edited.csv')

st.title('Plots')

if ('allgood' not in st.session_state) or not (st.session_state['allgood']):
    st.write('Viable dataset not yet found; Upload and fix a dataset in the sidebar!')
    exit()


st.pyplot(sns.pairplot(st.session_state['daframe']))