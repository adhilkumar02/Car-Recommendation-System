import pandas as pd
from flask import Flask, render_template, request, redirect, url_for

# --- Load Car Dataset ---
file_path = "car_detail.csv"
try:
    car_data = pd.read_csv(file_path)
except FileNotFoundError:
    print(f"Error: CSV file not found at {file_path}")
    car_data = pd.DataFrame()

# --- Recommendation Logic ---
def recommend_cars(min_price=None, max_price=None, fuel=None, transmission=None, min_year=None, max_km=None, top_n=10):
    df = car_data.copy()

    if min_price is not None:
        df = df[df["selling_price"] >= min_price]
    if max_price is not None:
        df = df[df["selling_price"] <= max_price]
    if fuel:
        df = df[df["fuel"].str.lower() == fuel.lower()]
    if transmission:
        df = df[df["transmission"].str.lower() == transmission.lower()]
    if min_year:
        df = df[df["year"] >= min_year]
    if max_km:
        df = df[df["km_driven"] <= max_km]

    df = df.sort_values(by=["year", "km_driven"], ascending=[False, True])
    return df.head(top_n)[["name", "year", "selling_price", "km_driven", "fuel", "transmission"]]

# --- Flask App ---
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None

    if request.method == 'POST':
        min_price = request.form.get('min_price', '').strip()
        max_price = request.form.get('max_price', '').strip()
        fuel = request.form.get('fuel', '').strip()
        transmission = request.form.get('transmission', '').strip()
        min_year = request.form.get('min_year', '').strip()
        max_km = request.form.get('max_km', '').strip()

        try:
            min_price = int(min_price) if min_price else None
            max_price = int(max_price) if max_price else None
            min_year = int(min_year) if min_year else None
            max_km = int(max_km) if max_km else None
        except ValueError:
            error = "⚠️ Please enter valid numerical values."
            return render_template('index.html', error=error)

        return redirect(url_for('results', 
                                min_price=min_price or '',
                                max_price=max_price or '',
                                fuel=fuel or '',
                                transmission=transmission or '',
                                min_year=min_year or '',
                                max_km=max_km or ''))

    return render_template('index.html', error=error)

@app.route('/results')
def results():
    
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    fuel = request.args.get('fuel')
    transmission = request.args.get('transmission')
    min_year = request.args.get('min_year')
    max_km = request.args.get('max_km')

    try:
        min_price = int(min_price) if min_price else None
        max_price = int(max_price) if max_price else None
        min_year = int(min_year) if min_year else None
        max_km = int(max_km) if max_km else None
    except ValueError:
        return render_template('results.html', error="⚠️ Invalid input values.", results=None)
    
    results_df = recommend_cars(min_price, max_price, fuel, transmission, min_year, max_km)
    results = results_df.to_dict('records')
    return render_template('results.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
