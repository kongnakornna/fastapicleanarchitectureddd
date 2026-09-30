# ═══════════════════════════════════════════════════════════════
# Layer 0 — Base (LLM + Embeddings)
# ═══════════════════════════════════════════════════════════════
python create_module_llm.py all llm 5 llm --force
python create_module_embeddings.py all --force

# ═══════════════════════════════════════════════════════════════
# Layer 1 — Storage & Tools (VectorDB + ToolCalling + StructuredOutputs)
# ═══════════════════════════════════════════════════════════════
python create_module_vector_db.py all --force
python create_module_tool_calling.py all tool_calling 5 tool --force
python create_module_structured_outputs.py all --force

# ═══════════════════════════════════════════════════════════════
# Layer 2 — Retrieval & Frameworks (HybridSearch + LangChain + LlamaIndex)
# ═══════════════════════════════════════════════════════════════
python create_module_hybrid_search.py all --force
python create_module_langchain.py all --force
python create_module_llamaindex.py all --force

# ═══════════════════════════════════════════════════════════════
# Layer 3 — Application (RAG + AI Evaluation)
# ═══════════════════════════════════════════════════════════════
python create_module_rag.py all --force
python create_module_ai_evaluation.py all --force

# ═══════════════════════════════════════════════════════════════
# Migrate
# ═══════════════════════════════════════════════════════════════
alembic upgrade head
