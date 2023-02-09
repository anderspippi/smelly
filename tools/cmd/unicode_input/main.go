// License: GPLv3 Copyright: 2023, Kovid Goyal, <kovid at kovidgoyal.net>

package unicode_input

import (
	"fmt"
	"unicode"

	"kitty/tools/cli"
	"kitty/tools/unicode_names"
	"kitty/tools/utils"
)

var _ = fmt.Print

const default_set_of_symbols string = `
‘’“”‹›«»‚„ 😀😛😇😈😉😍😎😮👍👎 —–§¶†‡©®™ →⇒•·°±−×÷¼½½¾
…µ¢£€¿¡¨´¸ˆ˜ ÀÁÂÃÄÅÆÇÈÉÊË ÌÍÎÏÐÑÒÓÔÕÖØ ŒŠÙÚÛÜÝŸÞßàá âãäåæçèéêëìí
îïðñòóôõöøœš ùúûüýÿþªºαΩ∞
`

var DEFAULT_SET []rune
var EMOTICONS_SET []rune

func build_sets() {
	DEFAULT_SET = make([]rune, 0, len(default_set_of_symbols))
	for _, ch := range default_set_of_symbols {
		if !unicode.IsSpace(ch) {
			DEFAULT_SET = append(DEFAULT_SET, ch)
		}
	}
	EMOTICONS_SET = make([]rune, 0, 0x1f64f-0x1f600+1)
	for i := 0x1f600; i <= 0x1f64f; i++ {
		DEFAULT_SET = append(DEFAULT_SET, rune(i))
	}
}

type CachedData struct {
	Recent []rune `json:"recent,omitempty"`
	Mode   string `json:"mode,omitempty"`
}

var cached_data *CachedData

func main(cmd *cli.Command, o *Options, args []string) (rc int, err error) {
	go unicode_names.Initialize() // start parsing name data in the background
	build_sets()
	cv := utils.NewCachedValues("unicode-input", &CachedData{Recent: DEFAULT_SET, Mode: "HEX"})
	cached_data = cv.Load()
	defer cv.Save()
	return
}

func EntryPoint(parent *cli.Command) {
	create_cmd(parent, main)
}
