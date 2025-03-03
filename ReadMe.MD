## Image Extraction Service

> also check commands.sh for dependencies and stuff

#### Setup

##### installing dependencies and database setup
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

> NOTE: please make sure to setup your .env file AWS Access key and S3 Bucket

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

## Demo Video Here


https://drive.google.com/file/d/1J66rulPIRCZXhwmRzdufcmhJsI-HiYeL/view?usp=sharing

https://drive.google.com/file/d/1VFes4SgctaSzWLCHoAS26fnkKdTbKD3x/view?usp=sharing


#### My Portfolio
https://drive.google.com/drive/folders/1qr6cehFulxdQC2m7NRPjvhC5ayV28N6_?usp=sharing





