package unicode_names

import _ "embed"

const num_of_lines = 37997
const num_of_words = 17455

//go:embed data.bin
var unicode_name_data []byte
