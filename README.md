# AdvancedSettingsMacOs

A user interface for setting hidden preferences on macOS (mostly `defaults`).


## Usage

### 1. Clone this repository

```bash
git clone https://github.com/jneuendorf/AdvancedSettingsMacOS.git
cd AdvancedSettingsMacOS
```


### 2. Setup a virtual environment

```bash
python3 -m venv venv
source ./venv/bin/activate
pip install -r ./requirements.txt
```


### 3. Start the server

```bash
./manage.py runserver
```

and wait for 

```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

This should take about 10 seconds.


### 4. Open the browser

Click [this link](http://localhost:8000/) or run


```bash
open http://localhost:8000/
```


### Altogether


```bash
git clone https://github.com/jneuendorf/AdvancedSettingsMacOS.git
cd AdvancedSettingsMacOS
python3 -m venv venv
source ./venv/bin/activate
pip install -r ./requirements.txt
./manage.py runserver
```

The URL must be opened manually since the server process is running endlessly.