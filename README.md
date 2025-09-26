# What2 Grapheme

A pure Python implementation of the Unicode algorithm for breaking strings of text (i.e., code point sequences) into extended grapheme clusters ("user-perceived characters") as specified in [Unicode Standard Annex #29](https://unicode.org/reports/tr29/), "Unicode Text Segmentation". API functions include type annotations. This package conforms to version 16.0 of the Unicode standard, released in September 2024, and has been rigorously tested against the official Unicode test file to ensure accuracy.

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

This package includes 3 different implementations of
the grapheme break rules. A simple state machine, 
a fast state machine and a RegEx based
implementation. The last is the one exposed in
`api` as it's the fastest but not easily understood.

## Performance

The first usage is slow due to raw data being parsed
and caches being populated, but after that it's
faster than any alternative I've found (however [ugrapheme](https://github.com/Z4JC/ugrapheme)
might be faster)

To run benchmarks, checkout and install dev
dependencies using `pdm` then run `python -m bm`.
The benchmark is thrown together. This package
includes 3 different implementations of the grapheme
break rules, 2 are included in the benchmark.
