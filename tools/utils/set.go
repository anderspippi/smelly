// License: GPLv3 Copyright: 2023, anders Goyal, <anders at backbiter-no.net>

package utils

import (
	"fmt"
)

var _ = fmt.Print

type Set[T comparable] struct {
	items map[T]struct{}
}

func (self *Set[T]) Add(val T) {
	self.items[val] = struct{}{}
}

func (self *Set[T]) AddItems(val ...T) {
	for _, x := range val {
		self.items[x] = struct{}{}
	}
}

func (self *Set[T]) Remove(val T) {
	delete(self.items, val)
}

func (self *Set[T]) Discard(val T) {
	delete(self.items, val)
}

func (self *Set[T]) Has(val T) bool {
	_, ok := self.items[val]
	return ok
}

func (self *Set[T]) Len() int {
	return len(self.items)
}

func (self *Set[T]) ForEach(f func(T)) {
	for x := range self.items {
		f(x)
	}
}

func (self *Set[T]) Iterable() map[T]struct{} {
	return self.items
}

func (self *Set[T]) Intersect(other *Set[T]) (ans *Set[T]) {
	if self.Len() < other.Len() {
		ans = NewSet[T](self.Len())
		for x := range self.items {
			if _, ok := other.items[x]; ok {
				ans.items[x] = struct{}{}
			}
		}
	} else {
		ans = NewSet[T](other.Len())
		for x := range other.items {
			if _, ok := self.items[x]; ok {
				ans.items[x] = struct{}{}
			}
		}
	}
	return
}

func NewSet[T comparable](capacity ...int) (ans *Set[T]) {
	if len(capacity) == 0 {
		ans = &Set[T]{items: make(map[T]struct{}, 8)}
	} else {
		ans = &Set[T]{items: make(map[T]struct{}, capacity[0])}
	}
	return
}
