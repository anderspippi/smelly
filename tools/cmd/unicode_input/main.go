// License: GPLv3 Copyright: 2023, Kovid Goyal, <kovid at kovidgoyal.net>

package unicode_input

import (
	"fmt"

	"kitty/tools/cli"
	"kitty/tools/unicode_names"
)

var _ = fmt.Print

func main(cmd *cli.Command, o *Options, args []string) (rc int, err error) {
	go unicode_names.Initialize() // start parsing name data in the background
	return
}

func EntryPoint(parent *cli.Command) {
	create_cmd(parent, main)
}
