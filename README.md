# Steno Tools

Steno Tools is a collection of powerful tools for generating and managing stenography dictionaries.

Stenography is a fascinating and efficient way of writing, used by court reporters, live captioners, and speed writers for fast, ergonomic writing. If you're interested in learning more about stenography, check out the [Open Steno Project](https://www.openstenoproject.org/), a community dedicated to making stenography accessible to everyone.

## Table of Contents

- [Installation and Requirements](#installation-and-requirements)
- [Generate a Phonetic Dictionary](#generate-a-phonetic-dictionary)
  - [Usage](#usage)
  - [Default Theory](#default-theory)
  - [Customizing the Default Theory](#customizing-the-generated-theory)
    - [Customizing Phonemes](#customizing-phonemes)
    - [Overriding Phoneme Sequence Mappings](#overriding-phoneme-sequence-mappings)
    - [Postprocessing Strokes](#postprocessing-strokes)
- [Combine Dictionaries](#combine-dictionaries)
  - [Usage](#usage-1)
- [Sort Words By Frequency](#sort-words-by-frequency)
  - [Usage](#usage-2)
- [License](#license)
- [Contributing](#contributing)

## Installation and Requirements

The code was designed to work with Python3.11. You can download Python from the official [Python webiste](https://www.python.org/downloads/).

In your terminal, run:
```
git clone https://github.com/AndrewHess/steno-tools.git
cd steno-tools
pip install -r requirements.txt
```

## Generate a Phonetic Dictionary

Steno Tools allows you to generate a phonetic steno dictionary by providing a list of words to generate strokes for and specifying how each phoneme maps to steno keys. This can be very useful for generating a base phonetic dictionary that you can then manually add briefs to.

### Usage

1. Download a CSV file that maps words to their pronunciation in IPA. A good choice is to go to https://github.com/open-dict-data/ipa-dict/releases/tag/1.0 and download the `csv.zip` file, unzip it, and extract the file for your language (e.g., `en_US.csv` for American English).
2. Create a file containing the words that you want to include in the generated dictionary. There should be one word per line. A good option is to download the list of most frequently used English words from https://www.kaggle.com/datasets/rtatman/english-word-frequency and then clean it up by removing the comma and number after each word, capitalizing certain words, and anything else you want to do.
3. In a terminal, go into the `generator` directory of this repository.
4. In a terminal, run
```
python generate_phonetic_dictionary.py /path/to/en_US.csv /path/to/your_word_list --config_file generator/configs/config.yaml
```
5. View the generated dictionary in `output.json`.

To write the emitted logs to `logs.txt` rather than to the console, append ` 2> logs.txt` to your command.

For more usage information, run `python generate_phonetic_dictionary.py -h`.

### Default Theory

By default the mapping from phonemes to steno keys largely follows [Plover Theory](https://www.artofchording.com/introduction/theories-and-dictionaries.html#plover-theory). A few exceptions are that left-side `z` is formed by `SWR-` and right-side `v` is `-FB`. For a more complete mapping of phonemes to keys, open `generator/configs/config.yaml` and look at the `vowels` and `consonants` sections. The phonemes in those sections are specified via the [International Phonetic Alphabet](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet) (IPA). If you're not familiar with IPA you can look at the examples for each phoneme in `config.yaml`.

After strokes are generated phonetically, there some postprocessing that's done by default before writting the final dictionary. You can disable this postprocessing or specify your own rules in the `postprocessing` section. The default postprocessing consists of:
1. Strokes can use the `-F` for a right-side `s` sound, but if the `s` sound is the last sound in the syllable it must be produced with the `-S` key.
2. For multistroke translations, if the vowel keys for the stroke consist only of `E`, `U`, or `EU` and the stroke is not the first stroke in the sequence, the vowels are removed from the stroke. For example, the generated stroke for `instead` will be `EUPB/ST-D` instead of `EUPB/STED`.
3. If the final stroke in a multistroke translation is `SHUPB` (the `SHUN` sound in `ration`), that stroke is folded into the previous stroke by adding `-GS` to the previous stroke.
4. If a non-final stroke in a stroke sequence consists entirely of `TK-` plus `AOE`, `E`, `EU`, or `U`, the vowels are removed and the stroke becomes `TK-`. This is because those types of strokes can often be pronounced several of those ways (e.g., the first syllable of the word `develop`) and removing the vowels doesn't seem to add many conflicts.
5. If a stroke sequence for one word is already used for a different word, the stroke `W-B` is repeatedly appended to the sequence until the sequence is unique.

### Customizing the Default Theory

The file `generator/configs/config.yaml` specifies how strokes are generated for words. You can update this file to customize the generated theory in almost any way.

If you want to make a customization that's not covered in the following subsections, you'll have to make changes to the Python files. In that case, please consider making a pull request with the changes, or ask for the feature by raising a GitHub Issue so that more people can benefit from the desired feature.

#### Customizing Phonemes

The generator ensures generated strokes are in steno order. So in addition to the phonemes your language uses, you may want to add clusters of phonemes (e.g., a cluster for an ending `lp` sound because `-LP` is not in steno order so the generator could not make a stroke for words like `help`).

In `config.yaml`, the `vowels` and `consonants` sections specify how phonemes are mapped to keys on a steno machine. The phoneme is specified with its IPA symbol(s) and the keys are specified as a list of ways to write that phoneme. Note that if the keys do not include a vowel or the asterisk key, you need to include a dash to show which side the consonant keys are one.

In cases where it's not possible to produce a consonant sound on one side of the vowel, set the corresponding value for that sound on the unused side to `NO_STENO_MAPPING`.

If you change the list of phonemes in `consonants`, you'll need to update the `phonology` section as well, which specifies which consonant sounds coming before the vowel can follow each other. For context, the algorithm[^1] used to split a word into syllables is:
1. Find all vowels; these make the nucleaus of each syllable.
2. For each nucleus, form the syllable's onset by prepended as many of the leading consonants as possible while following the specified phonology rules.
3. If there are any additional consonants before the vowel that could not be prepended to the onset, append those consonants to the previous syllable, forming the previous syllable's coda.

So your updates in the `phonology` specify how step 2 is done.

#### Overriding Phoneme Sequence Mappings

By default, the stroke for a syllable is constructed by mapping each phoneme to a set of keys and appending those keys to the stroke while ensuring that the stroke remains in steno order. However, in some cases you may want to override this behavior so that certain phoneme sequences are mapped all at once to a custom set of steno keys. This is done in the `phoneme_sequence_overrides` section of the YAML config file by adding a list of overrides. For example, if you want to map the right-side phoneme sequence `mp` to `*PL`, you would add the following to your config file.
```
phoneme_sequence_overrides:
  - sequence:
    - ["m", RIGHT_CONSONANT]
    - ["p", RIGHT_CONSONANT]
    keys: ["*PL"]
```
For each phoneme in the sequence, you must specify it as a `LEFT_CONSONANT`, `VOWEL`, or `RIGHT_CONSONANT`.

Notably, these overrides only apply after words are split into syllables. This means that a word like `compost` will continue to be split into the syllables `com` and `post` (so this override will not apply to that word becuase the `m` and `p` are on different syllables), but the override will apply to the word `lamp`.

#### Postprocessing Strokes

For certain strokes, you may want to modify them before exporting them to the final dictionary. You can specify these rules in the `postprocessing` section of `config.yaml`. Additional information about setting up each of the rules mentioned below is available in the comments of the provided `config.yaml`.

Many of the postprocessing steps have a `keep_original_sequence` key. When this is `True`, the original stroke is kept, and if postprocessing would change it, the changed versions are added to the dictionary. When `keep_original_sequence` is `False`, strokes that would not be changed by postprocessing are kept, but strokes that would get changed are replaced by the updated version.

##### Disallow -F as Final S
You may want to allow right-side `s` to be formed with the `-F` key if and only if there are other right-side keys in the stroke. If your `vowels` and `consonants` section is setup to allow `-F` as `s`, you can omit strokes that incorrectly use `-F` as the final `s` by enabling `disallow_f_for_final_s_sound`.

##### Folding Strokes

You may want to fold certain prefix and suffix strokes into the next/previous stroke. You can specify these rules in the `fold_strokes` section.

##### Dropping Vowels

You may find it useful to drop the vowels from certain strokes. You can specify when this should occur in the `drop_vowels` section.

For each `drop_vowels` rule, you can specify what the left and right consonants should be for this rule to apply (or that they can be anything, or anything with at least one key), and you can specify which vowel clusters to drop. A vowel cluster is only dropped if it exactly matches the set of vowels in the stroke.

##### Conflict Resolution

You can enabled the `append_disambiguator_stroke` setting so that when two different words map to the same sequence of strokes, one of the sequences gets appended with a certain stroke until the resulting sequence has no conflicts. The `disambiguator_stroke` field specifies which stroke is appended. The sequence that gets appended to is the one that appears later in the file containing a list of words to generate strokes for; so if that list is sorted so more frequent words are at the top, then the sequence for the less frequent word will get appended to.

## Combine Dictionaries

You may want to split your steno dictionaries into different files for better organization, but be able to easily toggle them on and off en masse. The `combine_dictionaries.py` script allows you to combine all the dictionaries in a specified directory into a single dictionary. This can be helpful if you want to split your main dictionary into normal words, proper nouns, written numbers, dates, etc. but you know that whenever you want one of these dictionaries to be active, you want them all to be active.

### Usage

1. In a terminal, run `cd /path/to/your/dictionaries`
2. Run `python /path/to/steno-tools/combine_dictionaries.py <directory>` where `<directory>` is the name of the folder containing the dictionaries you want to combine.

By default, only JSON files directly in the specified directory will be merged, but you can recursively search all directories with the `--recursive` flag. If multiple files have an entry for the same stroke sequence, the first entry will have priority and later entries will be ignored. Files are searched alphabetically but filename portions with numbers are sorted by the numbers; so if you have three files `priority-1-prefixes.json`, `priority-5-names.json`, and `priority-20-other.json`, they will be searched in that order, NOT as `priority-1-prefixes.json`, `priority-20-other.json`, `priority-5-names.json`. Use the flag `-v` or `-vv` to get more information on which files are searched when for your specific directory structure.

For more usage information, run `python /path/to/steno-tools/combine_dictionaries.py -h`.

## Sort Words By Frequency

You may want to sort a list of words by freqency so you can add more frequent words to your dictionary first or to compile a list of practice words. To do this, use the `sort_by_frequency.py` script. Provide a file containing the list of words to sort and another file listing the words by their frequency. For example, you can use the English word frequency list available at https://www.kaggle.com/datasets/rtatman/english-word-frequency.


### Usage

To sort a list of words by their order in a different file, run the following.

```
python /path/to/steno-tools/sort_by_frequency.py  --word-list /your/words_to_sort.txt --frequency-file /many/words_by_frequency.txt --output-file output.txt
```

Both input files should have exactly one word per line and nothing else.

Words in the word list file that are not in the frequency list file are printed to the console. If you just want to see which words in the word list file are not in the frequency file, without writing the resulting sorted list to a file, use the `--no-output` flag instead of `--output-file`.

For more usage information, run `python /path/to/steno-tools/sort_by_frequency.py -h`

## License

This project is under the MIT License. See the `License` file for more info.

## Contributing

Contributions are welcome! Please submit a pull request to contribute to this project. For bugs and feature requests, raise an Issue.

[^1]: The algorithm for splitting syllables is based on https://linguistics.stackexchange.com/questions/30933/how-to-split-ipa-spelling-into-syllables/30934#30934 and may not work for all languages. If you're generating strokes for a different language, then you may need to update how the IPA listing for a word is split into syllables; this is in `ipa_config.py`.
