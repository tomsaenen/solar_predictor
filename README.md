# solar_predictor
Local solar predictions for my dad

Just a small DIY project

## Features
- Read out local solar predictions (provided by Elia for Belgium)
- Recalculate for local site capacity
- Read out actual performance (provided by SolarEdge)
- Create nice graph

![plot.png](./plot.png)

## Install

#### Repository
```bash
git clone https://github.com/tomsaenen/solar_predictor.git
```

#### SolarEdge API
To access the SolarEdge API an API key is required. This key is read from `solaredge_api.json`:
```json
{
  "api_key": "KEY",
}
```
This file is not included in the repository for privacy reasons.

## Run
Run for today:
```bash
python3 local_predictor.py
```

Run for any day:
```bash
python3 local_predictor.py YYYY-MM-DD
```

You can test the communication with Solar Edge separately:
```bash
python3 solaredge.py
```

## TODO
- Add SolarEdge data to graph
- Communicate predictions to PLC via OPC
