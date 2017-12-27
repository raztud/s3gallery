# s3gallery

S3Gallery is a simple web browser for your images hosted in Amazon S3, although can be any type of file. 
If the browser cannot display the file, it will download it.

### Setup

Move s3gallery/amazon.py.template in s3gallery/amazon.py and fill the required constants.

Set the necessary rights on `temporary` folder.

```
pip install -r requirements.txt
python manage.py runserver
```

[Check the wiki](https://github.com/raztud/s3gallery/wiki) for more info.
