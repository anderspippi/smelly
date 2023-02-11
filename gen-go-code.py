#!./smelly/launcher/smelly +launch
# License: GPLv3 Copyright: 2022, anders Goyal <anders at backbiter-no.net>

import io
import json
import os
import subprocess
import sys
from contextlib import contextmanager, suppress
from functools import lru_cache
from typing import Any, Dict, Iterator, List, Optional, Sequence, Set, Tuple, Union

import smelly.constants as kc
from wellies.tui.operations import Mode
from wellies.tui.spinners import spinners
from smelly.cli import (
    CompletionSpec,
    GoOption,
    go_options_for_seq,
    parse_option_spec,
    serialize_as_go_string,
)
from smelly.guess_mime_type import text_mimes
from smelly.key_encoding import config_mod_map
from smelly.key_names import character_key_name_aliases, functional_key_name_aliases
from smelly.options.types import Options
from smelly.rc.base import RemoteCommand, all_command_names, command_for_name
from smelly.remote_control import global_options_spec
from smelly.rgb import color_names

changed: List[str] = []


# Utils {{{

def serialize_go_dict(x: Union[Dict[str, int], Dict[int, str], Dict[int, int], Dict[str, str]]) -> str:
    ans = []

    def s(x: Union[int, str]) -> str:
        if isinstance(x, int):
            return str(x)
        return f'"{serialize_as_go_string(x)}"'

    for k, v in x.items():
        ans.append(f'{s(k)}: {s(v)}')
    return '{' + ', '.join(ans) + '}'


def replace(template: str, **kw: str) -> str:
    for k, v in kw.items():
        template = template.replace(k, v)
    return template
# }}}


# Completions {{{

@lru_cache
def kitten_cli_docs(kitten: str) -> Any:
    from wellies.runner import get_kitten_cli_docs
    return get_kitten_cli_docs(kitten)


@lru_cache
def go_options_for_kitten(kitten: str) -> Tuple[Sequence[GoOption], Optional[CompletionSpec]]:
    kcd = kitten_cli_docs(kitten)
    if kcd:
        ospec = kcd['options']
        return (tuple(go_options_for_seq(parse_option_spec(ospec())[0])), kcd.get('args_completion'))
    return (), None


def generate_wellies_completion() -> None:
    from wellies.runner import all_kitten_names, get_kitten_wrapper_of
    for kitten in sorted(all_kitten_names()):
        kn = 'kitten_' + kitten
        print(f'{kn} := plus_kitten.AddSubCommand(&cli.Command{{Name:"{kitten}", Group: "wellies"}})')
        wof = get_kitten_wrapper_of(kitten)
        if wof:
            print(f'{kn}.ArgCompleter = cli.CompletionForWrapper("{serialize_as_go_string(wof)}")')
            print(f'{kn}.OnlyArgsAllowed = true')
            continue
        gopts, ac = go_options_for_kitten(kitten)
        if gopts or ac:
            for opt in gopts:
                print(opt.as_option(kn))
            if ac is not None:
                print(''.join(ac.as_go_code(kn + '.ArgCompleter', ' = ')))
        else:
            print(f'{kn}.HelpText = ""')


@lru_cache
def clone_safe_launch_opts() -> Sequence[GoOption]:
    from smelly.launch import clone_safe_opts, options_spec
    ans = []
    allowed = clone_safe_opts()
    for o in go_options_for_seq(parse_option_spec(options_spec())[0]):
        if o.obj_dict['name'] in allowed:
            ans.append(o)
    return tuple(ans)


def completion_for_launch_wrappers(*names: str) -> None:
    for o in clone_safe_launch_opts():
        for name in names:
            print(o.as_option(name))


