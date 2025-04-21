import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pornhub_api import PornhubApi
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# Initialize API
api = PornhubApi()

# Set page configuration
st.set_page_config(page_title="Video Content Analytics Dashboard", layout="wide")

# Dashboard title
st.title("Video Content Analytics Dashboard")
st.markdown("An analytics tool for content performance metrics")

# Sidebar for filters
st.sidebar.header("Filters")

# Search options
search_term = st.sidebar.text_input("Search Term", value="")

# Category selection
try:
    categories_list = ["amateur", "anal", "asian", "bbw", "big-dick", "big-tits", 
                      "blonde", "blowjob", "brunette", "compilation", "creampie", 
                      "cumshot", "ebony", "fetish", "handjob", "hardcore", "hd-porn",
                      "interracial", "latina", "lesbian", "milf", "pornstar", 
                      "pov", "reality", "redhead", "rough-sex", "solo-female", 
                      "squirt", "threesome", "toys"]
    selected_categories = st.sidebar.multiselect("Categories", categories_list)
except:
    st.sidebar.warning("Could not load categories. Using default options.")
    selected_categories = []

# Time period selection
period_options = ["weekly", "monthly", "yearly", "all"]
selected_period = st.sidebar.selectbox("Time Period", period_options)

# Ordering options
ordering_options = ["mostviewed", "newest", "rating"]
selected_ordering = st.sidebar.selectbox("Order By", ordering_options)

# Tag selection
try:
    common_tags = ["amateur", "anal", "asian", "babe", "big ass", "big tits", 
                  "black", "blonde", "blowjob", "brunette", "compilation", 
                  "creampie", "cumshot", "ebony", "hardcore", "hd", "interracial", 
                  "latina", "lesbian", "milf", "orgy", "pornstar", "pov", 
                  "rough", "solo", "squirt","threesome"]
    selected_tags = st.sidebar.multiselect("Tags", common_tags)
except:
    st.sidebar.warning("Could not load tags. Using default options.")
    selected_tags = []

# Apply filters button
filter_button = st.sidebar.button("Apply Filters")

# Function to fetch data and handle exceptions
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_data(search_term, categories, tags, ordering, period):
    try:
        # Apply filters safely
        kwargs = {}
        if categories:
            kwargs['category'] = categories[0] if len(categories) == 1 else random.choice(categories)
        if tags:
            kwargs['tags'] = tags
        if ordering:
            kwargs['ordering'] = ordering
        if period:
            kwargs['period'] = period
        
        # Search videos
        result = api.search.search_videos(search_term, **kwargs)
        
        # Convert to DataFrame
        videos_data = []
        
        # Check if result is iterable (as in the original code example from your document)
        if hasattr(result, '__iter__'):
            for video in result:
                video_dict = extract_video_data(video)
                videos_data.append(video_dict)
        # Check if result has __root__ attribute (based on your document structure)
        elif hasattr(result, '__root__'):
            video_dict = extract_video_data(result.__root__)
            videos_data.append(video_dict)
        # If result itself is a video object
        else:
            video_dict = extract_video_data(result)
            videos_data.append(video_dict)
            
        return pd.DataFrame(videos_data)
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        # Return empty DataFrame with expected columns
        return pd.DataFrame(columns=['title', 'duration', 'views', 'rating', 'publish_date', 'categories', 'tags', 'video_id'])

def extract_video_data(video):
    """Extract relevant data from a video object regardless of its structure"""
    video_dict = {}
    
    # Try to extract common attributes, handling different possible structures
    try:
        if hasattr(video, 'title'):
            video_dict['title'] = video.title
        elif hasattr(video, '__root__') and hasattr(video.__root__, 'title'):
            video_dict['title'] = video.__root__.title
        else:
            video_dict['title'] = "Unknown Title"
            
        # Extract other attributes with similar pattern
        for attr in ['duration', 'views', 'rating', 'video_id', 'publish_date']:
            if hasattr(video, attr):
                video_dict[attr] = getattr(video, attr)
            elif hasattr(video, '__root__') and hasattr(video.__root__, attr):
                video_dict[attr] = getattr(video.__root__, attr)
            else:
                video_dict[attr] = None
                
        # Handle complex attributes
        if hasattr(video, 'categories'):
            video_dict['categories'] = [c.category for c in video.categories] if hasattr(video.categories[0], 'category') else video.categories
        elif hasattr(video, '__root__') and hasattr(video.__root__, 'categories'):
            video_dict['categories'] = [c.category for c in video.__root__.categories] if hasattr(video.__root__.categories[0], 'category') else video.__root__.categories
        else:
            video_dict['categories'] = []
            
        if hasattr(video, 'tags'):
            video_dict['tags'] = [t.tag_name for t in video.tags] if hasattr(video.tags[0], 'tag_name') else video.tags
        elif hasattr(video, '__root__') and hasattr(video.__root__, 'tags'):
            video_dict['tags'] = [t.tag_name for t in video.__root__.tags] if hasattr(video.__root__.tags[0], 'tag_name') else video.__root__.tags
        else:
            video_dict['tags'] = []
            
    except Exception as e:
        st.warning(f"Error extracting video data: {str(e)}")
        
    return video_dict

