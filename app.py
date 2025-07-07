from flask import Flask, request
from PIL import Image
from flask_cors import CORS
from io import BytesIO
import base64

app = Flask(__name__)
CORS(app)

@app.route('/kompres', methods=['POST'])
def kompres():
    if 'gambar' not in request.files:
        return "Gambar tidak ditemukan.", 400

    file = request.files['gambar']
    kualitas = request.form.get('kualitas', 'medium')

    try:
        img = Image.open(file.stream)
    except Exception:
        return "File bukan gambar atau rusak.", 400

    quality_map = {'high': 90, 'medium': 75, 'low': 40}
    quality = quality_map.get(kualitas, 75)

    # Simpan gambar asli (dengan kualitas tinggi untuk pembanding)
    buffer_asli = BytesIO()
    img.convert("RGB").save(buffer_asli, format="JPEG", quality=95)
    ukuran_asli = buffer_asli.tell()

    # Simpan gambar terkompresi
    buffer_kompres = BytesIO()
    img.convert("RGB").save(buffer_kompres, format="JPEG", quality=quality, optimize=True)
    ukuran_kompresi = buffer_kompres.tell()
    buffer_kompres.seek(0)

    # Konversi gambar terkompresi ke base64
    img_base64_kompres = base64.b64encode(buffer_kompres.read()).decode("utf-8")
    download_url = f"data:image/jpeg;base64,{img_base64_kompres}"

    # HTML hasil
    hasil_html = f"""
    <div class='image-compare'>
        <div>
            <h3>Gambar Asli</h3>
            <img src="data:image/jpeg;base64,{img_to_base64(img)}" />
            <p>Ukuran: {round(ukuran_asli / 1024, 2)} KB</p>
        </div>
        <div>
            <h3>Gambar Terkompresi</h3>
            <img src="{download_url}" />
            <p>Ukuran: {round(ukuran_kompresi / 1024, 2)} KB</p>
            <a href="{download_url}" download="gambar_kompresi.jpg">
              <button>Download Gambar</button>
            </a>
        </div>
    </div>
    """
    return hasil_html

def img_to_base64(image):
    buffered = BytesIO()
    image.convert("RGB").save(buffered, format="JPEG", quality=95)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

if __name__ == '__main__':
    app.run(debug=True)
