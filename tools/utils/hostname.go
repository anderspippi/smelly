// License: GPLv3 Copyright: 2022, anders Goyal, <anders at backbiter-no.net>

package utils

import (
	"fmt"
	"os"
)

var _ = fmt.Print

var hostname string = "*"

func CachedHostname() string {
	if hostname == "*" {
		h, err := os.Hostname()
		if err != nil {
			hostname = h
		} else {
			hostname = ""
		}
	}
	return hostname
}