def generate_completions_for_smelly() -> None:
    from smelly.config import option_names_for_completion
    print('package completion\n')
    print('import "smelly/tools/cli"')
    print('import "smelly/tools/cmd/tool"')
    print('import "smelly/tools/cmd/at"')
    conf_names = ', '.join((f'"{serialize_as_go_string(x)}"' for x in option_names_for_completion()))
    print('var smelly_option_names_for_completion = []string{' + conf_names + '}')

    print('func smelly(root *cli.Command) {')

    # The smelly exe
    print('k := root.AddSubCommand(&cli.Command{'
          'Name:"smelly", SubCommandIsOptional: true, ArgCompleter: cli.CompleteExecutableFirstArg, SubCommandMustBeFirst: true })')
    print('kt := root.AddSubCommand(&cli.Command{Name:"kitten", SubCommandMustBeFirst: true })')
    print('tool.smellyToolEntryPoints(kt)')
    for opt in go_options_for_seq(parse_option_spec()[0]):
        print(opt.as_option('k'))

    # smelly +
    print('plus := k.AddSubCommand(&cli.Command{Name:"+", Group:"Entry points", ShortDescription: "Various special purpose tools and wellies"})')

    # smelly +launch
    print('plus_launch := plus.AddSubCommand(&cli.Command{'
          'Name:"launch", Group:"Entry points", ShortDescription: "Launch Python scripts", ArgCompleter: complete_plus_launch})')
    print('k.AddClone("", plus_launch).Name = "+launch"')

    # smelly +list-fonts
    print('plus_list_fonts := plus.AddSubCommand(&cli.Command{'
          'Name:"list-fonts", Group:"Entry points", ShortDescription: "List all available monospaced fonts"})')
    print('k.AddClone("", plus_list_fonts).Name = "+list-fonts"')

    # smelly +runpy
    print('plus_runpy := plus.AddSubCommand(&cli.Command{'
          'Name: "runpy", Group:"Entry points", ArgCompleter: complete_plus_runpy, ShortDescription: "Run Python code"})')
    print('k.AddClone("", plus_runpy).Name = "+runpy"')

    # smelly +open
    print('plus_open := plus.AddSubCommand(&cli.Command{'
          'Name:"open", Group:"Entry points", ArgCompleter: complete_plus_open, ShortDescription: "Open files and URLs"})')
    print('for _, og := range k.OptionGroups { plus_open.OptionGroups = append(plus_open.OptionGroups, og.Clone(plus_open)) }')
    print('k.AddClone("", plus_open).Name = "+open"')

    # smelly +kitten
    print('plus_kitten := plus.AddSubCommand(&cli.Command{Name:"kitten", Group:"wellies", SubCommandMustBeFirst: true})')
    generate_wellies_completion()
    print('k.AddClone("", plus_kitten).Name = "+kitten"')

    # @
    print('at.EntryPoint(k)')

    # clone-in-smelly, edit-in-smelly
    print('cik := root.AddSubCommand(&cli.Command{Name:"clone-in-smelly"})')
    completion_for_launch_wrappers('cik')

    print('}')
    print('func init() {')
    print('cli.RegisterExeForCompletion(smelly)')
    print('}')
# }}}


# rc command wrappers {{{
json_field_types: Dict[str, str] = {
    'bool': 'bool', 'str': 'escaped_string', 'list.str': '[]escaped_string', 'dict.str': 'map[escaped_string]escaped_string', 'float': 'float64', 'int': 'int',
    'scroll_amount': 'any', 'spacing': 'any', 'colors': 'any',
}


def go_field_type(json_field_type: str) -> str:
    q = json_field_types.get(json_field_type)
    if q:
        return q
    if json_field_type.startswith('choices.'):
        return 'string'
    if '.' in json_field_type:
        p, r = json_field_type.split('.', 1)
        p = {'list': '[]', 'dict': 'map[string]'}[p]
        return p + go_field_type(r)
    raise TypeError(f'Unknown JSON field type: {json_field_type}')


class JSONField:

    def __init__(self, line: str) -> None:
        field_def = line.split(':', 1)[0]
        self.required = False
        self.field, self.field_type = field_def.split('/', 1)
        if self.field.endswith('+'):
            self.required = True
            self.field = self.field[:-1]
        self.struct_field_name = self.field[0].upper() + self.field[1:]

    def go_declaration(self) -> str:
        return self.struct_field_name + ' ' + go_field_type(self.field_type) + f'`json:"{self.field},omitempty"`'


