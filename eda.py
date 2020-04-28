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

def run():
    df = get_df()
    
    if df is not None:
        st.sidebar.title('Welcome!')
        st.sidebar.image('img/logo.png', width=280)

        df_info = pd.DataFrame({'names': df.columns, 'types': df.dtypes, 'NA #': df.isna().sum(), 'NA %': (df.isna().sum() / df.shape[0]) * 100})

        st.sidebar.subheader('Check at least one below and watch magic happen:')
        if st.sidebar.checkbox('Quantitative Analysis'):
            quantitative_analysis(df, df_info)
        
        if st.sidebar.checkbox('Data Visualization'):
            data_visualization(df, df_info)

        if st.sidebar.checkbox('Missing Values'):
            missing_data(df, df_info)

        about()

def quantitative_analysis(df, df_info):
    st.subheader("Quantitative Analysis")

    view = st.radio('View:', ('Head', 'Tail', 'First nth rows'))
    if view == 'Head':
        st.write(df.head())
    elif view == 'Tail':
        st.write(df.tail())
    elif view == 'First nth rows':
        n_rows = st.slider('How many rows?', min_value=1, max_value=df.shape[0])
        st.dataframe(df.head(n_rows))

    data_dim = st.radio('What dimension do you want to show?', ('Rows', 'Columns'))
    if data_dim == 'Rows':
        st.write('Showing length of rows:', df.shape[0])
    if data_dim == 'Columns':
        st.write('Showing length of columns:', df.shape[1])

    if st.checkbox('Columns info'):
        st.write(df_info['types'].value_counts())
        st.write('int64 columns:', ', '.join(df_info[df_info['types'] == 'int64']['names'].tolist()))
        st.write('float64 columns:', ', '.join(df_info[df_info['types'] == 'float64']['names'].tolist()))
        st.write('object columns:', ', '.join(df_info[df_info['types'] == 'object']['names'].tolist()))

    if st.checkbox('Numeric summary'):
        st.table(df.describe())

def data_visualization(df, df_info):
    st.subheader('Data Visualization')

    type_of_plot = st.selectbox('Select type of plot:', ['area', 'bar', 'line', 'hist', 'box', 'kde', 'correlation'])
    if type_of_plot != 'correlation':
        selected_columns_names = st.multiselect('Select columns to plot:', df.columns.tolist())

    if st.button("Generate plot"):
        if type_of_plot != 'correlation':
            st.success("Generating customizable plot of {} for {}".format(type_of_plot, ', '.join(selected_columns_names)) + '.')

        if type_of_plot == 'area':
            cust_data = df[selected_columns_names]
            st.area_chart(cust_data)

        elif type_of_plot == 'bar':
            cust_data = df[selected_columns_names]
            st.bar_chart(cust_data)

        elif type_of_plot == 'line':
            cust_data = df[selected_columns_names]
            st.line_chart(cust_data)

        elif type_of_plot == 'correlation':
            corr = df.corr()
            sns.heatmap(corr, 
                cmap='viridis', vmax=1.0, vmin=-1.0, linewidths=0.1,
                annot=True, annot_kws={"size": 8}, square=True);
            st.pyplot()

        elif type_of_plot:
            cust_plot= df[selected_columns_names].plot(kind=type_of_plot)
            st.pyplot()

def missing_data(df, df_info):
    st.subheader('Missing Values')

    st.table(df_info[df_info['NA #'] != 0][['types', 'NA %']])
    st.bar_chart(df_info['NA %'].sort_values(ascending=False))
    
    columns_numeric_na = df_info[(df_info['NA %'] > 0) & (df_info['types'] != 'object')]['names'].values.tolist()
    columns_selected = []

    if st.checkbox('Handle NA values'):
        df_handled = df.copy()

        method = st.radio('Choose one method:', ('Mean', 'Median', 'Mode', 'Drop rows'))
        if method == 'Mean':
            columns_selected = st.multiselect('Select numeric columns:', columns_numeric_na)
            if columns_selected:
                st.write(df[columns_selected].mean().rename(method))
                df_handled[columns_selected] = df[columns_selected].fillna(df[columns_selected].mean())
                for col in columns_selected:
                    df_handled[col] = df[col].fillna(df[col].mean())
        elif method == 'Median':
            columns_selected = st.multiselect('Select numeric columns:', columns_numeric_na)
            if columns_selected:
                st.write(df[columns_selected].median().rename(method))
                for col in columns_selected:
                    df_handled[col] = df[col].fillna(df[col].median())
        elif method == 'Mode':
            columns_selected = st.multiselect('Select columns:', df_info[df_info['NA #'] != 0]['names'].values.tolist())
            if columns_selected:
                for col in columns_selected:
                    st.write(f'Mode {col}:', df[col].mode()[0])
                    df_handled[col] = df[col].fillna(df[col].mode()[0])
        elif method == 'Drop rows':
            columns_selected = st.multiselect('Select columns:', df_info[df_info['NA #'] != 0]['names'].values.tolist())
            if columns_selected:
                df_handled.dropna(subset=columns_selected, inplace=True)

        if columns_selected:
            if st.button("Apply"):
                st.success('Data input!')

                df_handled_info = pd.DataFrame({'names': df_handled.columns, 'types': df_handled.dtypes, 
                                        'NA #': df_handled.isna().sum(), 'NA %': (df_handled.isna().sum() / df_handled.shape[0]) * 100})
                st.table(df_handled_info)

                st.markdown(get_table_download_link(df_handled), unsafe_allow_html=True)

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

def about():
    st.sidebar.title('About')    
    st.sidebar.subheader('Exploratory Data Analysis App')
    st.sidebar.markdown(
        '''
        This app is a data explorer tool to help data scientists get their dataset first insights.

        It was developed using Streamlit, an open-source app framework for Machine Learning and Data Science teams.

        You can check the code on my [GitHub](https://github.com/bosamatheus/eda).
        Feel free to reach out for collab! :grin:
        '''
    )
    st.sidebar.image('img/matheusbosa.jpg', width=200)
    st.sidebar.markdown('Developed by **Matheus Bosa.**')
    st.sidebar.markdown('Bachelor degree in Electrical Engineering from the Federal University of Paraná (UFPR).')
    st.sidebar.markdown('My [LinkedIn](https://www.linkedin.com/in/matheusbosa/) and [Portfolio](https://bosamatheus.github.io/).')

def main():
    st.title('Exploratory Data Analysis App :mag:')
    run()
    
if __name__ == '__main__':
    main()
