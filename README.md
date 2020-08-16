# pyhue - a python Philips Hue bridge reader

Currently aiming at reading the temperature readings and logging them to InfluxDB.

#### To get an API key from the bridge
```
curl -d '{"devicetype:"appnamer#device"}' --header "Content-Type: application/json" --request POST http://<bridge IP address>/api
```

#### Run the program
```
HUE_API_KEY=your generated Hue API Key
INFLUX_DB_ADDRESS=http://<your influx db address>:8086/write?db=<influx database name>
```
