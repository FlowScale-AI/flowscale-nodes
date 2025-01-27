import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebhookSender:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "webhook_url": ("STRING",),
                "property_name": ("STRING",),
                "property_value": ("STRING",),
                "identifier": ("STRING",),
            },
            "optional": {
                "context": ("STRING",),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "send_to_webhook"
    CATEGORY = "Custom/Webhook"

    def send_to_webhook(self, webhook_url, property_name, property_value, identifier, context=None):
        try:
            logger.info("Sending to webhook")
            input_dict = {property_name: property_value, "identifier": identifier, "context": context}
            response = requests.post(webhook_url, json=input_dict)
            response.raise_for_status()
            logger.info(response.status_code)
            return (f"Success: {response.status_code}",)
        except requests.exceptions.RequestException as e:
            return (f"Error: {str(e)}",)
