# Log folder

Logs will be put in here in form:

```
DRS-{user}_PID-{PID}
```

where:
- `PID` is the drs process ID number


Note that logs generated by the processor will be in a sub-directory:

```
DRS-{user}_PID-{PID}_{group_name}
```

where:
- `user` is the host computer username (set to `host` if unknown)
- `PID` is the drs process ID number
- `group_name` is the name of the group (for processing this is `_processing_group`)

This path can be changed in  ```{DRS_UCONFIG}/{INSTRUMENT}/user_config.ini```