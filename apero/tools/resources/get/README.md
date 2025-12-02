# Explanation for APERO GET yaml files


## apero_groups.yamls

 This file contains the Apero user groups and their members
 used for access control and permissions

 Format should be
```yaml
GROUP_NAME:
    SERVER: server_name
    SET_DIRECTORY_PERMISSIONS:
        - command1
        - command2
    SET_FILE_PERMISSIONS:
        - command1
        - command2
    USERS:
        - user1
        - user2
```

Where GROUP_NAME is {INSTRUMENT}.{PROJECT/GROUP}.{SERVER_NAME}
  

Note that commands can only currently use arguments {user} and {path} 


# permissions.yaml

This file links the RUN IDs to the Apero user groups/users for access control

Each RUN ID can have groups and users assigned to it.

GROUPS must be taken from apero_groups.yaml in form {INSTRUMENT}.{PROJECT/GROUP}.{SERVER_NAME}

USERS should be the username on the system this code is intended to be run on

Format should be

```yaml
RUN ID NAME:
    GROUPS:
        - GROUP_NAME1
        - GROUP_NAME2
    PI: "{PI NAME}"
    USERS: 
        - user1
        - user2
```


## Intended directory structure

```
data_root/ [all u:rx]
    objects/ [all u:rx]
        OBJNAME1/ [all u:rx]
            symlink to data_root/runid/RUN_ID_1/file_obj1
        OBJNAME2/ [all u:rx]
            symlink to data_root/runid/RUN_ID_1/file_obj2
        OBJNAME3/ [all u:rx]
            symlink to data_root/runid/RUN_ID_1/file_obj3
    runid/ [all u:rx]
        RUN_ID_1/  [with correct permission]
            hard copied file1  [with correct permission]
            hard copied file2  [with correct permission]
            hard copied file3  [with correct permission]
        RUN_ID_2/  [with correct permission]
            hard copied file4  [with correct permission]
            hard copied file5  [with correct permission]
            hard copied file6  [with correct permission]
```