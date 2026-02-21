"""
Streaming interface for the Verbatim RAG system
Provides structured streaming of RAG processing stages
"""

from typing import AsyncGenerator, Dict, Any, List, Optional
import asyncio
import time
from .models import (
    DocumentWithHighlights,
)
from .core import VerbatimRAG


class StreamingRAG:
    """
    Streaming wrapper for VerbatimRAG that provides step-by-step processing
    """

    def __init__(self, rag: VerbatimRAG):
        self.rag = rag

    async def stream_query(
        self, question: str, num_docs: int = None, filter: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream a query response in stages:
        1. Documents (without highlights)
        2. Documents with highlights
        3. Final answer

        Args:
            question: The user's question
            num_docs: Optional number of documents to retrieve
            filter: Optional vector-store filter expression (passed to VerbatimIndex)

        Yields:
            Dictionary with type and data for each stage
        """
        original_k = self.rag.k
        try:
            # Set number of documents if specified
            if num_docs is not None:
                self.rag.k = num_docs

            # Step 1: Retrieve documents and send them without highlights
            # Some backends can fail if k is too large for the current collection;
            # if that happens, reduce k progressively until query succeeds.
            docs = None
            last_query_error = None
            for candidate_k in range(max(1, self.rag.k), 0, -1):
                try:
                    docs = self.rag.index.query(text=question, k=candidate_k, filter=filter)
                    break
                except Exception as e:
                    last_query_error = e

            if docs is None:
                yield {
                    "type": "error",
                    "error": f"retrieval_failed: {last_query_error}",
                    "done": True,
                }
                return

            valid_docs = [
                doc
                for doc in docs
                if isinstance(getattr(doc, "text", None), str) and doc.text.strip()
            ]
            dropped_docs = len(docs) - len(valid_docs)
            if dropped_docs > 0:
                yield {
                    "type": "progress",
                    "stage": "dropped_empty_documents",
                    "count": dropped_docs,
                }

            if not valid_docs:
                yield {
                    "type": "error",
                    "error": "retrieval_failed: all retrieved documents were empty",
                    "done": True,
                }
                return

            documents_without_highlights = [
                DocumentWithHighlights(
                    content=doc.text,
                    highlights=[],
                    title=doc.metadata.get("title", ""),
                    source=doc.metadata.get("source", ""),
                    metadata=doc.metadata,
                )
                for doc in valid_docs
            ]

            yield {
                "type": "documents",
                "data": [doc.model_dump() for doc in documents_without_highlights],
            }

            # Step 2: Extract spans and create highlights (non-numbered for interim UI)
            # Offload potentially blocking LLM extraction to a thread so we don't block the event loop
            extraction_start = time.time()
            try:
                relevant_spans = await asyncio.to_thread(
                    self.rag.extractor.extract_spans, question, valid_docs
                )
            except Exception as e:
                yield {
                    "type": "error",
                    "error": f"span_extraction_failed: {e}",
                    "done": True,
                }
                return
            extraction_duration = time.time() - extraction_start

            yield {
                "type": "progress",
                "stage": "extraction_complete",
                "elapsed_ms": int(extraction_duration * 1000),
            }
            interim_documents = []
            for doc in valid_docs:
                doc_content = doc.text
                doc_spans = relevant_spans.get(doc_content, [])
                if doc_spans:
                    highlights = self.rag.response_builder._create_highlights(
                        doc_content, doc_spans
                    )
                else:
                    highlights = []
                interim_documents.append(
                    DocumentWithHighlights(
                        content=doc_content,
                        highlights=highlights,
                        title=doc.metadata.get("title", ""),
                        source=doc.metadata.get("source", ""),
                        metadata=doc.metadata,
                    )
                )

            yield {
                "type": "highlights",
                "data": [d.model_dump() for d in interim_documents],
            }

            # Step 3: Generate answer using enhanced pipeline with new architecture
            # Rank spans and split into display vs citation-only
            display_spans, citation_spans = self.rag._rank_and_split_spans(
                relevant_spans
            )

            # Generate and fill template using template manager (async)
            try:
                answer = await self.rag.template_manager.process_async(
                    question, display_spans, citation_spans
                )
                answer = self.rag.response_builder.clean_answer(answer)
            except Exception as e:
                yield {
                    "type": "error",
                    "error": f"template_processing_failed: {e}",
                    "done": True,
                }
                return
            result = self.rag.response_builder.build_response(
                question=question,
                answer=answer,
                search_results=valid_docs,
                relevant_spans=relevant_spans,
                display_span_count=len(display_spans),
            )

            yield {"type": "answer", "data": result.model_dump(), "done": True}

        except Exception as e:
            yield {"type": "error", "error": str(e), "done": True}
        finally:
            # Restore original k value even for early returns/errors
            self.rag.k = original_k

    def stream_query_sync(
        self, question: str, num_docs: int = None, filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Synchronous version that returns all streaming stages as a list
        Useful for testing or when async is not needed
        """
        import asyncio

        async def collect_stream():
            stages = []
            async for stage in self.stream_query(question, num_docs, filter):
                stages.append(stage)
            return stages

        return asyncio.run(collect_stream())
