from flask import Flask, request, render_template, jsonify
import requests
from api import API_KEY
app = Flask(__name__)

API_URL = "http://dataservice.accuweather.com"
def check_bad_weather(mn_t, mx_t, wind_speed, rain_prob):
    if mn_t < 0 or mx_t > 35:
        return "Температура экстремальна!"
    if wind_speed > 50:
        return "Сильный ветер!"
    if rain_prob > 70:
        return "Высокая вероятность осадков!"
    return "Погода благоприятная."

def get_location_key(lat, lon):
    weather_url = f"{API_URL}/locations/v1/cities/geoposition/search?apikey={API_KEY}&q={lat}%2C{lon}"
    try:
        loc_data = requests.get(weather_url)
        loc_data = loc_data.json()
        loc_key = loc_data['Key']
        return loc_key
    except Exception as e:
        return render_template('index.html', error = "Недоступные данные ключа")

def get_weather_data(location_key):
    weather_url = f"{API_URL}/forecasts/v1/daily/1day/{location_key}?apikey={API_KEY}&language=en-us&details=true&metric=true"
    try:
        response = requests.get(weather_url)
        if response.status_code != 200:
            return None
        return response.json()
    except Exception as e:
        return render_template('index.html', error = "Недоступные данные погоды")


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/weather', methods=['POST'])
def weather():
    st_latitude = request.form['lat_st']
    st_longitude = request.form['lon_st']
    end_latitude = request.form['lat_end']
    end_longitude = request.form['lon_end']

    if not st_latitude or not st_longitude or not end_latitude or not end_longitude:
        return "Ошибка: Укажите все координаты!", 400

    location_key_st = get_location_key(st_latitude, st_longitude)
    if not location_key_st:
        return "Ошибка: Не удалось найти начальную точку!", 400

    location_key_end = get_location_key(end_latitude, end_longitude)
    if not location_key_end:
        return "Ошибка: Не удалось найти конечную точку!", 400

    weather_data_st = get_weather_data(location_key_st)
    weather_data_end = get_weather_data(location_key_end)

    if not weather_data_st or not weather_data_end:
        return "Ошибка: Не удалось получить данные о погоде!", 400

    forecast_st = weather_data_st['DailyForecasts'][0]
    mx_temperature_st = forecast_st['Temperature']['Maximum']['Value']
    mn_temperature_st = forecast_st['Temperature']['Minimum']['Value']
    wind_speed_st = forecast_st['Day']['Wind']['Speed']['Value']
    rain_prob_st = forecast_st['Day']['PrecipitationProbability']

    forecast_end = weather_data_end['DailyForecasts'][0]
    mx_temperature_end = forecast_end['Temperature']['Maximum']['Value']
    mn_temperature_end = forecast_end['Temperature']['Minimum']['Value']
    wind_speed_end = forecast_end['Day']['Wind']['Speed']['Value']
    rain_prob_end = forecast_end['Day']['PrecipitationProbability']

    weather_report_st = check_bad_weather(mn_temperature_st, mx_temperature_st, wind_speed_st, rain_prob_st)
    weather_report_end = check_bad_weather(mn_temperature_end, mx_temperature_end, wind_speed_end, rain_prob_end)

    return f'''
        <h2>Прогноз для начальной точки:</h2>
        <p>{weather_report_st}</p>
        <h2>Прогноз для конечной точки:</h2>
        <p>{weather_report_end}</p>
        <a href="/">Назад</a>
    '''

if __name__ == '__main__':
    app.run(debug=True)