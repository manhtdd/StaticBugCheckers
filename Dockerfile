# Use an official Ubuntu runtime as a parent image
FROM ubuntu:22.04

# Set environment variables for Java
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64
ENV PATH $PATH:$JAVA_HOME/bin

# Install Java 8, curl, wget, unzip, SVN, Perl, Git, Python, pip, cpan, tzdata
RUN apt-get update && \
    apt-get install -y openjdk-8-jdk curl wget unzip python3 python3-pip cpanminus subversion perl git

# Install tzdata
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC
RUN apt-get install -y tzdata

# Install icecream using pip
RUN pip3 install icecream

# Set the working directory to /app
WORKDIR /app

# Clone the Git repository
RUN git clone https://github.com/manhlamabc123/StaticBugCheckers && \
    git checkout test-infer-build

RUN cd StaticBugCheckers && \
    git clone -q https://github.com/rjust/defects4j.git && \
    cd defects4j && cpanm --installdeps . && ./init.sh