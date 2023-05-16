import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from apify_client import ApifyClient

# Function to fetch data
def fetch_data(url):
    # Initialize the ApifyClient with your API token
    client = ApifyClient("apify_api_WumdvyLSNxeUxGoK7wjX5UKEngQW1R1tdkAU")
    # Prepare the actor input
    run_input = {
        "listUrls": [{ "url": url }],
        "propertyUrls": [],
        "proxy": { "useApifyProxy": True },
    }

    # Run the actor and wait for it to finish
    run = client.actor("dhrumil/propertyfinder-scraper").call(run_input=run_input)
    results = []

    # Fetch and print actor results from the run's dataset (if there are any)
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        results.append(item)

    df = pd.DataFrame(results)

    df.drop(columns=['completionDate', 'id', 'agentBrn', 'completionDate', 'images','freehold','priceDuration','propertyType','reference','url','title', 'type'], inplace=True)
    df.propertyAge.replace(np.nan,'off plan', inplace=True)
    df['sizeMin'] = df.sizeMin.str.extract('(\d+(?:,\d+)?)', expand=False).str.replace(',', '').astype('int')
    df['latitude'] = df.coordinates.apply(lambda x:x.get('latitude'))
    df['longitude'] = df.coordinates.apply(lambda x:x.get('longitude'))
    
    return df

# Streamlit app
def main():    
    st.title('Property Finder Data Dashboard')
    st.markdown("""
    This application provides an interactive dashboard for real estate data collected from Property Finder through its API. 
    The data is fetched in real time based on a URL input by the user.

    The main goal of the dashboard is to present key real estate metrics or Key Performance Indicators (KPIs) 
    in an easy-to-understand way. These KPIs include metrics such as average price, most common number of bedrooms, 
    most common number of bathrooms, most common broker, and average property size.

    The application also provides visualizations of the data, including distributions of prices, number of bedrooms, 
    number of bathrooms, and geographical locations of properties. These visualizations can help users better understand 
    the data and identify trends or patterns.
    
    The source code for this application is available on [GitHub](https://github.com/alifadl009/realestate).
    """)    
    st.sidebar.header('Input URL')
    url = st.sidebar.text_input('Enter the URL: ')
    
    if url:
        with st.spinner('Loading data... this may take a while.'):
            df = fetch_data(url)
        price = df['price']
        latitude = df['latitude']
        longitude = df['longitude']
        
        st.header('Property Data')
        st.write(df)
        st.subheader('Shape of the Data')
        st.write(f'The dataset contains {df.shape[0]} rows and {df.shape[1]} columns.')

        # KPIs
        st.header('Key Performance Indicators')
        st.markdown(f'**Average Price:** {df["price"].mean():.2f}')
        st.markdown(f'**Most Common Number of Bedrooms:** {df["bedrooms"].mode()[0]}')
        st.markdown(f'**Most Common Number of Bathrooms:** {df["bathrooms"].mode()[0]}')
        st.markdown(f'**Most Common Broker:** {df["broker"].mode()[0]}')
        st.markdown(f'**Average Property Size:** {df["sizeMin"].mean():.2f}')


        # Visualizations
        st.header('Visualizations')
        fig1 = px.histogram(df, x="price", nbins=50, title='Price distribution')
        st.plotly_chart(fig1)

        fig2 = px.histogram(df, x="bedrooms", nbins=20, title='Bedrooms distribution')
        st.plotly_chart(fig2)

        fig3 = px.histogram(df, x="bathrooms", nbins=20, title='Bathrooms distribution')
        st.plotly_chart(fig3)

        fig4 = go.Figure(go.Scattermapbox(
            lat=latitude,
            lon=longitude,
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=14
            ),
            text=price,  
            hoverinfo='text'
        ))

        fig4.update_layout(
            autosize=True,
            hovermode='closest',
            mapbox=dict(
                bearing=0,
                center=dict(
                    lat=latitude.mean(),
                    lon=longitude.mean()
                ),
                pitch=0,
                zoom=10,
                style='open-street-map'
            ),
        )

        st.plotly_chart(fig4)

if __name__ == "__main__":
    main()





