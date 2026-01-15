import os
import warnings
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
warnings.filterwarnings(
    "ignore",
    message=".*mask.*",
    category=UserWarning
)
warnings.filterwarnings("ignore", category=FutureWarning)

from flask import Flask,request,jsonify
import tensorflow as tf
import keras
import joblib
import numpy as np

app = Flask(__name__)

model = keras.models.load_model("flask_app/model/line_charcnn_lstm_final.keras")

log_data = joblib.load("flask_app/model/textvectorization_char.pkl")

vec = keras.layers.TextVectorization.from_config(log_data["config"])
vec.set_vocabulary(log_data["vocabulary"])

le = joblib.load("flask_app/model/label_encoder_line.joblib")

ID_TO_LABEL = {
    0: "Disk full",
    1: "Machine down",
    2: "Network disconnection",
    3: "Normal"
}

@app.route("/health")
def check_health():
    return jsonify({"status":"ok"})


@app.route("/predict",methods=["GET","POST"])
def predict():
    if(request.method=="GET"):
        return "Use post method"
    elif(request.method=="POST"):
        data = request.get_json(silent=True)
        
        x = vec([data["log"]])

        probs = model.predict(x, verbose=0)

        class_id = int(np.argmax(probs, axis=1)[0])
        confidence = float(np.max(probs))

        return jsonify({
            "prediction": ID_TO_LABEL[class_id],
            "confidence": round(confidence, 4)
        })
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)