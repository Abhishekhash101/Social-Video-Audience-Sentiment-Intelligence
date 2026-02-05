from src.logger import logging
from src.exception import CustomException
from dataclasses import dataclass
import os
import sys
from googleapiclient.discovery import build
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

api_key_provide = os.getenv('YOUTUBE_API')


@dataclass
class DataIngestionConfig:
    raw_data_path: str = os.path.join("artifacts", "raw_data.csv")


class DataIngestion:

    def __init__(self, api_key):
        self.ingestion_config = DataIngestionConfig()
        self.api_key = api_key

        try:
            self.youtube = build('youtube', 'v3', developerKey=api_key)
            logging.info("Youtube API client Initialized successfully")
        except Exception as e:
            logging.error(e)
            raise CustomException(e, sys)

    def fetch_comments(self, video_id, max_results=50):

        logging.info(f"Started fetching comments for Video ID: {video_id}")
        comments_data = []

        try:
            request = self.youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=100,
                textFormat="plainText"
            )

            fetched_count = 0

            while request and fetched_count < max_results:
                response = request.execute()

                for item in response['items']:
                    comment = item['snippet']['topLevelComment']['snippet']

                    comments_data.append({
                        'author': comment['authorDisplayName'],
                        'comment': comment['textDisplay'],
                        'date': comment['publishedAt'],
                        'like_count': comment['likeCount']
                    })

                fetched_count += len(response['items'])

                if 'nextPageToken' in response and fetched_count < max_results:
                    request = self.youtube.commentThreads().list(
                        part="snippet",
                        videoId=video_id,
                        maxResults=100,
                        pageToken=response['nextPageToken'],
                        textFormat="plainText"
                    )
                else:
                    break

            df = pd.DataFrame(comments_data)

            os.makedirs(os.path.dirname(self.ingestion_config.raw_data_path), exist_ok=True)

            df.to_csv(self.ingestion_config.raw_data_path, index=False)

            logging.info("Data saved successfully")

            return self.ingestion_config.raw_data_path

        except Exception as e:
            logging.error("Error occurred while fetching comments")
            raise CustomException(e, sys)


if __name__ == "__main__":

    API_KEY = api_key_provide
    VIDEO_ID = "wtLJPvx7-ys"

    obj = DataIngestion(API_KEY)
    path = obj.fetch_comments(VIDEO_ID, max_results=200)

    print(f"Data saved at: {path}")
