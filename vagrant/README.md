# Multinode GlusterFS on Vagrant

This guide walks users through setting up a 3-node GlusterFS cluster, creating and starting a volume, and mounting it on a client.

It's fun to learn [GlusterFS](http://gluster.org), kids!

## Install prerequisites

Install [Vagrant](http://www.vagrantup.com/downloads.html) and a provider such as [VirtualBox](https://www.virtualbox.org/wiki/Downloads).

We'll also need the [vagrant-cachier](https://github.com/fgrehm/vagrant-cachier) plugin so we don't pull all of these packages unnecessarily on four hosts.

```console
$ vagrant plugin install vagrant-cachier
```

## Start the VMs

This instructs Vagrant to start the VMs and install GlusterFS on them.

```console
$ vagrant up
```

## Probe for peers

Before we can create a volume spanning multiple machines, we need to tell Gluster to recognize the other hosts.

```console
$ vagrant ssh gluster-server-1 -c 'sudo gluster peer probe gluster-server-2 ; sudo gluster peer probe gluster-server-3'
```

May be useful (needed in case of error for peer)
```console
$ vagrant ssh gluster-server-2 -c 'sudo gluster peer probe gluster-server-1'
```

## Create a volume

Now we can create and start our volume spanning multiple hosts.

```console
$ vagrant ssh gluster-server-1 -c 'sudo gluster volume create dicom replica 3 transport tcp gluster-server-1:/data gluster-server-2:/data gluster-server-3:/data force'
```

```console
$ vagrant ssh gluster-server-1 -c 'sudo gluster volume start dicom'
```

Here, we create a [replicated volume](http://gluster.org/community/documentation/index.php/Gluster_3.2:_Creating_Replicated_Volumes) across three hosts. The number of bricks must match the number of replicas.

## NFS on Windows (not working)

On Windows
```console
mount \\192.168.50.21\dicom Z:
mount -o anon \\192.168.50.21\dicom Z:
mount -o anon \\gluster-server-1\dicom Z:
```

Installation for windows (NFS)

```console
apt -y install nfs-ganesha-gluster
mv /etc/ganesha/ganesha.conf /etc/ganesha/ganesha.conf.org
vim /etc/ganesha/ganesha.conf
```

Config file content

```console
NFS_CORE_PARAM {
    # possible to mount with NFSv3 to NFSv4 Pseudo path
    mount_path_pseudo = true;
    # NFS protocol
    Protocols = 3,4;
}
EXPORT_DEFAULTS {
    # default access mode
    Access_Type = RW;
}
EXPORT {
    # uniq ID
    Export_Id = 101;
    # mount path of Gluster Volume
    Path = "/dicom";
    FSAL {
        # any name
        name = GLUSTER;
        # hostname or IP address of this Node
        hostname="gluster-server-1";
        # Gluster volume name
        volume="dicom";
    }
    # rconfig for root Squash
    Squash="No_root_squash";
    # NFSv4 Pseudo path
    Pseudo="/dicom";
    # allowed security options
    SecType = "sys";
}
LOG {
    # default log level
    Default_Log_Level = WARN;
}
```

```console
root@node01:~# systemctl restart nfs-ganesha
root@node01:~# systemctl enable nfs-ganesha
root@node01:~# showmount -e localhost
```

## Mount the volume

On our client, we can mount this volume and play around with it.

```console
$ vagrant ssh gluster-client -c 'sudo mkdir /mnt/glusterfs ; sudo chmod 777 /mnt/glusterfs ; sudo mount -t glusterfs gluster-server-1:/dicom /mnt/glusterfs'
```

Note here that we just need to specify one host to mount - this is because the gluster client will connect and get metadata about the
volume, and may never even talk to this host again! Neat!

## Samba

https://linuxize.com/post/how-to-install-and-configure-samba-on-ubuntu-18-04/


```console
vagrant ssh gluster-client

sudo apt install samba
vi /etc/samba/smb.conf

[dicom]
  path = /mnt/glusterfs
  read only = no
  guest ok = yes
  browsable = yes

sudo systemctl restart smbd

```

net use z: \\gluster-client\dicom /user:"anonymous" ""

## Play around

We can use this like a local filesystem:

```console
$ vagrant ssh gluster-client -c 'echo hello | sudo tee /mnt/glusterfs/f.txt'
```

Or, we can write big chunks of data to see how it performs:

```console
$ vagrant ssh gluster-client -c 'sudo dd if=/dev/urandom of=/mnt/glusterfs/junk bs=64M count=16'
```

## Test the cluster

What happens when we take down a machine?

```console
$ vagrant halt gluster-server-1
```

```console
vagrant ssh gluster-client -c 'ls /mnt/glusterfs/'
f.txt  junk  lolol.txt
```

Everything still works!

What happens if we take down a second machine?

```console
$ vagrant halt gluster-server-2
```

```console
vagrant ssh gluster-client -c 'ls /mnt/glusterfs/'
f.txt  junk  lolol.txt
```

Everything still works!

## Inspecting cluster state

As you mess with things, two commands are helpful to determine what is happening:

```console
vagrant@gluster-server-x:/$ sudo gluster peer status
vagrant@gluster-server-x:/$ sudo gluster volume info
```

You can also tail the gluster logs:

```console
vagrant@gluster-server-x:/$ sudo tail -f /var/log/glusterfs/etc-glusterfs-glusterd.vol.log
```

As you bring down the other hosts, you'll see the healthy host report them as down in the logs:
```
[2014-08-14 23:00:10.415446] W [socket.c:522:__socket_rwv] 0-management: readv on 192.168.50.22:24007 failed (No data available)
[2014-08-14 23:00:12.686355] E [socket.c:2161:socket_connect_finish] 0-management: connection to 192.168.50.22:24007 failed (Connection refused)
[2014-08-14 23:01:02.611395] W [socket.c:522:__socket_rwv] 0-management: readv on 192.168.50.23:24007 failed (No data available)
[2014-08-14 23:01:03.726702] E [socket.c:2161:socket_connect_finish] 0-management: connection to 192.168.50.23:24007 failed (Connection refused)
```

Similarly, you'll see the host come back up:
```
[2014-08-14 23:02:34.288696] I [glusterd-handshake.c:563:__glusterd_mgmt_hndsk_versions_ack] 0-management: using the op-version 30501
[2014-08-14 23:02:34.293048] I [glusterd-handler.c:2050:__glusterd_handle_incoming_friend_req] 0-glusterd: Received probe from uuid: 1dc04e5c-958f-4eea-baab-7afb33aaee69
[2014-08-14 23:02:34.293415] I [glusterd-handler.c:3085:glusterd_xfer_friend_add_resp] 0-glusterd: Responded to 192.168.50.22 (0), ret: 0
[2014-08-14 23:02:34.294823] I [glusterd-sm.c:495:glusterd_ac_send_friend_update] 0-: Added uuid: 1dc04e5c-958f-4eea-baab-7afb33aaee69, host: 192.168.50.22
[2014-08-14 23:02:34.295016] I [glusterd-sm.c:495:glusterd_ac_send_friend_update] 0-: Added uuid: 929cfe49-337b-4b41-a1e6-bc1636d5c757, host: 192.168.50.23
[2014-08-14 23:02:34.296738] I [glusterd-handler.c:2212:__glusterd_handle_friend_update] 0-glusterd: Received friend update from uuid: 1dc04e5c-958f-4eea-baab-7afb33aaee69
[2014-08-14 23:02:34.296904] I [glusterd-handler.c:2257:__glusterd_handle_friend_update] 0-: Received uuid: 9c9f8f9b-2c12-45dc-b95d-6b806236c0bd, hostname:192.168.50.21
[2014-08-14 23:02:34.297068] I [glusterd-handler.c:2266:__glusterd_handle_friend_update] 0-: Received my uuid as Friend
[2014-08-14 23:02:34.297270] I [glusterd-handler.c:2257:__glusterd_handle_friend_update] 0-: Received uuid: 929cfe49-337b-4b41-a1e6-bc1636d5c757, hostname:192.168.50.23
[2014-08-14 23:02:34.297469] I [glusterd-rpc-ops.c:356:__glusterd_friend_add_cbk] 0-glusterd: Received ACC from uuid: 1dc04e5c-958f-4eea-baab-7afb33aaee69, host: 192.168.50.22, port: 0
[2014-08-14 23:02:34.313528] I [glusterd-rpc-ops.c:553:__glusterd_friend_update_cbk] 0-management: Received ACC from uuid: 1dc04e5c-958f-4eea-baab-7afb33aaee69
```

## Cleanup

When you're all done, tell Vagrant to destroy the VMs.

```console
$ vagrant destroy -f
```

```console
vagrant resume
vagrant suspend
```
