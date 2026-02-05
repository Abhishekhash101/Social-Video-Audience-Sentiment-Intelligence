from src.logger import logging
from src.exception import CustomException
import os
import sys
from dataclasses import dataclass
import nltk
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import pandas as pd 
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.model_selection import train_test_split
import numpy as np
nltk.download('stopwords')
nltk.download('vader_lexicon')
from src.utils import save_object

@dataclass
class DataTransformationConfig:
    preprocessor_obj_file_path:str=os.path.join("artifacts","preprocessor.pkl")

class DataTransformation:
    def __init__(self):
        self.data_transformation_config=DataTransformationConfig()

    def clean_text(self, text):
        try:
            text=re.sub('[^a-zA-Z]',' ',str(text))
            text=text.lower()
            text=text.split()
            ps=PorterStemmer()
            all_stopwords=stopwords.words('english')
            all_stopwords.remove('not')

            text=[ps.stem(word) for word in text if word not in set(all_stopwords)]
            text=' '.join(text)

            return text
        
        except Exception as e:
            logging.error(e)
            raise CustomException(e,sys)

    def initiate_data_transformation(self,raw_data_path):
        try:
            logging.info("Datatransformation is started........................")
            df=pd.read_csv(raw_data_path)
            logging.info("Dataframe loaded")


            if 'label' not in df.columns:
                logging.info("Creating the label column.....")
                sia=SentimentIntensityAnalyzer()
                df['label']=df['comment'].apply(lambda x:1 if sia.polarity_scores(str(x))['compound']>0 else 0)
                logging.info("Pseudo Labeling is Completed.....")

                logging.info("Starting the data cleaning part....")
                df['cleaned_comment'] =df['comment'].apply(self.clean_text)

                X=df['cleaned_comment']
                y=df['label']

                logging.info("Spliting the data")
                X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.2,random_state=42)

                tfidf=TfidfVectorizer(max_features=5000)
                x_train_tfidf=tfidf.fit_transform(X_train).toarray()
                x_test_tfidf=tfidf.transform(X_test).toarray()

                save_object(
                file_path=self.data_transformation_config.preprocessor_obj_file_path,
                obj=tfidf
            )
            logging.info(f"Preprocessor saved at {self.data_transformation_config.preprocessor_obj_file_path}")

            return (
                x_train_tfidf,
                np.array(y_train),
                x_test_tfidf,
                np.array(y_test),
                self.data_transformation_config.preprocessor_obj_file_path,
            )

        except Exception as e:
            logging.error(e)
            raise(CustomException(e,sys))

if __name__ == "__main__":
    try:
        transformer = DataTransformation()
        transformer.initiate_data_transformation('artifacts/raw_data.csv')
        print("Transformation Complete.")
    except Exception as e:
        print(e)
