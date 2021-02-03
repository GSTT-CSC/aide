#!/bin/bash

echo "creating if not exist ... sleep 5"
sleep 5

# volume_list=$(gluster volume list)
# echo ${volume_list}

if [ "$(gluster volume list)" != "dicom" ]
then
    echo "creating and starting volume"

    gluster peer probe gluster-s1
    gluster peer probe gluster-s2
    gluster volume create dicom replica 3 gluster-m:/data gluster-s1:/data gluster-s2:/data force
    gluster volume start dicom

    # gluster volume create dicom gluster-m:/data force
    # gluster volume start dicom

    echo "done"
else
    echo "already created ..."
fi