# Alternative fetch method that works based on your example
def fetch_single_video_data():
    try:
        # Get a single video as shown in your example
        video = api.video.get_by_id("ph560b93077ddae")
        
        # Create dataframe from this single video
        video_dict = {}
        
        # First check if video has __root__ attribute
        if hasattr(video, '__root__'):
            video_data = video.__root__
        else:
            video_data = video
            
        # Extract attributes
        video_dict['title'] = getattr(video_data, 'title', "Unknown")
        video_dict['duration'] = getattr(video_data, 'duration', "0:00")
        video_dict['views'] = getattr(video_data, 'views', 0)
        video_dict['rating'] = getattr(video_data, 'rating', 0)
        video_dict['video_id'] = getattr(video_data, 'video_id', "unknown")
        video_dict['publish_date'] = getattr(video_data, 'publish_date', None)
        
        # Handle complex structures
        try:
            if hasattr(video_data, 'categories'):
                video_dict['categories'] = [c.category for c in video_data.categories]
            else:
                video_dict['categories'] = []
        except:
            video_dict['categories'] = []
            
        try:
            if hasattr(video_data, 'tags'):
                video_dict['tags'] = [t.tag_name for t in video_data.tags]
            else:
                video_dict['tags'] = []
        except:
            video_dict['tags'] = []
            
        return pd.DataFrame([video_dict])
    except Exception as e:
        st.error(f"Error fetching example video: {str(e)}")
        return pd.DataFrame(columns=['title', 'duration', 'views', 'rating', 'publish_date', 'categories', 'tags', 'video_id'])

