from flask import Flask, render_template, request, redirect, url_for, jsonify
from PIL import Image as pil_image
import numpy as np
from keras.preprocessing import image
from keras.applications.xception import preprocess_input
from keras.models import load_model
import base64
import io
import plotly.graph_objects as go
import json

app = Flask(__name__)

# modelo
print('Cargando modelo...')
model = load_model('modelomejoradoval (4).h5')
model.save('saved_model', save_format='tf')
model = load_model('saved_model')
print('Modelo cargado')

# categorías 
categorias = {0:'battery', 1:'biological', 2:'brown-glass', 3:'cardboard', 4:'clothes', 5:'green-glass', 6:'metal', 7:'paper', 8:'plastic', 9:'shoes', 10:'trash', 11:'white-glass'}
conteo_clases = {categoria: 0 for categoria in categorias.values()}
custom_conteo_clases = {}
img_data = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/edit_class', methods=['GET','POST'])
def edit_class():
    global categorias
    global conteo_clases
    if request.method == 'POST':
        oldie = request.form['old_name']
        new = request.form['new_name']
        for key, value in categorias.items():
            if value == oldie:
                categorias[key] = new
                break
        if oldie in conteo_clases:
          conteo_clases[new] = conteo_clases.pop(oldie)
    return render_template('advanced.html', categorias=categorias)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    predicted_label = None
    global img_data
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file:
            img = file.read()
            img_data = base64.b64encode(img).decode('utf-8')
            img = pil_image.open(io.BytesIO(img))
            img = img.resize((320, 320))
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = preprocess_input(img_array)
            predictions = model.predict(img_array)
            predicted_class = np.argmax(predictions)
            predicted_label = categorias[predicted_class]
            print(conteo_clases)
            conteo_clases[predicted_label] += 1
    return render_template('index.html', predicted_label=predicted_label, custom_classes=custom_conteo_clases, show_customize=False, img_data=img_data)

@app.route('/upload_photo', methods=['POST'])
def upload_photo():
    predicted_label = None
    global img_data
    if request.method == 'POST':
        photo_data = request.form['photo']
        img = base64.b64decode(photo_data)
        img_data = photo_data
        img = pil_image.open(io.BytesIO(img))
        img = img.resize((320, 320))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        predictions = model.predict(img_array)
        predicted_class = np.argmax(predictions)
        predicted_label = categorias[predicted_class]
        conteo_clases[predicted_label] += 1
    return render_template('index.html', predicted_label=predicted_label, custom_classes=custom_conteo_clases, show_customize=False, img_data=img_data)

@app.route('/customize', methods=['POST'])
def customize():
    predicted_label = request.form.get('predicted_label')
    return render_template('index.html', predicted_label=predicted_label, custom_classes=custom_conteo_clases, show_customize=True, img_data=img_data)

@app.route('/update_custom_class', methods=['GET','POST'])
def update_custom_class():
    if request.method == 'POST':
        custom_class = request.form.get('custom_class')
        if custom_class:
            if custom_class not in custom_conteo_clases:
                custom_conteo_clases[custom_class] = 0
    return render_template('custom.html')

@app.route('/classify_custom_class', methods=['POST'])
def classify_custom_class():
    if request.method == 'POST':
        selected_class = request.form['selected_class']
        custom_conteo_clases[selected_class] += 1
        return redirect(url_for('index'))

@app.route('/grafico')
def grafico():
    labels = list(conteo_clases.keys())
    counts = list(conteo_clases.values())

    fig = go.Figure([go.Bar(x=labels, y=counts, marker_color='orange')])
    fig.update_layout(
        title='Reporte de Recolección',
        xaxis_title='Tipos',
        yaxis_title='Cantidad',
        xaxis_tickangle=-45,
        autosize=False,
        width=800,
        height=600
    )

    custom_labels = list(custom_conteo_clases.keys())
    custom_counts = list(custom_conteo_clases.values())

    custom_fig = go.Figure([go.Bar(x=custom_labels, y=custom_counts, marker_color='green')])
    custom_fig.update_layout(
        title='Reporte de Clases Personalizadas',
        xaxis_title='Tipos Personalizados',
        yaxis_title='Cantidad',
        xaxis_tickangle=-45,
        autosize=False,
        width=800,
        height=600
    )

    return render_template('grafico.html', graphd=fig.to_json(), customgraphd=custom_fig.to_json())

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True, port=5000)