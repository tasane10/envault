"""Entry point that assembles all sub-command groups into the main CLI."""

import click
from envault.cli import cli
from envault.audit_cli import audit_cmd
from envault.diff_cli import diff_cmd
from envault.rotate_cli import rotate_cmd
from envault.search_cli import search_cmd
from envault.copy_cli import copy_cmd
from envault.snapshot_cli import snapshot_cmd
from envault.tag_cli import tag_cmd
from envault.ttl_cli import ttl_cmd
from envault.template_cli import template_cmd
from envault.lint_cli import lint_cmd
from envault.alias_cli import alias_cmd
from envault.watch_cli import watch_cmd
from envault.schema_cli import schema_cmd
from envault.env_check_cli import check_cmd as env_check_cmd
from envault.share_cli import share_cmd
from envault.env_inject_cli import inject_cmd
from envault.remote_cli import remote_cmd
from envault.hook_cli import hook_cmd
from envault.pin_cli import pin_cmd
from envault.namespace_cli import namespace_cmd
from envault.acl_cli import acl_cmd
from envault.compress_cli import compress_cmd


cli.add_command(audit_cmd, "audit")
cli.add_command(diff_cmd, "diff")
cli.add_command(rotate_cmd, "rotate")
cli.add_command(search_cmd, "search")
cli.add_command(copy_cmd, "copy")
cli.add_command(snapshot_cmd, "snapshot")
cli.add_command(tag_cmd, "tag")
cli.add_command(ttl_cmd, "ttl")
cli.add_command(template_cmd, "template")
cli.add_command(lint_cmd, "lint")
cli.add_command(alias_cmd, "alias")
cli.add_command(watch_cmd, "watch")
cli.add_command(schema_cmd, "schema")
cli.add_command(env_check_cmd, "env-check")
cli.add_command(share_cmd, "share")
cli.add_command(inject_cmd, "inject")
cli.add_command(remote_cmd, "remote")
cli.add_command(hook_cmd, "hook")
cli.add_command(pin_cmd, "pin")
cli.add_command(namespace_cmd, "namespace")
cli.add_command(acl_cmd, "acl")
cli.add_command(compress_cmd, "compress")


def main():
    cli()


if __name__ == "__main__":
    main()