def go_code_for_remote_command(name: str, cmd: RemoteCommand, template: str) -> str:
    template = '\n' + template[len('//go:build exclude'):]
    NO_RESPONSE_BASE = 'false'
    af: List[str] = []
    a = af.append
    af.extend(cmd.args.as_go_completion_code('ans'))
    od: List[str] = []
    option_map: Dict[str, GoOption] = {}
    for o in rc_command_options(name):
        option_map[o.go_var_name] = o
        a(o.as_option('ans'))
        if o.go_var_name in ('NoResponse', 'ResponseTimeout'):
            continue
        od.append(o.struct_declaration())
    jd: List[str] = []
    json_fields = []
    field_types: Dict[str, str] = {}
    for line in cmd.protocol_spec.splitlines():
        line = line.strip()
        if ':' not in line:
            continue
        f = JSONField(line)
        json_fields.append(f)
        field_types[f.field] = f.field_type
        jd.append(f.go_declaration())
    jc: List[str] = []
    handled_fields: Set[str] = set()
    jc.extend(cmd.args.as_go_code(name, field_types, handled_fields))

    unhandled = {}
    used_options = set()
    for field in json_fields:
        oq = (cmd.field_to_option_map or {}).get(field.field, field.field)
        oq = ''.join(x.capitalize() for x in oq.split('_'))
        if oq in option_map:
            o = option_map[oq]
            used_options.add(oq)
            if field.field_type == 'str':
                jc.append(f'payload.{field.struct_field_name} = escaped_string(options_{name}.{o.go_var_name})')
            elif field.field_type == 'list.str':
                jc.append(f'payload.{field.struct_field_name} = escape_list_of_strings(options_{name}.{o.go_var_name})')
            elif field.field_type == 'dict.str':
                jc.append(f'payload.{field.struct_field_name} = escape_dict_of_strings(options_{name}.{o.go_var_name})')
            else:
                jc.append(f'payload.{field.struct_field_name} = options_{name}.{o.go_var_name}')
        elif field.field in handled_fields:
            pass
        else:
            unhandled[field.field] = field
    for x in tuple(unhandled):
        if x == 'match_window' and 'Match' in option_map and 'Match' not in used_options:
            used_options.add('Match')
            o = option_map['Match']
            field = unhandled[x]
            if field.field_type == 'str':
                jc.append(f'payload.{field.struct_field_name} = escaped_string(options_{name}.{o.go_var_name})')
            else:
                jc.append(f'payload.{field.struct_field_name} = options_{name}.{o.go_var_name}')
            del unhandled[x]
    if unhandled:
        raise SystemExit(f'Cant map fields: {", ".join(unhandled)} for cmd: {name}')
    if name != 'send_text':
        unused_options = set(option_map) - used_options - {'NoResponse', 'ResponseTimeout'}
        if unused_options:
            raise SystemExit(f'Unused options: {", ".join(unused_options)} for command: {name}')

    argspec = cmd.args.spec
    if argspec:
        argspec = ' ' + argspec
    ans = replace(
        template,
        CMD_NAME=name, __FILE__=__file__, CLI_NAME=name.replace('_', '-'),
        SHORT_DESC=serialize_as_go_string(cmd.short_desc),
        LONG_DESC=serialize_as_go_string(cmd.desc.strip()),
        IS_ASYNC='true' if cmd.is_asynchronous else 'false',
        NO_RESPONSE_BASE=NO_RESPONSE_BASE, ADD_FLAGS_CODE='\n'.join(af),
        WAIT_TIMEOUT=str(cmd.response_timeout),
        OPTIONS_DECLARATION_CODE='\n'.join(od),
        JSON_DECLARATION_CODE='\n'.join(jd),
        JSON_INIT_CODE='\n'.join(jc), ARGSPEC=argspec,
        STRING_RESPONSE_IS_ERROR='true' if cmd.string_return_is_error else 'false',
        STREAM_WANTED='true' if cmd.reads_streaming_data else 'false',
    )
    return ans
# }}}


# wellies {{{

