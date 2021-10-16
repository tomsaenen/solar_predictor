# solar_predictor
Local solar predictions for my dad

Just a small DIY project

## Features
- Read out local solar predictions (provided by Elia for Belgium)
- Recalculate for local site capacity
- Read out actual performance (provided by SolarEdge)
- Create nice graph

![plot.png](./doc/plot.png)

## Install

#### Prerequisites
- Python
- git

#### Repository
```bash
git clone https://github.com/tomsaenen/solar_predictor.git
```

#### Dependencies
```bash
pip install colorama requests xmltodict pytz pandas scipy matplotlib astral python-snap7
```

#### SolarEdge API
To access the SolarEdge API an API key is required. This key is read from `credentials.json`:
```json
{
        "solaredge" : {
                "api_key": "..."
        },
        "plc" : {
                "ip" : {
                        "local": "192.168.0.xx",
                        "public": "xx.xx.xx.xx"
                }
        }

}
```
This file is not included in the repository for privacy reasons.

## Run
Run for today:
```bash
py main.py
```

Run for any day:
```bash
py main.py YYYY-MM-DD
```

Test communication with 3rd parties separately:
```bash
py elia.py
py solaredge.py
py solar.py
py plc.py
```

Run in a loop:
```bash
py loop.py
```
Every 30 seconds, this reads out the current battery level and writes it to the PLC.

## Update
```bash
git pull
```

## TODO
- Plot today's values when running connectors standalone
- Communicate predictions to PLC via OPC
