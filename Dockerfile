FROM bqcuongas/vul4j:latest

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC
RUN apt-get install -y tzdata

RUN pip3 install icecream

WORKDIR /StaticBugCheckers

COPY . .