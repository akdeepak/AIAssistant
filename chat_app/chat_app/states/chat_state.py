import asyncio
import os
from typing import List, TypedDict

import reflex as rx
import requests


class Message(TypedDict):
    text: str
    is_ai: bool


class ChatState(rx.State):
    messages: List[Message] = []
    typing: bool = False
    has_openai_key: bool = "OPENAI_API_KEY" in os.environ
    # The currently-selected assistant's knowledge base ID, set when
    # the user clicks a preset card on the dashboard.
    knowledge_base_id: str | None = None

    @rx.event
    def clear_messages(self):
        """Clears all chat messages and resets typing status."""
        self.typing = False
        self.messages = []

    @rx.event
    def select_assistant(self, knowledge_base_id: str | None):
        """Select the active assistant/knowledge base.

        Called when a preset card is clicked. This also clears any
        existing conversation so the new chat starts fresh.
        """

        self.knowledge_base_id = knowledge_base_id
        self.typing = False
        self.messages = []

    @rx.event
    def send_message(self, form_data: dict):
        """Adds a user message and triggers AI response generation."""
        if self.typing:
            return
        message = form_data["message"].strip()
        if message:
            self.messages.append({"text": message, "is_ai": False})
            self.messages.append({"text": "", "is_ai": True})
            self.typing = True
            yield ChatState.generate_response

    @rx.event(background=True)
    async def generate_response(self):
        """Generates a response by calling the backend chat API.

        The backend is expected to accept a JSON payload with the
        conversation history and return a JSON object containing a
        "reply" field with the assistant's response.
        """

        # Snapshot messages and selected knowledge base at the start to
        # avoid race conditions.
        async with self:
            messages_to_send = list(self.messages)
            kb_id = self.knowledge_base_id
            if not messages_to_send:
                self.typing = False
                return

        # Take the most recent user message as the query.
        query_text = ""
        for m in reversed(messages_to_send):
            if not m["is_ai"]:
                query_text = m["text"]
                break

        # If no assistant is selected, return a helpful error.
        if not kb_id:
            reply = "No assistant selected. Please go to the dashboard and choose one of the assistant templates first."
            async with self:
                if self.messages:
                    self.messages[-1]["text"] = reply
                self.typing = False
            return

        payload = {
            "knowledge_base_id": kb_id,
            "query": query_text,
        }

        try:
            # Call the backend chat endpoint with the selected
            # knowledge base and the user's query.
            response = requests.post(
                "http://localhost:9000/llama-faq/query",
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()

            # Backend contract: { "response": "..." }
            reply = data.get("response", "")
            print("Received reply from chat API:", reply)
        except Exception as e:
            reply = f"Error contacting chat API: {e!s}"

        # Write the reply into the last assistant message.
        async with self:
            if self.messages:
                self.messages[-1]["text"] = reply
            self.typing = False
