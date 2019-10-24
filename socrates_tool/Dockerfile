FROM ubuntu:18.04
LABEL maintainer="eviglianisi@fbk.eu"

# Update repository
RUN apt-get clean && apt-get update

# Set the locale
RUN apt-get install -y locales
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# UPDATE apt
RUN apt-get update

# Install utils
RUN apt-get install -y curl build-essential git nano software-properties-common software-properties-common

# Install node/python3/curl
RUN curl -sL https://deb.nodesource.com/setup_10.x | bash -
RUN apt-get -y install nodejs python3 python3-pip
RUN npm i npm@latest -g

# Install solc
RUN curl -o /usr/bin/solc -fL https://github.com/ethereum/solidity/releases/download/v0.4.25/solc-static-linux \
    && chmod u+x /usr/bin/solc

# Install tsc/truffle/ganache/z3
RUN npm install -g typescript truffle@^4.1.15
RUN npm install -g ganache-cli
RUN pip3 install z3-solver web3==4.9.2

# Create app folder
RUN mkdir -p /usr/src/app

# Copy the rest of the app
COPY app /usr/src/app

WORKDIR /usr/src/app
RUN (cd bot-framework && npm install && ./node_modules/typescript/bin/tsc)

RUN chmod +x ./my_wrapper_script.sh

ENTRYPOINT ["/bin/bash", "/usr/src/app/my_wrapper_script.sh"]
