import argparse

from gen_vm_image.cli.parsers.actions import PositionalArgumentsAction
from gen_vm_image.cli.parsers.single import single_group


def api():
    """Extract the default expected arguments and options from the argparser."""
    parser = argparse.ArgumentParser()
    single_group(parser)
    default_args = []
    default_options = {}

    for action in parser._actions:
        if isinstance(action, argparse._StoreAction):
            # Strip the leading double dash
            striped_key = action.option_strings[1].strip("--")
            key = striped_key.replace("-", "_")
            default_options[key] = action.default
        if isinstance(action, PositionalArgumentsAction):
            default_args.append(action.dest)
    return default_args, default_options
