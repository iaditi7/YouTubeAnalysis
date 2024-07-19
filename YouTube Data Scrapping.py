from googleapiclient.discovery import build
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
#from videosId import video_data, top10_videos, videos_per_month, sort_order

api_key = 'AIzaSyD3nWTz94gvdbKxJgBXJwqxnymaG7niuQ4'
channel_ids = ['UCnz-ZXXER4jOvuED5trXfEA',
              'UC8LUT6Qn7MSvPQPM8ZJsW8g',
              'UC7cs8q-gJRlGwj4A8OmCmXg',
              'UC2UXDak6o7rBm23k3Vv5dww',
              'UCiT9RITQ9PW6BhXK0y2jaeg',
              'UCLLw7jmFsvfIVaUFsLs8mlQ',
            ]

youtube = build('youtube', 'v3', developerKey=api_key)

#Function to get channel statistic

def get_channel_stats(youtube, channel_ids):
    all_data = []
    request = youtube.channels().list(
        part='snippet,contentDetails,statistics',
        id=','.join(channel_ids))  # convert the list into string that will be comma separated
    response = request.execute()

    for i in range(len(response['items'])):
        data = dict(Channel_name=response['items'][i]['snippet']['title'],
                    Subscribers=response['items'][i]['statistics']['subscriberCount'],
                    Views=response['items'][i]['statistics']['viewCount'],
                    Total_videos=response['items'][i]['statistics']['videoCount'],
                    Playlist_id=response['items'][i]['contentDetails']['relatedPlaylists']['uploads']
                    )
        all_data.append(data)  # appending all result one by one as a single result

    return all_data

channel_statistics = get_channel_stats(youtube, channel_ids) #putting result in a variable

channel_data = pd.DataFrame(channel_statistics) #loading into dataframe

print(channel_data)

# --Converting the data type
channel_data['Subscribers'] = pd.to_numeric(channel_data['Subscribers'])
channel_data['Views'] = pd.to_numeric(channel_data['Views'])
channel_data['Total_videos'] = pd.to_numeric(channel_data['Total_videos'])

channel_data.dtypes

sns.set(rc={'figure.figsize':(10,8)})
ax = sns.barplot(x='Channel_name', y='Subscribers', data=channel_data, hue='Channel_name',  palette='Set3')
plt.show()

ax = sns.barplot(x='Channel_name', y='Views', data=channel_data, hue='Channel_name',  palette='Set3')
plt.show()


#-- Function to get Video Details
playlist_id = channel_data.loc[channel_data['Channel_name']=='Ken Jee', 'Playlist_id'].iloc[0]


def get_video_id(youtube, playlist_id):
    request = youtube.playlistItems().list(
        part='contentDetails',
        playlistId=playlist_id,
        maxResults=50)
    response = request.execute()

    video_ids = []

    for i in range(len(response['items'])):
        video_ids.append(response['items'][i]['contentDetails']['videoId'])

    next_page_token = response.get('nextPageToken')
    more_pages = True

    while more_pages:
        if next_page_token is None:
            more_pages = False
        else:
            request = youtube.playlistItems().list(
                part='contentDetails',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token)
            response = request.execute()

            for i in range(len(response['items'])):
                video_ids.append(response['items'][i]['contentDetails']['videoId'])

            next_page_token = response.get('nextPageToken')

    return video_ids

video_ids = get_video_id(youtube, playlist_id)

#--Function to get Video Details

def get_video_details(youtube, video_ids):
    all_video_stats = []

    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(
            part='snippet,statistics',
            id=','.join(video_ids[i:i + 50]))
        response = request.execute()

        for video in response['items']:
            video_stats = dict(Title=video['snippet']['title'],
                               Published_date=video['snippet']['publishedAt'],
                               Views=video['statistics']['viewCount'],
                               Likes=video['statistics']['likeCount'],
                               Comments=video['statistics']['commentCount']
                               )
            all_video_stats.append(video_stats)

    return all_video_stats

video_details = get_video_details(youtube, video_ids)
video_data = pd.DataFrame(video_details)

video_data['Published_date'] = pd.to_datetime(video_data['Published_date']).dt.date
video_data['Views'] = pd.to_numeric(video_data['Views'])
video_data['Likes'] = pd.to_numeric(video_data['Likes'])
video_data['Comments'] = pd.to_numeric(video_data['Comments'])

print(video_data)


# Top 10 content details of a particular channel that is selected in the playlist_id

top10_videos = video_data.sort_values(by = 'Views', ascending = False).head(10)

ax1 = sns.barplot(x='Views', y='Title', hue='Title', data=top10_videos, palette='Set3', legend=False)
plt.show()

video_data['Month'] = pd.to_datetime(video_data['Published_date']).dt.strftime('%b') #Extracted month from published date

videos_per_month = video_data.groupby('Month', as_index=False).size() #Extracted videos posted per month

sort_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

videos_per_month.index = pd.CategoricalIndex(videos_per_month['Month'], categories=sort_order, ordered=True)
videos_per_month.sort_index()

ax2 = sns.barplot(x='Month', y= 'size', data=videos_per_month, palette='viridis', hue='Month', legend= False)
plt.show()

