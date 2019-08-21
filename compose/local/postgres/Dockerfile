FROM postgres:10.4

# update and install all required packages (no sudo required as root)
# https://gist.github.com/isaacs/579814#file-only-git-all-the-way-sh
# RUN apt-get update -yq && apt-get upgrade -yq && \
# 	apt-get install -yq curl git nano

# copy over important files
COPY ./compose/production/postgres/maintenance /usr/local/bin/maintenance
RUN chmod +x /usr/local/bin/maintenance/*
RUN mv /usr/local/bin/maintenance/* /usr/local/bin \
    && rmdir /usr/local/bin/maintenance

# launch initialization sql commands on docker postgres
COPY ./compose/local/postgres/init /docker-entrypoint-initdb.d
RUN chmod +x /docker-entrypoint-initdb.d/*

RUN echo $(id)

EXPOSE 5432
