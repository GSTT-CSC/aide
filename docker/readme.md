## HELPERS for docker

docker-compose down -v -t 0

docker-compose build

docker-compose up -d

docker-compose stop -t 0

docker-compose exec gluster-m /bin/bash
docker-compose logs gluster-m

# MOUNT from docker

```
sudo mount -t glusterfs gluster-m:/dicom /var/local/data
```

# MOUNT

``apt install glusterfs-client``

```
sudo mount -t glusterfs 192.168.50.11:/dicom /var/local/data
sudo umount --force /var/local/data
```

add to ``/etc/hosts``
```
192.168.50.11 gluster-m
```
for mount to work locally in debug

# WINDOWS

RUN ...
optionalfeatures

Services for NFS -> Client to install

# VAGRANT

```
vagrant ssh gluster-server-1 -c 'sudo gluster peer probe gluster-server-2 ; sudo gluster peer probe gluster-server-3'
vagrant ssh gluster-server-2 -c 'sudo gluster peer probe gluster-server-1'
vagrant ssh gluster-server-1 -c 'sudo gluster volume create dicom replica 3 transport tcp gluster-server-1:/data gluster-server-2:/data gluster-server-3:/data force'
vagrant ssh gluster-server-1 -c 'sudo gluster volume start dicom'
vagrant ssh gluster-client -c 'sudo mkdir /mnt/glusterfs ; sudo chmod 777 /mnt/glusterfs ; sudo mount -t glusterfs gluster-server-1:/dicom /mnt/glusterfs'
```

```console
vagrant ssh gluster-client

sudo apt install samba
sudo vi /etc/samba/smb.conf

[dicom]
  path = /mnt/glusterfs
  read only = no
  guest ok = yes
  browsable = yes
  force user = root

sudo systemctl restart smbd
```

``Remark: force user may be bad idea for production``

Remount after restart ! (TODO: we may use fstab but for dev is ok as is ...)
```
vagrant ssh gluster-client -c 'sudo mount -t glusterfs gluster-server-1:/dicom /mnt/glusterfs'
```

```
net use z: \\gluster-client\dicom /user:"anonymous" ""
net use z: /delete
```

```
docker-machine ssh
cd /var/lib/docker/volumes/docker_scanner-data/_data
```

# DICOM SEND
```
dcmsend --verbose 192.168.50.11 11112 *.dcm
dcmsend --scan-directories --verbose 192.168.50.11 11112 --recurse test_dicom_study_gstt
```
