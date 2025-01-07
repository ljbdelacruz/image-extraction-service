## Image Extraction Service

> also check commands.sh for dependencies and stuff

#### Setup

docker-compose up -d
prisma migrate dev


##### installing dependencies
```
sh script/dependencies.sh
```

#### Running the app
FLASK_APP=app.py
export FLASK_APP=app.py
flask run
> or
```
sh script/run.sh
```

#### Test Docs
> to view swagger docs 
```
http://localhost:5000/api/#/
```

#### Testing
> currently i can't get wscat or websocat to work had to use python client script 
```
# modify the python path if not the same location in the script/test.sh

sh script/test.sh
```








