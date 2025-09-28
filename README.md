# What2 Grapheme

A pure Python implementation of the Unicode algorithm
for breaking strings of text (i.e., code point
sequences) into extended grapheme clusters
("user-perceived characters") as specified in
[Unicode Standard Annex #29](https://unicode.org/reports/tr29/), "Unicode Text Segmentation".
API functions include type annotations. This package
conforms to version 17.0 of the Unicode standard,
released in August 2025, and has been rigorously
tested against the official Unicode test file to
ensure accuracy. It's also tested by generating
random combinations of strings from the test cases
and comparing output between multiple different
implementations. This has found several bugs in this
implementation as well as in other implementations
which have been reported to the authors and fixed.

Note: Package contains grapheme data files 
as downloaded from [Unicode Data Files](https://www.unicode.org/Public/UCD/latest/ucd/auxiliary/)
and associated license.

Unicode data files are under the associated unicode license.
Use of this package should be in accordance with those terms.

## Why?

```python
>>> from what2_grapheme import api
>>> string = 'u̲n̲d̲e̲r̲l̲i̲n̲e̲d̲'
>>> len(string)
20
>>> api.is_safe(string)
False
>>> api.length(string)
10
>>> string[:3]
'u̲n'
>>> api.strslice(string, 0, 3)
'u̲n̲d̲'
```

## Usage

Functions are available in `what2_grapheme.api`:
```python
>>> from what2_grapheme import api
```

- `is_safe`: Whether a string is safe to handle using builtin `str` operations.
- `iter_grapheme_sizes`: Iterate through grapheme cluster lengths.
- `contains`: Grapheme aware is-substring test.
- `graphemes`: Break a string to a list of graphemes.
- `length`: Grapheme aware length.
- `strslice`: Grapheme aware slicing

## Updating UTF data version

It's possible to load newer versions of grapheme
data with the provided functions by downloading
data files. If rules haven't changed, this will
continue to work without code change. To load newer
data files load data using
`what2_grapheme.grapheme_property.lookup.GraphemeBreak`
then pass an instance of that class to `api` functions as the `properties` argument.

If rules change, code will need changing.

## Implementation

This implementation is pure python. It achieves good
performance by relying on the python `re` module.
This implementation translates each codepoint
in a string into a codepoint representing its
break properties then applies a RegEx consistent
with the one described in [Unicode Standard Annex #29](https://unicode.org/reports/tr29/).
This turns out to give very good performance and
is fairly easy to update based on the regex
definitions in that page, as long as care is
taken to handle codepoints with multiple properties
(eg InCB Extend characters also have the Extend
property).

## Performance

The first usage is slow due to raw data being parsed
and caches being populated, but after that it's
faster than most alternatives. There is a rough
benchmark in the repository comparing different
implementations. One alternate implementation,
[ugrapheme](https://pypi.org/project/ugrapheme/)
consistently gives better performance but requires
cython and (at time of writing) has not been updated
for unicode 17.

To run benchmarks, checkout and install dev
dependencies using `pdm` then run `python -m bm`.
The benchmark is thrown together. However,
it compares a range of different implementations
and use cases.
