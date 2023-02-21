import subprocess


def run(cmd, format_output_str=False, **run_kwargs):
    result = subprocess.run(cmd, **run_kwargs)
    command_results = {}
    if hasattr(result, "args"):
        command_results.update({"command": " ".join((getattr(result, "args")))})
    if hasattr(result, "returncode"):
        command_results.update({"returncode": getattr(result, "returncode")})
    if hasattr(result, "stderr"):
        command_results.update({"error": getattr(result, "stderr")})
    if hasattr(result, "stdout"):
        command_results.update({"output": getattr(result, "stdout")})

    if format_output_str:
        for key, value in command_results.items():
            command_results[key] = str(value)
    return command_results