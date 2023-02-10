// License: GPLv3 Copyright: 2023, Kovid Goyal, <kovid at kovidgoyal.net>

package unicode_input

import (
	"fmt"
	"strings"
	"unicode"

	"kitty/tools/cli"
	"kitty/tools/tui"
	"kitty/tools/tui/loop"
	"kitty/tools/unicode_names"
	"kitty/tools/utils"
	"kitty/tools/utils/style"
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

type Mode int

const (
	HEX Mode = iota
	NAME
	EMOTICONS
	FAVORITES
)

type ModeData struct {
	mode  Mode
	key   string
	title string
}

var all_modes [4]ModeData

type handler struct {
	mode                                     Mode
	recent                                   []rune
	current_char                             rune
	err                                      error
	lp                                       *loop.Loop
	ctx                                      style.Context
	current_tab_formatter, tab_bar_formatter func(...any) string
}

func (self *handler) initialize() {
	self.lp.AllowLineWrapping(false)
	self.lp.SetWindowTitle("Unicode input")
	self.ctx.AllowEscapeCodes = true
	self.current_tab_formatter = self.ctx.SprintFunc("reverse=false bold=true")
	self.tab_bar_formatter = self.ctx.SprintFunc("reverse=true")
	self.draw_screen()
}

func (self *handler) draw_title_bar() {
	entries := make([]string, 0, len(all_modes))
	for _, md := range all_modes {
		entry := fmt.Sprintf(" %s (%s) ", md.title, md.key)
		if md.mode == self.mode {
			entry = self.current_tab_formatter(entry)
		}
		entries = append(entries, entry)
	}
	sz, _ := self.lp.ScreenSize()
	text := fmt.Sprintf("Search by:%s", strings.Join(entries, ""))
	extra := int(sz.WidthCells) - wcswidth.Stringwidth(text)
	if extra > 0 {
		text += strings.Repeat(" ", extra)
	}
	self.lp.QueueWriteString(self.tab_bar_formatter(text))
}

func (self *handler) draw_screen() {
	self.lp.StartAtomicUpdate()
	defer self.lp.EndAtomicUpdate()
	self.lp.ClearScreen()
	self.draw_title_bar()
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

	h := handler{recent: cached_data.Recent, lp: lp}
	switch cached_data.Mode {
	case "HEX":
		h.mode = HEX
	case "NAME":
		h.mode = NAME
	case "EMOTICONS":
		h.mode = EMOTICONS
	case "FAVORITES":
		h.mode = FAVORITES
	}
	all_modes[0] = ModeData{mode: HEX, title: "Code", key: "F1"}
	all_modes[1] = ModeData{mode: NAME, title: "Name", key: "F2"}
	all_modes[2] = ModeData{mode: EMOTICONS, title: "Emoticons", key: "F3"}
	all_modes[3] = ModeData{mode: FAVORITES, title: "Favorites", key: "F4"}

	lp.OnInitialize = func() (string, error) {
		h.initialize()
		return "", nil
	}

	lp.OnResize = func(old_size, new_size loop.ScreenSize) error {
		h.draw_screen()
		return nil
	}

	err = lp.Run()
	if err != nil {
		return
	}
	if h.err == nil {
		switch h.mode {
		case HEX:
			cached_data.Mode = "HEX"
		case NAME:
			cached_data.Mode = "NAME"
		case EMOTICONS:
			cached_data.Mode = "EMOTICONS"
		case FAVORITES:
			cached_data.Mode = "FAVORITES"
		}
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
