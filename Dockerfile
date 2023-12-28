# Use an official Ubuntu runtime as a parent image
FROM ubuntu:22.04

# Set environment variables for Java
ENV JAVA_HOME_7 /usr/lib/jvm/java-7-openjdk-amd64
ENV JAVA_HOME_8 /usr/lib/jvm/java-8-openjdk-amd64
ENV PATH $PATH:$JAVA_HOME_7/bin:$JAVA_HOME_8/bin

# Install Java 7, Java 8, curl, wget, unzip, SVN, Perl, Git, Python, pip, cpan, tzdata, and Maven 3
RUN apt-get update && \
    apt-get install -y openjdk-7-jdk openjdk-8-jdk curl wget unzip python3 python3-pip cpanminus subversion perl git maven

# Install tzdata
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC
RUN apt-get install -y tzdata

# Install icecream using pip
RUN pip3 install icecream

# Set the working directory to /app
WORKDIR /app

# Clone the Git repository
RUN git clone https://github.com/manhlamabc123/StaticBugCheckers

RUN cd StaticBugCheckers && \
    git clone https://github.com/bqcuong/vul4j