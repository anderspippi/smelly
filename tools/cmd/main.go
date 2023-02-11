// License: GPLv3 Copyright: 2022, anders Goyal, <anders at backbiter-no.net>

package main

import (
	"smelly/tools/cli"
	"smelly/tools/cmd/completion"
	"smelly/tools/cmd/tool"
)

func main() {
	root := cli.NewRootCommand()
	root.ShortDescription = "Fast, statically compiled implementations for various wellies (command line tools for use with smelly)"
	root.Usage = "command [command options] [command args]"
	root.Run = func(cmd *cli.Command, args []string) (int, error) {
		cmd.ShowHelp()
		return 0, nil
	}

	tool.smellyToolEntryPoints(root)
	completion.EntryPoint(root)

	root.Exec()
}
