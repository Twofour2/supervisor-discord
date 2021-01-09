# supervisor-discord
Connects supervisor alerts to discord using webhooks.

## Install
```
pip install supervisor-discord
```

## Configure
Either run `supervisor-discord -s`, or create config.yaml manually.

config.yaml can be in one of two locations, `/etc/supervisordiscord/config.yaml` or the location where site-packages are installed on your system.

```
example: # process name
  alerts: # list of process states that can trigger this message
  - STARTING
  - RUNNING
  - BACKOFF
  - STOPPING
  - FATAL
  - EXITED
  - STOPPED
  - UNKNOWN
  message_format: '{{process_name}} changed to state {{to_state}}'
  webhookURL: # discord webhook url
 ```
 repeat for each process.
 
`message_format` supports [strftime](https://strftime.org/) and the following formats:  
```
{{process_name}}, {{from_state}}, {{to_state}}
```

## Supervisor.conf
Ensure that supervisor-discord is on your system `PATH`.
```
[eventlistener:supervisor-discord]
command=supervisor-discord
events=PROCESS_STATE
```


