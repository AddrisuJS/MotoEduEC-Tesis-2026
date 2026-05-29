async def asistente_rag(
    pregunta: str,
    perfil: dict,
    contexto_chromadb: list,
    historial: list
) -> dict:
    """
    M3 — Asistente RAG con ChromaDB + Claude API.
    contexto_chromadb: documentos recuperados de ChromaDB.
    """
    if USE_MOCK:
        return _mock_rag(pregunta, contexto_chromadb)

    import anthropic
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

    contexto_str = "\n\n".join([
        f"[Fuente: {d.get('fuente','LOTTTSV')}]\n{d.get('texto','')}"
        for d in contexto_chromadb
    ])

    system_prompt = _system_prompt_base() + _perfil_prompt(perfil) + f"""
    
    CONTEXTO DE LA BASE DE CONOCIMIENTO (LOTTTSV y catálogo):
    {contexto_str}
    
    INSTRUCCIÓN: Responde usando únicamente la información del contexto anterior.
    Cita el artículo o fuente específica al final de tu respuesta.
    Si la información no está en el contexto, indícalo claramente.
    """

    messages = historial[-6:] + [{"role": "user", "content": pregunta}]

    response = client.messages.create(
        model=CLAUDE_MODEL_SONNET,
        max_tokens=1000,
