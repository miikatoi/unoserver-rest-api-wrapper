# unoserver-rest-api-wrapper

Wraps https://github.com/libreofficedocker/unoserver-rest-api for embedding images into html.

WARNING: Currently no security implemented!

usage
```bash
curl -s -v \
   --request POST \
   --url http://127.0.0.1:2004/request \
   --header 'Content-Type: multipart/form-data' \
   --form "file=@my_file.docx" \
   --form 'convert-to=html' \
--output "foo.html"
```