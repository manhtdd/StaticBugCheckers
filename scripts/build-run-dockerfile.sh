#!/bib/bash

docker build -t static-checker:vul4j .
docker run -it -v $(pwd):/StaticBugCheckers --name static-checker-vul4j static-checker:vul4j