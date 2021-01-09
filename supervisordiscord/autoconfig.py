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

logging.basicConfig(filename=script_dir+'/supervisordiscord.log',level=logging.INFO, format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',datefmt='%Y-%m-%d %H:%M:%S')

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
            json = {'content': f"**supervisordiscord is now active on this channel.**"}
            try:
                requests.post(url=webhookurl, json=json)  # send message
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
            console.print(f"Supervisor alert types: [bold dodger_blue3]\n{validAlertTypes}[/bold dodger_blue3]")

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
            console.print("[bold]Availible formats[/bold]: [bold dodger_blue3]{{process_name}}, {{from_state}}, {{to_state}}[/bold dodger_blue3]")
            console.print("[bold]Example:[/bold] [bold dodger_blue3]\"{{process_name}} changed to state {{to_state}}\"[/bold dodger_blue3]")
            console.print("Use datetime's strftime() format to insert timestamps. See https://strftime.org/ for reference.")
            console.print("This field supports discords markdown format, see https://gist.github.com/matthewzring/9f7bbfd102003963f9be7dbcf7d40e51 for usage.")
            fmt = console.input("Write out below how you would like to format the message for this process, leave blank for default:\n")
            if fmt == "":
                fmt = "{{process_name}} changed to state {{to_state}}"
            prev = example_format(fmt, process_name)
            requests.post(url=webhookurl, json={'content':prev})  # send message
            console.print("[i bold dodger_blue3]Posted preview message to discord.[/i bold dodger_blue3]")
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
    examples = {'{{process_name}}':process_name, '{{from_state}}':'RUNNING', '{{to_state}}':'EXITED'}
    for i, j in examples.items():
        message = message.replace(i,j)
    message = datetime.datetime.now().strftime(message)
    return message

def saveConfig():
    console.print("[bold dodger_blue3]Saving configuration...[/bold dodger_blue3]")
    time.sleep(1)

    if os.access("/etc/", os.W_OK):  # we can open /etc so save there
        if not os.path.exists("/etc/supervisordiscord"):
            os.mkdir("/etc/supervisordiscord")
        configLocation = "/etc/supervisordiscord/"
    else:
        configLocation = ""

    if os.path.exists(configLocation+"config.yaml"):
        overwrite = Confirm.ask(f"[bold red]Warning file {configLocation}config.yaml already exists. Overwrite?[/bold red]")
        if overwrite:
            with open(configLocation+"config.yaml", "w") as f:
                f.write(yaml.dump(processes, explicit_start=True))
                console.print(f"[bold blue]Config has been saved to {configLocation}config.yaml.[/bold blue]")
        else:
            console.print(f"Here is your auto generated config file:\n{yaml.dump(processes, explicit_start=True)}")
    else:
        with open(configLocation+"config.yaml", "w") as f:
            f.write(yaml.dump(processes, explicit_start=True))
            console.print(f"[bold blue]Config has been saved to {configLocation}config.yaml.[/bold blue]")

    exit()

def run():
    supervisorSetup()
    saveConfig()

if __name__ == "__main__":
    run()

