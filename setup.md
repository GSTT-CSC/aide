# Mac setup

## Requirements

* Install **Python3** (*3.8 recommended if you want to debug*).
You may install it using homebrew or download installable.

* Install **Node js** 14.x or newer.

* Install **Docker**.

## Setup

---
&nbsp;
### Create virtual enviroment for python development in selected directory

```bash
pip3 install virtualenv
virtualenv venv
source venv/bin/activate
```

> ```deactivate``` - *to deactivate venv context if needed !*

---
&nbsp;

### Install requirements

```bash
pip install -r requirements.txt
```

---
&nbsp;

### Git clone

```bash
git clone https://***********@bitbucket.org/fortrus/ai_engine.git
```

---

#### Then in project directory

```bash
cd web/ai_pipeline
npm i

cd docker/nginx
sh build.sh

cd docker/app
sh build.sh
```

---

#### Docker specific

```bash
cd docker
```

> edit **```.env```** file - there is DATA_DIRECTORY variable you need to set with path where all files will be stored

```bash
docker-compose build
docker-compose up -d
```

&nbsp;

---

&nbsp;

> *To shoutdown docker you should use*

```bash
docker-compose down -v -t 0
```
