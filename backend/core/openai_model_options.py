"""Request options for the GPT-4 replacement, without changing model overrides."""


def response_model_options(model: str) -> dict:
    options = {"model": model}
    # Preserve the non-reasoning latency baseline and temperature compatibility.
    # Other explicitly configured models retain their existing request options.
    if model == "gpt-6-luna":
        options["reasoning"] = {"effort": "none"}
    return options
