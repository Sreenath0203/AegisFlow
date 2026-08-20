import os
import json
import httpx
from dotenv import load_dotenv

load_dotenv()


class WatsonOrchestrateService:

    def __init__(self):
        self.base_url = os.getenv(
            "WATSON_ORCHESTRATE_URL",
            ""
        ).rstrip("/")

        self.agent_id = os.getenv(
            "WATSON_ORCHESTRATE_AGENT_ID",
            ""
        )

        self.api_key = os.getenv(
            "WATSON_ORCHESTRATE_API_KEY",
            ""
        )

    def _get_bearer_token(self):
        """
        Exchange the IBM API key for a temporary
        watsonx Orchestrate bearer token.
        """

        if not self.api_key:
            raise RuntimeError(
                "WATSON_ORCHESTRATE_API_KEY is not configured."
            )

        token_url = (
            "https://iam.platform.saas.ibm.com/"
            "siusermgr/api/1.0/apikeys/token"
        )

        try:
            response = httpx.post(
                token_url,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                json={
                    "apikey": self.api_key
                },
                timeout=30.0,
            )

            response.raise_for_status()

        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                "IBM authentication failed. "
                f"HTTP {exc.response.status_code}: "
                f"{exc.response.text}"
            )

        except httpx.RequestError as exc:
            raise RuntimeError(
                "Could not connect to IBM authentication service: "
                f"{exc}"
            )

        data = response.json()

        token = (
            data.get("access_token")
            or data.get("token")
        )

        if not token:
            raise RuntimeError(
                "IBM authentication response did not contain "
                "an access token."
            )

        return token

    def chat(
        self,
        message: str,
        conversation_history=None,
        thread_id=None,
    ):
        """
        Send a message to the deployed IBM watsonx
        Orchestrate agent.
        """

        if not self.base_url:
            raise RuntimeError(
                "WATSON_ORCHESTRATE_URL is not configured."
            )

        if not self.agent_id:
            raise RuntimeError(
                "WATSON_ORCHESTRATE_AGENT_ID is not configured."
            )

        if not message or not message.strip():
            raise RuntimeError(
                "Message cannot be empty."
            )

        token = self._get_bearer_token()

        url = (
            f"{self.base_url}"
            "/v1/orchestrate/runs"
            "?stream=true"
            "&stream_timeout=120000"
            "&multiple_content=true"
        )

        headers = {
            "Authorization": f"Bearer {token}",
            "IAM-API_KEY": self.api_key,
            "Accept": "text/event-stream",
            "Content-Type": "application/json",
        }

        payload = {
            "message": {
                "role": "user",
                "content": message.strip(),
            },
            "agent_id": self.agent_id,
        }

        # Continue an existing Orchestrate conversation
        if thread_id:
            payload["thread_id"] = thread_id

        try:
            with httpx.stream(
                "POST",
                url,
                headers=headers,
                json=payload,
                timeout=180.0,
            ) as response:

                response.raise_for_status()

                events = []

                # Accumulate raw bytes so we can decode as UTF-8
                # rather than relying on httpx's default charset
                # detection, which can produce mojibake (â€™ etc.)
                # when IBM returns UTF-8 text without an explicit
                # charset header.
                raw_bytes = b"".join(response.iter_bytes())

            # Decode once as UTF-8 with error replacement as safety net
            raw_text = raw_bytes.decode("utf-8", errors="replace")

            for raw_line in raw_text.splitlines():

                line = raw_line.strip()

                if not line:
                    continue

                # Handle Server-Sent Events format
                if line.startswith("data:"):
                    line = line[5:].strip()

                if not line:
                    continue

                if line == "[DONE]":
                    continue

                try:
                    event = json.loads(line)
                    events.append(event)

                except json.JSONDecodeError:
                    # Preserve unexpected plain-text chunks
                    events.append({
                        "type": "text",
                        "content": line,
                    })

            return self._build_response(
                events,
                original_thread_id=thread_id,
            )

        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                "IBM watsonx Orchestrate returned "
                f"HTTP {exc.response.status_code}: "
                f"{exc.response.text}"
            )

        except httpx.RequestError as exc:
            raise RuntimeError(
                "Could not connect to IBM watsonx Orchestrate: "
                f"{exc}"
            )

    def _build_response(
        self,
        events,
        original_thread_id=None,
    ):
        """
        Extract the assistant response from IBM
        watsonx Orchestrate streaming events.

        IBM message.delta structure:

        event
          -> data
             -> thread_id
             -> run_id
             -> delta
                -> role
                -> content[]
                   -> text
        """

        thread_id = original_thread_id
        run_id = None
        task_id = None
        message_id = None

        text_parts = []

        for event in events:

            if not isinstance(event, dict):
                continue

            # -------------------------------------------------
            # Some IBM events may contain IDs at the top level
            # -------------------------------------------------

            run_id = (
                event.get("run_id")
                or event.get("runId")
                or run_id
            )

            task_id = (
                event.get("task_id")
                or event.get("taskId")
                or task_id
            )

            message_id = (
                event.get("message_id")
                or event.get("messageId")
                or message_id
            )

            # -------------------------------------------------
            # Actual IBM streaming response is inside data
            # -------------------------------------------------

            data = event.get("data")

            if not isinstance(data, dict):
                continue

            # Thread ID
            thread_id = (
                data.get("thread_id")
                or data.get("threadId")
                or thread_id
            )

            # Run ID
            run_id = (
                data.get("run_id")
                or data.get("runId")
                or run_id
            )

            # Task ID
            task_id = (
                data.get("task_id")
                or data.get("taskId")
                or task_id
            )

            # Message ID
            message_id = (
                data.get("message_id")
                or data.get("messageId")
                or message_id
            )

            # -------------------------------------------------
            # IBM message.delta event
            # -------------------------------------------------

            delta = data.get("delta")

            if not isinstance(delta, dict):
                continue

            content = delta.get("content")

            if not isinstance(content, list):
                continue

            for item in content:

                if not isinstance(item, dict):
                    continue

                text = item.get("text")

                if isinstance(text, str):
                    text_parts.append(text)

        # IBM sends the answer in small streamed chunks.
        # Join them together without adding extra spaces.
        response_text = "".join(text_parts).strip()

        return {
            "thread_id": thread_id,
            "run_id": run_id,
            "task_id": task_id,
            "message_id": message_id,
            "response": response_text,
            "events": events,
        }


watson_orchestrate_service = WatsonOrchestrateService()