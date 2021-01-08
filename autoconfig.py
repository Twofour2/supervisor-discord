import yaml
import requests
import os
import logging
import datetime
import time
from rich.console import Console
from rich.theme import Theme
from rich.prompt import Confirm
custom_theme = Theme({
    "info" : "dark_blue",
    "bold" : "underline bold blue1",
    "warning": "magenta",
    "warn": "red",
    "rule": "black bold"
})
console = Console(theme=custom_theme, highlight=False)

script_dir = os.path.split(os.path.realpath(__file__))[0]  # get where this script is

logging.basicConfig(filename=script_dir+'/supervisor-discord.log',level=logging.INFO, format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',datefmt='%Y-%m-%d %H:%M:%S')

webhookChannels = {}
processes = {} # {"process_name": {"webhookURL": "url", alerts:["STARTED", "EXITED"], "message_format":"{{process_name}} changed to state {{to_state}}"}

def clear(numlines=100):
  """Clear the console.
numlines is an optional argument used only as a fall-back.
"""
  if os.name == "posix":
    # Unix/Linux/MacOS/BSD/etc
    os.system('clear')
  elif os.name in ("nt", "dos", "ce"):
    # DOS/Windows
    os.system('CLS')
  else:
    # Fallback for other operating systems.
    print('\n' * numlines)

def supervisorSetup():
    # basic stuff
    while True:
        clear()
        while True:
            console.rule("[bold blue]Setup", style="rule")
            process_name = input("Enter the process name: ")
            console.print("Create a webhook in discord (Server settings > integrations > webhooks > create webhook)", style="info")
            webhookurl = input("Enter the discord webhook url: ")
            json = {'content': f"**supervisor-discord is now active on this channel.**"}
            try:
                r = requests.post(url=webhookurl, json=json)  # send messsage
                console.input(f"Check that the message [bold black]\"{json.get('content').replace('**', '')}\"[/bold black] has been posted then press <[magenta]enter[/magenta]>.")
                break
            except Exception as e:
                clear()
                console.print("Check network and/or webhook url.", style="warn")
                console.print(f"Error: {e}", style="warn")
                continue
        # alerts
        validAlertTypes = ['STARTING', 'RUNNING', 'BACKOFF', 'STOPPING', 'FATAL', 'EXITED', 'STOPPED', 'UNKNOWN']

        clear()
        while True:
            console.rule("[bold blue]Choose Alerts", style="rule")
            console.print(f"Supervisor alert types: [dodger_blue3]\n{validAlertTypes}[/dodger_blue3]")

            console.print("Write out below a list of alert types separated by commas. Ex. \"Starting, Stopping...\"")
            console.print("Leave blank to use every alert type.")
            alerts = input()

            if alerts == "":
                alertTypes = validAlertTypes
                console.print("Using all alert types.")
                break
            else:
                alertTypes = alerts.split(", ")
                for i in alertTypes:
                    if i.upper() not in validAlertTypes:
                        console.print(f"Unknown alert type \"{i}\".", style="warn")
                        break
                else:
                    console.print("Alert types valid.")
                    break

        # formatting
        clear()
        while True:
            console.rule("[bold blue]Formatting", style="rule")
            console.print("[bold]Availible formats[/bold]: [dodger_blue3]{{process_name}}, {{timestamp}}, {{from_state}}, {{to_state}}[/dodger_blue3]")
            console.print("[bold]Example:[/bold] [dodger_blue3]\"{{process_name}} changed to state {{to_state}}\"[/dodger_blue3]")
            console.print("This field supports discords markdown format, see https://gist.github.com/matthewzring/9f7bbfd102003963f9be7dbcf7d40e51 for usage.")
            fmt = console.input("Write out below how you would like to format the message for this process, leave blank for default:\n")
            if fmt == "":
                fmt = "{{process_name}} changed to state {{to_state}}"
            prev = example_format(fmt, process_name)
            r = requests.post(url=webhookurl, json={'content':prev})  # send message
            console.print("[i dark_blue]Posted preview message to discord.[/i dark_blue]")
            accept = Confirm.ask("Does the message appear okay?")
            if accept:
                break
            else:
                console.print("Running formatting again.") # blank line
        # temp save
        processes[process_name] = {'webhookURL':webhookurl, 'alerts':alertTypes, 'message_format':fmt} # "webhookURL": "url", alerts:["STARTED", "EXITED"], "message_format":"{{process_name}} changed to state {{to_state}}"}
        # done
        add_more = Confirm.ask("Setup another process (y/n)?")
        if add_more: # yes
            clear()
            console.print("Adding another process.", style="info")
            continue
        else: # no
            break

def example_format(message, process_name):
    examples = {'{{process_name}}':process_name, '{{timestamp}}':str(datetime.datetime.now()), '{{from_state}}':'RUNNING', '{{to_state}}':'EXITED'}
    for i, j in examples.items():
        message = message.replace(i,j)
    return message

def saveConfig():
    console.print("[dodger_blue3]Saving configuration...[/dodger_blue3]")
    time.sleep(1)
    if os.path.exists("./config.yaml"):
        overwrite = Confirm.ask("[bold red]Warning file already exists. Overwrite?[/bold red]")
        if overwrite:
            with open("./config.yaml", "w") as f:
                f.write(yaml.dump(processes))
        else:
            console.print(f"Just in case, here's your config anyways: \n{yaml.dump(processes)}")
            exit()
    else:
        with open("./config.yaml", "w") as f:
            f.write(yaml.dump(processes, explicit_start=True))
    console.print("[bold blue]Config has been saved to config.yaml.[/bold blue]")
    exit()

if __name__ == "__main__":
    supervisorSetup()
    saveConfig()
