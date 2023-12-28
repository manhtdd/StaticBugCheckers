#!/bib/bash

docker build -t static-checker:vul4j .
docker run -it --name static-checker-vul4j static-checker:vul4j
