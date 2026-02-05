from flask import Flask,request,jsonify
from flask_cors import CORS
import pickle
import numpy as np
import sys
import os
from src.components.data_transformation import DataTransformation
from src.exception import CustomException
from src.logger import logging

app=Flask(__name__)
CORS(app)

print("Loading the artifacts and models")
try:
    model_path=os.path.join('artifacts','model.pkl')
    preprocessor_path=os.path.join('artifacts','preprocessor.pkl')

    with open(model_path,'rb') as f:
        model=pickle.load(f)
    
    with open(preprocessor_path,'rb') as f:
        vectorizer=pickle.load(f)

    print("Artificats and models are loaded....")

except Exception as e:
    logging.warning(e)
    raise CustomException(e,sys)

transformer=DataTransformation()

@app.route('/', methods=['GET'])
def home():
    return "Sentiment Analysis API is Running!"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        comment = data.get('comment')
        
        if not comment:
            return jsonify({'error': 'No comment provided'}), 400

        cleaned_text = transformer.clean_text(comment)
        
        vectorized_text = vectorizer.transform([cleaned_text]).toarray()
        
        prediction = model.predict(vectorized_text)
        
        sentiment = "Positive" if prediction[0] == 1 else "Negative"
        
        return jsonify({
            'comment': comment,
            'sentiment': sentiment,
            'prediction_code': int(prediction[0])
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
