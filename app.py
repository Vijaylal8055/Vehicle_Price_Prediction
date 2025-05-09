from flask import Flask, request, jsonify, render_template
import joblib
import numpy as np
import pandas as pd

app = Flask(__name__)
model = joblib.load('vehicle_price_model.pkl')
# Optional: Load preprocessor if used
# preprocessor = joblib.load('preprocessor.pkl')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json(force=True)

    required_features = [
        'make', 'model', 'engine', 'cylinders', 'fuel',
        'mileage', 'transmission', 'trim', 'body', 'doors',
        'exterior_color', 'interior_color', 'drivetrain', 'year'
    ]
    missing = [f for f in required_features if f not in data]
    if missing:
        return jsonify({'error': f'Missing features: {", ".join(missing)}'}), 400

    try:
        df = pd.DataFrame([data])
        df['vehicle_age'] = pd.Timestamp.now().year - df['year']
        df.drop(columns=['year'], inplace=True)

        # Cast types if needed
        for col in ['cylinders', 'mileage', 'doors']:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Optional: transform if preprocessor used
        # df = preprocessor.transform(df)

        prediction = model.predict(df)[0]
        return jsonify({'predicted_price': round(prediction, 2)})

    except Exception as e:
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
