import streamlit as st
import pandas as pd
import time


st.set_page_config(page_title="Dashboard", layout="wide")

placeholder = st.empty()

while True:
    with placeholder.container():
        st.title('Order API Live Monitoring Dashboard')
        df = pd.read_csv('audit_log.csv')
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        col1, col2, col3 = st.columns(3)

        with col1:
            total_req = len(df)
            st.metric(label='Total Requests', value=total_req)
        
        with col2:
            error_count = len(df[df['status_code'] >= 500])
            error_rate = (error_count / total_req) * 100
            if error_rate > 10:
                st.metric('System Status', f'{error_rate:.1f}%', delta='CRITICAL', delta_color='inverse')
            else:
                st.metric('System Status', f'{error_rate:.1f}%', delta='STABLE', delta_color='normal')

        with col3:
            avg_lat = round(df['duration_ms'].mean(), 2)
            st.metric('Average Latency (ms)', f'{avg_lat} ms')

        st.subheader('API Activity')
        # TODO: replace with st.line_chart when altair supports Python 3.14 
        st.dataframe(df[['timestamp', 'endpoint', 'duration_ms', 'status_code']],
                     use_container_width=True
        )
        

        # Show the last 10 events in a table
        st.subheader('Latest events') 
        st.dataframe(df.tail(10), use_container_width=True)

        # Refresh every 5 seconds
        time.sleep(5)