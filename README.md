# Raspberry Pi Code

All application code contained on the Raspberry Pi

## Contains:
- HX711 sensor files
- Execution code to activate scales and weigh items
- Raspberry Pi Camera connectivity
- Image uploading to server
- LCD Screen integration
- Button integration


## Current process
To run the Raspberry Pi scales, navigate into the `hx711` folder and execute the `example.py` file.
```
python example.py 
```

Scales are set to output the weight every 0.5 seconds, this can be modified at the end of the `example.py` file 
```
time.sleep(0.5)
```