# Main content area
if filter_button:
    with st.spinner("Fetching and analyzing data..."):
        # Try using filters
        df = fetch_data(search_term, selected_categories, selected_tags, selected_ordering, selected_period)
        
        # If no results or error, try showing example data
        if df.empty:
            st.warning("No results found with the current filters. Showing example data instead.")
            df = fetch_single_video_data()
        
        if not df.empty:
            # Display data summary
            st.subheader("Data Overview")
            st.write(f"Total videos found: {len(df)}")
            
            # Display sample of the data
            with st.expander("Preview Data"):
                st.dataframe(df[['title', 'views', 'rating', 'publish_date']].head(10))
            
            # Create dashboard with metrics and visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Performance Metrics")
                
                # Metrics
                total_views = df['views'].sum() if 'views' in df.columns else 0
                avg_rating = df['rating'].mean() if 'rating' in df.columns and not df['rating'].isna().all() else 0
                avg_views = df['views'].mean() if 'views' in df.columns and not df['views'].isna().all() else 0
                
                # Display metrics
                metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                metrics_col1.metric("Total Views", f"{total_views:,}")
                metrics_col2.metric("Avg. Rating", f"{avg_rating:.2f}/100")
                metrics_col3.metric("Avg. Views", f"{int(avg_views):,}")
                
                # Top viewed content
                st.subheader("Top Performing Content")
                if 'views' in df.columns and not df['views'].isna().all():
                    top_df = df.sort_values('views', ascending=False).head(5)
                    
                    fig = px.bar(
                        top_df,
                        x='views',
                        y='title',
                        orientation='h',
                        title='Top 5 Videos by Views',
                        labels={'views': 'Number of Views', 'title': 'Video Title'},
                        color='rating' if 'rating' in df.columns and not df['rating'].isna().all() else None,
                        color_continuous_scale=px.colors.sequential.Blues
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("View data not available for visualization.")
            
            with col2:
                # Rating distribution
                st.subheader("Rating Distribution")
                
                if 'rating' in df.columns and not df['rating'].isna().all():
                    fig = px.histogram(
                        df,
                        x='rating',
                        nbins=20,
                        title='Distribution of Ratings',
                        labels={'rating': 'Rating Score', 'count': 'Number of Videos'},
                        color_discrete_sequence=['#3366cc']
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No rating data available for visualization.")
                
                # Publish date analysis if available
                if 'publish_date' in df.columns and not df['publish_date'].isna().all():
                    # Convert to datetime if needed
                    if not pd.api.types.is_datetime64_any_dtype(df['publish_date']):
                        try:
                            df['publish_date'] = pd.to_datetime(df['publish_date'])
                        except:
                            pass
                    
                    if pd.api.types.is_datetime64_any_dtype(df['publish_date']):
                        # Create timeseries of video count
                        df['publish_month'] = df['publish_date'].dt.strftime('%Y-%m')
                        monthly_counts = df.groupby('publish_month').size().reset_index(name='count')
                        
                        fig = px.line(
                            monthly_counts,
                            x='publish_month',
                            y='count',
                            title='Video Publication Trend',
                            labels={'publish_month': 'Month', 'count': 'Number of Videos'},
                            markers=True
                        )
                        st.plotly_chart(fig, use_container_width=True)
            
            # Tag and Category Analysis
            st.subheader("Content Classification Analysis")
            col3, col4 = st.columns(2)
            
            with col3:
                # Extract all tags and count frequencies
                if 'tags' in df.columns and not all(pd.isna(df['tags'])):
                    all_tags = []
                    for tags_list in df['tags']:
                        if isinstance(tags_list, list):
                            all_tags.extend(tags_list)
                    
                    if all_tags:
                        tag_counts = pd.Series(all_tags).value_counts().head(10)
                        
                        fig = px.bar(
                            x=tag_counts.values,
                            y=tag_counts.index,
                            orientation='h',
                            title='Top 10 Tags',
                            labels={'x': 'Count', 'y': 'Tag'},
                            color=tag_counts.values,
                            color_continuous_scale=px.colors.sequential.Viridis
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No tag data available for visualization.")
                else:
                    st.info("No tag data available for visualization.")
            
            with col4:
                # Extract all categories and count frequencies
                if 'categories' in df.columns and not all(pd.isna(df['categories'])):
                    all_categories = []
                    for categories_list in df['categories']:
                        if isinstance(categories_list, list):
                            all_categories.extend(categories_list)
                    
                    if all_categories:
                        category_counts = pd.Series(all_categories).value_counts().head(10)
                        
                        fig = px.pie(
                            names=category_counts.index,
                            values=category_counts.values,
                            title='Category Distribution',
                            hole=0.4,
                            color_discrete_sequence=px.colors.qualitative.Pastel
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No category data available for visualization.")
                else:
                    st.info("No category data available for visualization.")
            
            # Correlation between views and ratings
            if 'views' in df.columns and 'rating' in df.columns and not df['views'].isna().all() and not df['rating'].isna().all():
                st.subheader("Correlation Analysis")
                
                fig = px.scatter(
                    df,
                    x='views',
                    y='rating',
                    title='Correlation: Views vs. Rating',
                    labels={'views': 'Number of Views', 'rating': 'Rating Score'},
                    color='rating',
                    color_continuous_scale=px.colors.sequential.Plasma,
                    size='views',
                    size_max=30,
                    hover_data=['title']
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Download data option
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Download Data as CSV",
                csv,
                "video_analytics_data.csv",
                "text/csv",
                key='download-csv'
            )
            
        else:
            st.warning("No data available. Please check your API connection or try different filters.")
else:
    # Initial dashboard state
    st.info("Use the filters in the sidebar and click 'Apply Filters' to analyze content data.")
    
    # Dashboard explanation
    st.markdown("""
    ## Dashboard Features
    
    This analytics tool provides insights into video content performance with the following features:
    
    - **Content Search & Filtering**: Filter by keywords, categories, tags, and time periods
    - **Performance Metrics**: View aggregate statistics on content performance
    - **Top Content Analysis**: Identify the highest-performing content by views
    - **Rating Distribution**: Analyze the distribution of content ratings
    - **Publication Trends**: Track content publication patterns over time
    - **Tag & Category Analysis**: Understand content classification patterns
    - **Correlation Analysis**: Explore relationships between metrics
    
    Adjust the filters in the sidebar and click "Apply Filters" to begin your analysis.
    """)

# Footer
st.markdown("---")
st.markdown("Analytics Dashboard | Content Performance Metrics")
