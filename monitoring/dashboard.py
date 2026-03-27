import streamlit as st
import pandas as pd
import time
import matplotlib.pyplot as plt


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

        # bar chart endpoint/duration_ms

        fig, ax = plt.subplots()

        ax.bar(df['endpoint'], df['duration_ms'])
        ax.set_xlabel('Endpoint')
        ax.set_ylabel('Duration (ms)')
        ax.set_title('Performance by Endpoint')
        ax.tick_params(axis='x', rotation=45)
        plt.tight_layout()
        st.pyplot(fig)

        # Camembert chart showing success/error distribution

        success_count = len(df[df['status_code'] < 400])
        client_error_count = len(df[(df['status_code'] >= 400) & (df['status_code'] < 500)])
        server_error_count = len(df[df['status_code'] >= 500])

        fig, ax = plt.subplots()
        ax.pie([success_count, client_error_count, server_error_count], labels=['Success', 'Client Errors', 'Server Errors'], autopct='%1.1f%%')
        ax.set_title('Reliability')
        st.pyplot(fig)

        # activity curve over time

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        # Count requests per minute
        activity_over_time = df.resample('1T').size() 
        fig, ax = plt.subplots()
        ax.plot(activity_over_time.index, activity_over_time.values)
        ax.set_title('API Activity Over Time')
        ax.set_xlabel('Time')
        ax.set_ylabel('Number of Requests')
        st.pyplot(fig)

        # Refresh every 5 seconds
        time.sleep(5)