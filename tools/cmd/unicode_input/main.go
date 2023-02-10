// License: GPLv3 Copyright: 2023, Kovid Goyal, <kovid at kovidgoyal.net>

package unicode_input

import (
	"fmt"
	"unicode"

	"kitty/tools/cli"
	"kitty/tools/tui"
	"kitty/tools/tui/loop"
	"kitty/tools/unicode_names"
	"kitty/tools/utils"
	"kitty/tools/wcswidth"

	"golang.org/x/exp/slices"
)

var _ = fmt.Print

const default_set_of_symbols string = `
‘’“”‹›«»‚„ 😀😛😇😈😉😍😎😮👍👎 —–§¶†‡©®™ →⇒•·°±−×÷¼½½¾
…µ¢£€¿¡¨´¸ˆ˜ ÀÁÂÃÄÅÆÇÈÉÊË ÌÍÎÏÐÑÒÓÔÕÖØ ŒŠÙÚÛÜÝŸÞßàá âãäåæçèéêëìí
îïðñòóôõöøœš ùúûüýÿþªºαΩ∞
`

var DEFAULT_SET []rune
var EMOTICONS_SET []rune

const DEFAULT_MODE string = "HEX"

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

type handler struct {
	mode         string
	recent       []rune
	current_char rune
	err          error
}

func run_loop(opts *Options) (lp *loop.Loop, err error) {
	output := tui.KittenOutputSerializer()
	lp, err = loop.New()
	if err != nil {
		return
	}
	cv := utils.NewCachedValues("unicode-input", &CachedData{Recent: DEFAULT_SET, Mode: DEFAULT_MODE})
	cached_data = cv.Load()
	defer cv.Save()

	h := handler{mode: cached_data.Mode, recent: cached_data.Recent}

	lp.OnInitialize = func() (string, error) {
		lp.AllowLineWrapping(false)
		lp.SetWindowTitle("Unicode input")
		return "", nil
	}

	err = lp.Run()
	if err != nil {
		return
	}
	if h.err == nil {
		cached_data.Mode = h.mode
		if h.current_char != 0 {
			cached_data.Recent = h.recent
			idx := slices.Index(cached_data.Recent, h.current_char)
			if idx > -1 {
				cached_data.Recent = slices.Delete(cached_data.Recent, idx, idx+1)
			}
			cached_data.Recent = slices.Insert(cached_data.Recent, 0, h.current_char)[:len(DEFAULT_SET)]
			ans := string(h.current_char)
			if wcswidth.IsEmojiPresentationBase(h.current_char) {
				switch opts.EmojiVariation {
				case "text":
					ans += "\ufe0e"
				case "graphic":
					ans += "\ufe0f"
				}
			}
			o, err := output(ans)
			if err != nil {
				return lp, err
			}
			fmt.Println(o)
		}
	}
	err = h.err
	return
}

func main(cmd *cli.Command, o *Options, args []string) (rc int, err error) {
	go unicode_names.Initialize() // start parsing name data in the background
	build_sets()
	lp, err := run_loop(o)
	if err != nil {
		return 1, err
	}
	ds := lp.DeathSignalName()
	if ds != "" {
		fmt.Println("Killed by signal: ", ds)
		lp.KillIfSignalled()
		return 1, nil
	}
	return
}

func EntryPoint(parent *cli.Command) {
	create_cmd(parent, main)
}
