"""Core secure RAG engine for SREC Cypher Bot."""

import os
import sqlite3
from pathlib import Path
from typing import Dict, List

from openai import OpenAI

from policy_guard import is_query_allowed
from retriever import SRECRetriever
from validator import filter_safe_documents

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "db" / "logs.db"

REFUSAL_POLICY = (
    "🚫 This request cannot be processed because it violates the SREC Cypher Bot policy."
)
REFUSAL_CONTEXT = (
    "🚫 I can only answer from verified public SREC context. No safe context was found for this question."
)


class SRECCypherEngine:
    def __init__(self) -> None:
        self.retriever = SRECRetriever()
        self._init_db()

    def _init_db(self) -> None:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS query_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    status TEXT NOT NULL,
                    reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()

    def _log_query(self, query: str, status: str, reason: str = "") -> None:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT INTO query_logs (query, status, reason) VALUES (?, ?, ?)",
                (query, status, reason),
            )
            conn.commit()

    def _generate_answer(self, query: str, safe_docs: List[Dict]) -> str:
        context = "\n\n".join(f"- {doc['text']}" for doc in safe_docs)
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            return (
                "OPENAI_API_KEY is not configured. Based on approved context:\n\n"
                f"{context}\n\n"
                "Please configure OPENAI_API_KEY to get a generated natural-language response."
            )

        client = OpenAI(api_key=api_key)
        system_prompt = (
            "You are SREC Cypher Bot, a cybersecurity-aware assistant. "
            "Answer strictly from the provided context. "
            "If context is insufficient, clearly say you do not have enough approved information."
        )
        user_prompt = f"Question: {query}\n\nApproved Context:\n{context}"

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
        )
        return response.output_text.strip()

    def ask(self, query: str) -> Dict[str, str]:
        allowed, reason = is_query_allowed(query)
        if not allowed:
            self._log_query(query, "BLOCKED_POLICY", reason)
            return {"status": "BLOCKED_POLICY", "answer": REFUSAL_POLICY, "reason": reason}

        docs = self.retriever.search(query=query, top_k=4)
        safe_docs = filter_safe_documents(docs)

        if not safe_docs:
            self._log_query(query, "BLOCKED_CONFIDENTIAL", "No safe context available")
            return {
                "status": "BLOCKED_CONFIDENTIAL",
                "answer": REFUSAL_CONTEXT,
                "reason": "No safe context",
            }

        answer = self._generate_answer(query, safe_docs)
        self._log_query(query, "ALLOWED", "Context-validated")
        return {"status": "ALLOWED", "answer": answer, "reason": "OK"}
