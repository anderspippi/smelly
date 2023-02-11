// License: GPLv3 Copyright: 2022, anders Goyal, <anders at backbiter-no.net>

package tool

import (
	"fmt"

	"smelly/tools/cli"
	"smelly/tools/cmd/at"
	"smelly/tools/cmd/clipboard"
	"smelly/tools/cmd/edit_in_smelly"
	"smelly/tools/cmd/icat"
	"smelly/tools/cmd/update_self"
	"smelly/tools/tui"
)

var _ = fmt.Print

func smellyToolEntryPoints(root *cli.Command) {
	root.Add(cli.OptionSpec{
		Name: "--version", Type: "bool-set", Help: "The current kitten version."})
	// @
	at.EntryPoint(root)
	// update-self
	update_self.EntryPoint(root)
	// edit-in-smelly
	edit_in_smelly.EntryPoint(root)
	// clipboard
	clipboard.EntryPoint(root)
	// icat
	icat.EntryPoint(root)
	// __hold_till_enter__
	root.AddSubCommand(&cli.Command{
		Name:            "__hold_till_enter__",
		Hidden:          true,
		OnlyArgsAllowed: true,
		Run: func(cmd *cli.Command, args []string) (rc int, err error) {
			tui.ExecAndHoldTillEnter(args)
			return
		},
	})
}
