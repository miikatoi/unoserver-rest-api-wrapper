# unoserver-rest-api-wrapper

Wraps https://github.com/libreofficedocker/unoserver-rest-api for embedding images into html.

NOTE:
- Currently no security implemented!
- Default filter loses correct positions of images sometimes. XHML filter maintains the correct positions better but sometimes raises error.

## Usage

Start the containers
```
docker-compose up --build
```

Make queries as you would to unoserver-rest-api
```bash
curl -s -v \
   --request POST \
   --url http://127.0.0.1:2004/request \
   --header 'Content-Type: multipart/form-data' \
   --form "file=@my_file.docx" \
   --form 'convert-to=html' \
--output "foo.html"
```
