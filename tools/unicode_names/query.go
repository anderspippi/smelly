// License: GPLv3 Copyright: 2023, Kovid Goyal, <kovid at kovidgoyal.net>

package unicode_names

import (
	"bytes"
	"encoding/binary"
	"fmt"
	"strings"
	"sync"
	"time"

	"kitty/tools/utils"
	"kitty/tools/utils/images"
)

type mark_set = *utils.Set[uint16]

var _ = fmt.Print
var names map[uint32]string
var marks []uint32
var word_map map[string][]uint16

func add_word(codepoint uint16, word []byte) {
	w := utils.UnsafeBytesToString(word)
	word_map[w] = append(word_map[w], codepoint)
}

func add_words(codepoint uint16, raw []byte) {
	for len(raw) > 0 {
		idx := bytes.IndexByte(raw, ' ')
		if idx < 0 {
			add_word(codepoint, raw)
			break
		}
		if idx > 0 {
			add_word(codepoint, raw[:idx])
		}
		raw = raw[idx+1:]
	}
}

func parse_record(record []byte, mark uint16) {
	codepoint := binary.LittleEndian.Uint32(record)
	record = record[4:]
	marks[mark] = codepoint
	namelen := binary.LittleEndian.Uint16(record)
	record = record[2:]
	name := utils.UnsafeBytesToString(record[:namelen])
	names[codepoint] = name
	add_words(mark, record[:namelen])
	if len(record) > int(namelen) {
		add_words(mark, record[:namelen])
	}
}

var parse_once sync.Once

func parse_data() {
	names = make(map[uint32]string, num_of_lines)
	word_map = make(map[string][]uint16, num_of_words)
	marks = make([]uint32, num_of_lines)
	raw := unicode_name_data
	var mark uint16
	for len(raw) > 0 {
		record_len := binary.LittleEndian.Uint16(raw)
		raw = raw[2:]
		parse_record(raw[:record_len], mark)
		mark += 1
		raw = raw[record_len:]
	}
}

func Initialize() {
	parse_once.Do(parse_data)
}

func NameForCodePoint(cp uint32) string {
	Initialize()
	return names[cp]
}

func find_matching_codepoints(prefix string) (ans mark_set) {
	for q, marks := range word_map {
		if strings.HasPrefix(q, prefix) {
			if ans == nil {
				ans = utils.NewSet[uint16](len(marks) * 2)
			}
			ans.AddItems(marks...)
		}
	}
	return ans
}

func marks_for_query(query string) (ans mark_set) {
	Initialize()
	prefixes := strings.Split(strings.ToLower(query), " ")
	results := make(chan mark_set, len(prefixes))
	ctx := images.Context{}
	ctx.Parallel(0, len(prefixes), func(nums <-chan int) {
		for i := range nums {
			results <- find_matching_codepoints(prefixes[i])
		}
	})
	close(results)
	for x := range results {
		if ans == nil {
			ans = x
		} else {
			ans = ans.Intersect(x)
		}
	}
	return
}

func CodePointsForQuery(query string) (ans []uint32) {
	x := marks_for_query(query)
	ans = make([]uint32, x.Len())
	i := 0
	for m := range x.Iterable() {
		ans[i] = marks[m]
		i += 1
	}
	return
}

func Develop() {
	start := time.Now()
	Initialize()
	fmt.Println("Parsing unicode name data took:", time.Since(start))
	start = time.Now()
	num := CodePointsForQuery("arr")
	fmt.Println("Querying arr took:", time.Since(start), "and found:", len(num))
	start = time.Now()
	num = CodePointsForQuery("arr right")
	fmt.Println("Querying arr right took:", time.Since(start), "and found:", len(num))
}