@lru_cache
def wrapped_wellies() -> Sequence[str]:
    with open('shell-integration/ssh/smelly') as f:
        for line in f:
            if line.startswith('    wrapped_wellies="'):
                val = line.strip().partition('"')[2][:-1]
                return tuple(sorted(filter(None, val.split())))
    raise Exception('Failed to read wrapped wellies from smelly wrapper script')


def kitten_clis() -> None:
    for kitten in wrapped_wellies():
        with replace_if_needed(f'tools/cmd/{kitten}/cli_generated.go'):
            od = []
            kcd = kitten_cli_docs(kitten)
            has_underscore = '_' in kitten
            print(f'package {kitten}')
            print('import "smelly/tools/cli"')
            print('func create_cmd(root *cli.Command, run_func func(*cli.Command, *Options, []string)(int, error)) {')
            print('ans := root.AddSubCommand(&cli.Command{')
            print(f'Name: "{kitten}",')
            print(f'ShortDescription: "{serialize_as_go_string(kcd["short_desc"])}",')
            if kcd['usage']:
                print(f'Usage: "[options] {serialize_as_go_string(kcd["usage"])}",')
            print(f'HelpText: "{serialize_as_go_string(kcd["help_text"])}",')
            print('Run: func(cmd *cli.Command, args []string) (int, error) {')
            print('opts := Options{}')
            print('err := cmd.GetOptionValues(&opts)')
            print('if err != nil { return 1, err }')
            print('return run_func(cmd, &opts, args)},')
            if has_underscore:
                print('Hidden: true,')
            print('})')
            gopts, ac = go_options_for_kitten(kitten)
            for opt in gopts:
                print(opt.as_option('ans'))
                od.append(opt.struct_declaration())
            if ac is not None:
                print(''.join(ac.as_go_code('ans.ArgCompleter', ' = ')))
            if has_underscore:
                print("clone := root.AddClone(ans.Group, ans)")
                print('clone.Hidden = false')
                print(f'clone.Name = "{serialize_as_go_string(kitten.replace("_", "-"))}"')
            print('}')
            print('type Options struct {')
            print('\n'.join(od))
            print('}')

# }}}


# Constants {{{

def generate_spinners() -> str:
    ans = ['package tui', 'import "time"', 'func NewSpinner(name string) *Spinner {', 'var ans *Spinner', 'switch name {']
    a = ans.append
    for name, spinner in spinners.items():
        a(f'case "{serialize_as_go_string(name)}":')
        a('ans = &Spinner{')
        a(f'Name: "{serialize_as_go_string(name)}",')
        a(f'interval: {spinner["interval"]},')
        frames = ', '.join(f'"{serialize_as_go_string(x)}"' for x in spinner['frames'])
        a(f'frames: []string{{{frames}}},')
        a('}')
    a('}')
    a('if ans != nil {')
    a('ans.interval *= time.Millisecond')
    a('ans.current_frame = -1')
    a('ans.last_change_at = time.Now().Add(-ans.interval)')
    a('}')
    a('return ans}')
    return '\n'.join(ans)


def generate_color_names() -> str:
    return 'package style\n\nvar ColorNames = map[string]RGBA{' + '\n'.join(
        f'\t"{name}": RGBA{{ Red:{val.red}, Green:{val.green}, Blue:{val.blue} }},'
        for name, val in color_names.items()
    ) + '\n}' + '\n\nvar ColorTable = [256]uint32{' + ', '.join(
        f'{x}' for x in Options.color_table) + '}\n'


def load_ref_map() -> Dict[str, Dict[str, str]]:
    with open('smelly/docs_ref_map_generated.h') as f:
        raw = f.read()
    raw = raw.split('{', 1)[1].split('}', 1)[0]
    data = json.loads(bytes(bytearray(json.loads(f'[{raw}]'))))
    return data  # type: ignore


