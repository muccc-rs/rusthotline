# Rust Hotline
## A Yate-hotline implementation

### Setup

Dependencies:

yate (>= 6.4.1)
python (= 3)
pip (=> 24)

Configuration:

- SIP connection: /conf/accfile

Setup steps:

```sh
cd ivr
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd ..
./init.sh
```

Execution:

```sh
./run.sh
```

Logs can be found in callog.csv (for caller stats) and call.log (internal logging)

### Next

- [ ] rewrite the ivr in rust
- [ ] send compatiple wav as Alert-Info header

### Notable mentions:

[python-yate](https://github.com/eventphone/python-yate/blob/master/LICENSE)

### Development notes:
