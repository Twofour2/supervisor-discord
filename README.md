# supervisor-discord
Connects supervisor alerts to discord using webhooks.

## Install
```
pip install supervisor-discord
```

## Supervisor.conf
[eventlistener:supervisor-discord]
command=python

## Setup
Navigate to site-packages > supervisor-discord.
Either run autoconfig.py, or create config.yaml manually.

## config.yaml
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