def generate_constants() -> str:
    ref_map = load_ref_map()
    dp = ", ".join(map(lambda x: f'"{serialize_as_go_string(x)}"', kc.default_pager_for_help))
    return f'''\
package smelly

type VersionType struct {{
    Major, Minor, Patch int
}}
const VersionString string = "{kc.str_version}"
const WebsiteBaseURL string = "{kc.website_base_url}"
const VCSRevision string = ""
const RC_ENCRYPTION_PROTOCOL_VERSION string = "{kc.RC_ENCRYPTION_PROTOCOL_VERSION}"
const IsFrozenBuild bool = false
const IsStandaloneBuild bool = false
const HandleTermiosSignals = {Mode.HANDLE_TERMIOS_SIGNALS.value[0]}
var Version VersionType = VersionType{{Major: {kc.version.major}, Minor: {kc.version.minor}, Patch: {kc.version.patch},}}
var DefaultPager []string = []string{{ {dp} }}
var FunctionalKeyNameAliases = map[string]string{serialize_go_dict(functional_key_name_aliases)}
var CharacterKeyNameAliases = map[string]string{serialize_go_dict(character_key_name_aliases)}
var ConfigModMap = map[string]uint16{serialize_go_dict(config_mod_map)}
var RefMap = map[string]string{serialize_go_dict(ref_map['ref'])}
var DocTitleMap = map[string]string{serialize_go_dict(ref_map['doc'])}
'''  # }}}


# Boilerplate {{{

@contextmanager
def replace_if_needed(path: str, show_diff: bool = False) -> Iterator[io.StringIO]:
    buf = io.StringIO()
    origb = sys.stdout
    sys.stdout = buf
    try:
        yield buf
    finally:
        sys.stdout = origb
    orig = ''
    with suppress(FileNotFoundError), open(path, 'r') as f:
        orig = f.read()
    new = buf.getvalue()
    new = f'// Code generated by {os.path.basename(__file__)}; DO NOT EDIT.\n\n' + new
    if orig != new:
        changed.append(path)
        if show_diff:
            with open(path + '.new', 'w') as f:
                f.write(new)
                subprocess.run(['diff', '-Naurp', path, f.name], stdout=open('/dev/tty', 'w'))
                os.remove(f.name)
        with open(path, 'w') as f:
            f.write(new)


@lru_cache(maxsize=256)
def rc_command_options(name: str) -> Tuple[GoOption, ...]:
    cmd = command_for_name(name)
    return tuple(go_options_for_seq(parse_option_spec(cmd.options_spec or '\n\n')[0]))


def update_at_commands() -> None:
    with open('tools/cmd/at/template.go') as f:
        template = f.read()
    for name in all_command_names():
        cmd = command_for_name(name)
        code = go_code_for_remote_command(name, cmd, template)
        dest = f'tools/cmd/at/cmd_{name}_generated.go'
        with replace_if_needed(dest) as f:
            f.write(code)
    struct_def = []
    opt_def = []
    for o in go_options_for_seq(parse_option_spec(global_options_spec())[0]):
        struct_def.append(o.struct_declaration())
        opt_def.append(o.as_option(depth=1, group="Global options"))
    sdef = '\n'.join(struct_def)
    odef = '\n'.join(opt_def)
    code = f'''
package at
import "smelly/tools/cli"
type rc_global_options struct {{
{sdef}
}}
var rc_global_opts rc_global_options

func add_rc_global_opts(cmd *cli.Command) {{
{odef}
}}
'''
    with replace_if_needed('tools/cmd/at/global_opts_generated.go') as f:
        f.write(code)


def update_completion() -> None:
    with replace_if_needed('tools/cmd/completion/smelly_generated.go'):
        generate_completions_for_smelly()
    with replace_if_needed('tools/cmd/edit_in_smelly/launch_generated.go'):
        print('package edit_in_smelly')
        print('import "smelly/tools/cli"')
        print('func AddCloneSafeOpts(cmd *cli.Command) {')
        completion_for_launch_wrappers('cmd')
        print(''.join(CompletionSpec.from_string('type:file mime:text/* group:"Text files"').as_go_code('cmd.ArgCompleter', ' = ')))
        print('}')


