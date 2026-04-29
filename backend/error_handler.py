import traceback


# ── Custom exception types ────────────────────────────────────────────────────

class PipelineError(Exception):
    """Base exception for all Machine Intelligence pipeline errors."""
    pass

class ComponentNotFoundError(PipelineError):
    pass

class PinAllocationError(PipelineError):
    pass

class FirmwareBuildError(PipelineError):
    pass

class BoardNotFoundError(PipelineError):
    pass

class LLMError(PipelineError):
    pass


# ── Centralized handler ───────────────────────────────────────────────────────

def handle_pipeline_error(stage: str, error: Exception):
    """
    Log a pipeline error with context and a user-friendly hint.

    Args:
        stage: name of the pipeline step where the error occurred
        error: the exception that was raised
    """

    print(f"\n{'='*50}")
    print(f"[ERROR] Stage : {stage}")
    print(f"[ERROR] Type  : {type(error).__name__}")
    print(f"[ERROR] Detail: {error}")

    if isinstance(error, ComponentNotFoundError):
        print("[HINT] Register the component in component_registry.py "
              "and add its class in the components/ folder.")

    elif isinstance(error, PinAllocationError):
        print("[HINT] The board may not have enough GPIO pins. "
              "Try a board with more pins or reduce the number of components.")

    elif isinstance(error, FirmwareBuildError):
        print("[HINT] Check firmware_builder.py and the component generate_*() methods.")

    elif isinstance(error, BoardNotFoundError):
        print("[HINT] Add a JSON profile for this board in the pin_profiles/ folder.")

    elif isinstance(error, LLMError):
        print("[HINT] Ensure Ollama is running (ollama serve) and the model is pulled.")

    elif isinstance(error, FileNotFoundError):
        print("[HINT] Check that all required files and directories exist.")

    else:
        print("[HINT] Unexpected error — full traceback:")
        traceback.print_exc()

    print(f"{'='*50}\n")