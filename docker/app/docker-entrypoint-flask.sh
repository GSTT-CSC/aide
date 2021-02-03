#!/bin/bash
set -x

# lets check is glusterfs working
</dev/tcp/gluster-m/49152
while [ "$?" != "0" ]
do
    sleep 3
    </dev/tcp/gluster-m/49152
done

# now rabbitmq
</dev/tcp/rmq/15672
while [ "$?" != "0" ]
do
    sleep 3
    </dev/tcp/rmq/15672
done

# mount it
# FIXME: use this for prod
# mount -t glusterfs gluster-m:/dicom /mnt/data

# mount vagrant
# mount -t glusterfs gluster-server-1:/dicom /mnt/data

# now the script
cd /usr/src/app
export FLASK_APP=$1

exec python -m flask run --host=0.0.0.0
