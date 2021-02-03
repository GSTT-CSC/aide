FROM gluster/gluster-centos:latest

RUN mkdir /data
RUN chmod a+w /data

COPY setup.sh /
RUN chmod +x /setup.sh

COPY init.sh /
RUN chmod +x /init.sh

ENTRYPOINT ["/setup.sh"]