def define_enum(package_name: str, type_name: str, items: str, underlying_type: str = 'uint') -> str:
    actions = []
    for x in items.splitlines():
        x = x.strip()
        if x:
            actions.append(x)
    ans = [f'package {package_name}', 'import "strconv"', f'type {type_name} {underlying_type}', 'const (']
    stringer = [f'func (ac {type_name}) String() string ''{', 'switch(ac) {']
    for i, ac in enumerate(actions):
        stringer.append(f'case {ac}: return "{ac}"')
        if i == 0:
            ac = ac + f' {type_name} = iota'
        ans.append(ac)
    ans.append(')')
    stringer.append('}\nreturn strconv.Itoa(int(ac)) }')
    return '\n'.join(ans + stringer)


def generate_readline_actions() -> str:
    return define_enum('readline', 'Action', '''\
        ActionNil

        ActionBackspace
        ActionDelete
        ActionMoveToStartOfLine
        ActionMoveToEndOfLine
        ActionMoveToStartOfDocument
        ActionMoveToEndOfDocument
        ActionMoveToEndOfWord
        ActionMoveToStartOfWord
        ActionCursorLeft
        ActionCursorRight
        ActionEndInput
        ActionAcceptInput
        ActionCursorUp
        ActionHistoryPreviousOrCursorUp
        ActionCursorDown
        ActionHistoryNextOrCursorDown
        ActionHistoryNext
        ActionHistoryPrevious
        ActionHistoryFirst
        ActionHistoryLast
        ActionHistoryIncrementalSearchBackwards
        ActionHistoryIncrementalSearchForwards
        ActionTerminateHistorySearchAndApply
        ActionTerminateHistorySearchAndRestore
        ActionClearScreen
        ActionAddText
        ActionAbortCurrentLine

        ActionStartKillActions
        ActionKillToEndOfLine
        ActionKillToStartOfLine
        ActionKillNextWord
        ActionKillPreviousWord
        ActionKillPreviousSpaceDelimitedWord
        ActionEndKillActions
        ActionYank
        ActionPopYank

        ActionNumericArgumentDigit0
        ActionNumericArgumentDigit1
        ActionNumericArgumentDigit2
        ActionNumericArgumentDigit3
        ActionNumericArgumentDigit4
        ActionNumericArgumentDigit5
        ActionNumericArgumentDigit6
        ActionNumericArgumentDigit7
        ActionNumericArgumentDigit8
        ActionNumericArgumentDigit9
        ActionNumericArgumentDigitMinus

        ActionCompleteForward
        ActionCompleteBackward
    ''')


def generate_mimetypes() -> str:
    import mimetypes
    if not mimetypes.inited:
        mimetypes.init()
    ans = ['package utils', 'import "sync"', 'var only_once sync.Once', 'var builtin_types_map map[string]string',
           'func set_builtins() {', 'builtin_types_map = map[string]string{',]
    for k, v in mimetypes.types_map.items():
        ans.append(f'  "{serialize_as_go_string(k)}": "{serialize_as_go_string(v)}",')
    ans.append('}}')
    return '\n'.join(ans)


def generate_textual_mimetypes() -> str:
    ans = ['package utils', 'var KnownTextualMimes = map[string]bool{',]
    for k in text_mimes:
        ans.append(f'  "{serialize_as_go_string(k)}": true,')
    ans.append('}')
    return '\n'.join(ans)


def main() -> None:
    with replace_if_needed('constants_generated.go') as f:
        f.write(generate_constants())
    with replace_if_needed('tools/utils/style/color-names_generated.go') as f:
        f.write(generate_color_names())
    with replace_if_needed('tools/tui/readline/actions_generated.go') as f:
        f.write(generate_readline_actions())
    with replace_if_needed('tools/tui/spinners_generated.go') as f:
        f.write(generate_spinners())
    with replace_if_needed('tools/utils/mimetypes_generated.go') as f:
        f.write(generate_mimetypes())
    with replace_if_needed('tools/utils/mimetypes_textual_generated.go') as f:
        f.write(generate_textual_mimetypes())

    update_completion()
    update_at_commands()
    kitten_clis()
    print(json.dumps(changed, indent=2))


if __name__ == '__main__':
    main()  # }}}
