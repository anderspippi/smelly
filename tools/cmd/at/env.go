// License: GPLv3 Copyright: 2022, anders Goyal, <anders at backbiter-no.net>

package at

import (
	"smelly/tools/utils"
)

func parse_key_val_args(args []string) map[escaped_string]escaped_string {
	ans := make(map[escaped_string]escaped_string, len(args))
	for _, arg := range args {
		key, value, found := utils.Cut(arg, "=")
		if found {
			ans[escaped_string(key)] = escaped_string(value)
		} else {
			ans[escaped_string(key+"=")] = ""
		}
	}
	return ans
}
