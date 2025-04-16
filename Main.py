import controller.Controller as controller
import service.JsonHandling as Service


config = Service.read_json("config/config.json")
getRecipients = config["recipients"]

print("Running...")
controller.send_discord_message(getRecipients)