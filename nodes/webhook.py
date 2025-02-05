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
                "property_name_1": ("STRING",),
                "property_value_1": ("STRING",),
                "property_name_2": ("STRING",),
                "property_value_2": ("STRING",),
                "property_name_3": ("STRING",),
                "property_value_3": ("STRING",),
                "property_name_4": ("STRING",),
                "property_value_4": ("STRING",),                
            },
            "optional": {
                "context": ("STRING",),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "send_to_webhook"
    CATEGORY = "Custom/Webhook"

    def send_to_webhook(self, webhook_url, property_name_1, property_value_1, property_name_2, property_value_2, property_name_3, property_value_3, property_name_4, property_value_4, context=None):
        try:
            logger.info("Sending to webhook")
            input_dict = {
                property_name_1: property_value_1,
                property_name_2: property_value_2,
                property_name_3: property_value_3,
                property_name_4: property_value_4,
            }
            
            if context:
                input_dict["context"] = context
                
            response = requests.post(webhook_url, json=input_dict)
            response.raise_for_status()
            logger.info(response.status_code)
            return (f"Success: {response.status_code}",)
        except requests.exceptions.RequestException as e:
            return (f"Error: {str(e)}",)
