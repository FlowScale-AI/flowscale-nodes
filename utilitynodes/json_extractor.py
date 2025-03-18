import json

class ExtractPropertyNode:
    """
    A ComfyUI node to:
    1) Accept a JSON string.
    2) Extract the value of a given property key.
    3) Return the property value as a string.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_data": ("STRING", {"multiline": True}),  # The raw JSON string
                "property_key": ("STRING", {}),               # The key to extract
            },
            "optional": {
                "silent_errors": ("BOOLEAN", ),               # Toggle quiet/fail-hard mode
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "extract_property"
    CATEGORY = "FlowScale/Utilities"

    def extract_property(self, json_data, property_key, silent_errors=True):
        """
        Extracts the given property_key from the json_data.
        """
        # 1. Validate inputs
        if not json_data.strip():
            if silent_errors:
                return ("No JSON data provided.",)
            raise ValueError("No JSON data provided.")

        if not property_key.strip():
            if silent_errors:
                return ("No property key provided.",)
            raise ValueError("No property key specified for extraction.")

        # 2. Parse the JSON
        try:
            parsed_json = json.loads(json_data)
        except Exception as e:
            if silent_errors:
                return (f"Failed to parse JSON: {e}",)
            raise ValueError(f"Failed to parse JSON: {e}")

        # 3. Extract the property
        try:
            value = parsed_json[property_key]
            # Convert anything to string for a consistent return
            return (str(value),)
        except KeyError:
            if silent_errors:
                return (f"Property '{property_key}' not found in JSON.",)
            raise ValueError(f"Property '{property_key}' not found in JSON.")
        except Exception as e:
            if silent_errors:
                return (f"Unexpected error extracting property: {e}",)
            raise ValueError(f"Unexpected error extracting property: {e}")
