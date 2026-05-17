# WeatherStack – Simple Weather App

## Group Members
- [Amro Muzahem] ([1220629])

## Description
A minimal web app that consumes the **WeatherStack REST API** (https://weatherstack.com).  
Enter any city name → shows current temperature, weather description, feels‑like temperature, wind, and humidity.

## REST principles demonstrated
- Resource URI: `/current?access_key=...&query=...`
- HTTP method: GET (safe, idempotent)
- Query parameters: `access_key` (API key), `query` (city), `units=m` (metric)
- Response format: JSON (parsed and displayed)
- Stateless: every request contains all required info


## API key
The key `6364088654c6a5523f5877422ab821ce`

## Technologies
- HTML / CSS
- WeatherStack REST API
