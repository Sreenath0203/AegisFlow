import os
import json
import logging
import requests
from fastapi import HTTPException
from backend.config.settings import settings

logger = logging.getLogger("aegisflow.watsonx")

class WatsonxGraniteClient:
    """
    Real IBM watsonx.ai & IBM Granite LLM Client Integration.
    Connects to IBM Cloud IAM and watsonx.ai REST endpoints.
    """
    def __init__(self):
        self.reload_config()

    def reload_config(self):
        self.api_key = os.getenv("WATSONX_API_KEY") or getattr(settings, "WATSONX_API_KEY", None)
        self.project_id = os.getenv("WATSONX_PROJECT_ID") or getattr(settings, "WATSONX_PROJECT_ID", None)
        self.url = (os.getenv("WATSONX_URL") or getattr(settings, "WATSONX_URL", "https://us-south.ml.cloud.ibm.com")).rstrip('/')
        self.model_id = os.getenv("MODEL_ID") or getattr(settings, "MODEL_ID", "ibm/granite-4-h-small")
        self.access_token = getattr(self, "access_token", None)
        self.token_expiry = getattr(self, "token_expiry", 0)

    def get_iam_token(self) -> str:
        """Fetch IBM Cloud IAM bearer token with caching and retries."""
        import time
        self.reload_config()
        if not self.api_key:
            raise HTTPException(status_code=500, detail="IBM Cloud WATSONX_API_KEY environment variable is not configured.")

        # Return cached token if valid
        if self.access_token and time.time() < (self.token_expiry - 60):
            return self.access_token

        iam_url = "https://iam.cloud.ibm.com/identity/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": self.api_key
        }

        max_attempts = 3
        last_error = None

        for attempt in range(max_attempts):
            try:
                res = requests.post(iam_url, headers=headers, data=data, timeout=15)
                if res.status_code == 200:
                    token_data = res.json()
                    self.access_token = token_data.get("access_token")
                    expires_in = token_data.get("expires_in", 3600)
                    self.token_expiry = time.time() + expires_in
                    return self.access_token
                else:
                    logger.error(f"IBM IAM Auth error {res.status_code}: {res.text}")
                    last_error = f"IBM IAM Auth error {res.status_code}: {res.text}"
            except Exception as e:
                logger.warning(f"IBM IAM token fetch attempt {attempt + 1} failed: {e}")
                last_error = str(e)
            
            if attempt < max_attempts - 1:
                time.sleep(1.0)

        raise HTTPException(status_code=500, detail=f"IBM IAM Token request failed: {last_error}")

    def generate_text(self, prompt: str, system_prompt: str = None, max_tokens: int = 500) -> dict:
        """
        Executes real text generation against IBM watsonx.ai Granite endpoint.
        """
        token = self.get_iam_token()
        endpoint = f"{self.url}/ml/v1/text/generation?version=2023-05-29"

        sys_p = system_prompt or "You are IBM Granite LLM, an enterprise AI assistant for supply chain decision intelligence."
        full_input = f"<|system|>\n{sys_p}\n<|user|>\n{prompt}\n<|assistant|>\n"

        payload = {
            "input": full_input,
            "parameters": {
                "decoding_method": "greedy",
                "max_new_tokens": max_tokens
            },
            "model_id": self.model_id,
            "project_id": self.project_id
        }

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        max_attempts = 2
        for attempt in range(max_attempts):
            try:
                response = requests.post(endpoint, headers=headers, json=payload, timeout=45)
                if response.status_code != 200:
                    logger.error(f"watsonx.ai API Error {response.status_code}: {response.text}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"IBM watsonx.ai error (model_id='{self.model_id}'): {response.text}"
                    )

                res_json = response.json()
                results = res_json.get("results", [])
                generated_text = results[0].get("generated_text", "").strip() if results else ""
                return {
                    "status": "SUCCESS",
                    "text": generated_text,
                    "model": self.model_id
                }
            except HTTPException:
                raise
            except Exception as e:
                if attempt < max_attempts - 1:
                    logger.warning(f"watsonx.ai connection attempt {attempt+1} failed: {e}. Retrying...")
                    import time; time.sleep(1)
                else:
                    logger.error(f"watsonx.ai connection exception: {e}")
                    raise HTTPException(status_code=500, detail=f"IBM watsonx.ai connection error: {str(e)}")

    def analyze_risk(self, input_data: dict) -> dict:
        """
        Sends supply chain risk telemetry directly to IBM watsonx.ai Granite model
        and returns structured risk analysis JSON.
        """
        token = self.get_iam_token()
        endpoint = f"{self.url}/ml/v1/text/generation?version=2023-05-29"

        supplier = input_data.get("supplier", "Unknown Supplier")
        delay_days = input_data.get("shipment_delay_days", 0)
        inv_days = input_data.get("inventory_days", 0)
        weather = input_data.get("weather_risk", "None")
        reliability = input_data.get("supplier_reliability", 100)

        prompt = (
            f"Analyze supply chain risk for:\n"
            f"Supplier: {supplier}\n"
            f"Shipment Delay Days: {delay_days}\n"
            f"Inventory Days Remaining: {inv_days}\n"
            f"Weather Risk: {weather}\n"
            f"Supplier Reliability Score: {reliability}%\n\n"
            f"Return ONLY a raw JSON object with these exact keys:\n"
            f'  "risk_level" (string: "LOW", "MODERATE", "HIGH", or "CRITICAL"),\n'
            f'  "risk_score" (number: 0 to 100),\n'
            f'  "reason" (string concise explanation of key risk drivers),\n'
            f'  "recommendation" (string actionable mitigation advice),\n'
            f'  "confidence" (number between 0.0 and 1.0).\n'
        )

        full_input = f"<|system|>\nYou are IBM Granite LLM. Output raw valid JSON only. Do not include markdown or commentary.\n<|user|>\n{prompt}\n<|assistant|>\n"

        payload = {
            "input": full_input,
            "parameters": {
                "decoding_method": "greedy",
                "max_new_tokens": 400
            },
            "model_id": self.model_id,
            "project_id": self.project_id
        }

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        try:
            response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
            if response.status_code != 200:
                logger.error(f"watsonx.ai API Error {response.status_code}: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"IBM watsonx.ai error (model_id='{self.model_id}'): {response.text}"
                )

            res_json = response.json()
            results = res_json.get("results", [])
            if not results:
                raise HTTPException(status_code=500, detail="IBM watsonx.ai returned an empty results payload.")

            generated_text = results[0].get("generated_text", "").strip()
            
            # Clean markdown artifacts or stop tokens
            cleaned_text = generated_text.split("</|")[0].replace("```json", "").replace("```", "").strip()

            try:
                parsed = json.loads(cleaned_text)
            except Exception:
                start_idx = cleaned_text.find('{')
                end_idx = cleaned_text.rfind('}')
                if start_idx != -1 and end_idx != -1:
                    parsed = json.loads(cleaned_text[start_idx:end_idx+1])
                else:
                    raise HTTPException(status_code=500, detail=f"Failed to parse JSON response from IBM Granite output: '{cleaned_text}'")

            return {
                "risk_level": str(parsed.get("risk_level", "MODERATE")).strip().upper(),
                "risk_score": float(parsed.get("risk_score", 50.0)),
                "reason": str(parsed.get("reason", "IBM Granite analysis completed.")),
                "recommendation": str(parsed.get("recommendation", "Monitor supplier telemetry.")),
                "confidence": float(parsed.get("confidence", 0.90)),
                "model_id": self.model_id
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"watsonx.ai connection exception: {e}")
            raise HTTPException(status_code=500, detail=f"IBM watsonx.ai connection error: {str(e)}")

watsonx_client = WatsonxGraniteClient()
