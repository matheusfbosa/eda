import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('whitegrid')
import base64
import time

def get_df(df=None, encode='utf-8', delimiter=','):
    read_cache_csv = st.cache(pd.read_csv, allow_output_mutation=True)

    if st.checkbox('Read options'):
        encode = st.selectbox('Encoding method:', ('utf-8', 'ISO-8859-1', 'us-ascii'))
        delimiter = st.selectbox('Delimiter:', (',', ';', '.', ' ', '|'))
    
    file = st.file_uploader('Upload your file (.csv):', type='csv')
    if file is not None:
        df = read_cache_csv(file, encoding=encode, sep=delimiter)
    
    return df

def sidebar():
    st.sidebar.title('Welcome!')
    st.sidebar.title('Project')
    st.sidebar.subheader('Exploratory Data Analysis App :')
    st.sidebar.markdown(
        '''
        This app is a data explorer tool to help data scientists get their dataset first insights.
        Code is available on [GitHub](https://github.com/bosamatheus/eda).
        '''
    )
    st.sidebar.title('About')    
    st.sidebar.image('img/matheusbosa.jpg', width=200)
    st.sidebar.markdown('Developed by **Matheus Bosa.**')
    st.sidebar.markdown('Bachelor degree in Electrical Engineering from the Federal University of Paraná (UFPR).')
    st.sidebar.markdown('My [LinkedIn](https://www.linkedin.com/in/matheusbosa/) and [Portfolio](https://bosamatheus.github.io/).')
    

def run():
    st.subheader('Preparations')
    df = get_df()
    sidebar()
    
    if df is not None:
        st.subheader('Analysis')
        df_info = pd.DataFrame({'names': df.columns, 'types': df.dtypes, 'NA #': df.isna().sum(), 'NA %': (df.isna().sum() / df.shape[0]) * 100})

        if st.checkbox('View data'):
            view = st.radio('View:', ('Head', 'Tail', 'First nth rows'))
            if view == 'Head':
                st.write(df.head())
            elif view == 'Tail':
                st.write(df.tail())
            elif view == 'First nth rows':
                n_rows = st.slider('How many rows?', min_value=1, max_value=df.shape[0])
                st.dataframe(df.head(n_rows))

        # Dimensions
        data_dim = st.radio('What dimension do you want to show?', ('Rows', 'Columns'))
        if data_dim == 'Rows':
            st.write('Showing length of rows:', df.shape[0])
        if data_dim == 'Columns':
            st.write('Showing length of columns:', df.shape[1])

        columns_view = st.radio('Columns info:', ('Names', 'Data types'))
        if columns_view == 'Names':
            st.write(', '.join(df.columns.tolist()))
        elif columns_view == 'Data types':
            st.write(df_info['types'].value_counts())
            st.write('int64 columns:', ', '.join(df_info[df_info['types'] == 'int64']['names'].tolist()))
            st.write('float64 columns:', ', '.join(df_info[df_info['types'] == 'float64']['names'].tolist()))
            st.write('object columns:', ', '.join(df_info[df_info['types'] == 'object']['names'].tolist()))

        if st.checkbox('Numeric summary'):
            st.table(df.describe())
        
        st.subheader('Data Visualization')
        vis = st.radio('Plot:', ('Histogram', 'Barplot', 'Correlation'))
        if vis == 'Histogram':
            # TODO
            pass
        elif vis == 'Barplot':
            # TODO
            pass
        elif vis == 'Correlation':
            corr = df.corr()
            sns.heatmap(corr, 
                cmap='viridis', vmax=1.0, vmin=-1.0, linewidths=0.1,
                annot=True, annot_kws={"size": 8}, square=True);
            st.pyplot()

        st.subheader('Missing Data')
        if st.checkbox('NA values'):
            st.write(df_info[df_info['NA #'] != 0][['types', 'NA %']])
            st.bar_chart(df_info['NA %'].sort_values(ascending=False))
        if st.checkbox('Drop NA values'):
            # TODO
            pass
        if st.checkbox('Inpute numeric missing data'):
            inpute_numeric_na(df, df_info)

def inpute_numeric_na(df, df_info):
    series_aux = df_info.query('(types == "float64" | types == "int64")')['NA #'] != 0
    columns_numeric_na = series_aux[series_aux].index.tolist()
    columns_input = st.multiselect('Select columns with NA values:', columns_numeric_na)

    if columns_input:
        method = st.radio('Choose one method:', ('Mean', 'Median'))
        
        if method == 'Mean':
            st.write(method + ':', df[columns_input].mean())
            df_input = df[columns_input].fillna(df[columns_input].mean())
        elif method == 'Median':
            st.write(method + ':', df[columns_input].median())
            df_input = df[columns_input].fillna(df[columns_input].median())

        df_input = pd.DataFrame({'names': df_input.columns, 'types': df_input.dtypes, 
                                'NA #': df_input.isna().sum(), 'NA %': (df_input.isna().sum() / df_input.shape[0]) * 100})

        if method:
            st.success('Data input!')
            st.markdown(get_table_download_link(df_input), unsafe_allow_html=True)

def get_table_download_link(df):
    '''
    Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    '''
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode() # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}">Download .csv file</a>'
    return href

def main():
    st.title('Exploratory Data Analysis App')
    run()
    
if __name__ == '__main__':
    main()
