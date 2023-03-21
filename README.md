# Steno Tools

Steno Tools is a collection of powerful tools for generating and managing stenography dictionaries.

Stenography is a fascinating and efficient way of writing, used by court reporters, live captioners, and speed writers for fast, ergonomic writing. If you're interested in learning more about stenography, check out the [Open Steno Project](https://www.openstenoproject.org/), a community dedicated to making stenography accessible to everyone.

## Table of Contents

- [Requirements](#requirements)
- [Generate a Phonetic Dictionary](#generate-a-phonetic-dictionary)
  - [Usage](#usage)
  - [Default Theory](#default-theory)
  - [Customizing the Default Theory](#customizing-the-generated-theory)
    - [Customizing Phonemes](#customizing-phonemes)
    - [Postprocessing Strokes](#postprocessing-strokes)
- [Combine Dictionaries](#combine-dictionaries)
  - [Usage](#usage-1)
- [License](#license)
- [Contributing](#contributing)

## Installation and Requirements

The code was designed to work with Python3.11. You can download Python from the official [Python webiste](https://www.python.org/downloads/).

To install Steno Tools, run `git clone https://github.com/AndrewHess/steno-tools.git` in your terminal.

## Generate a Phonetic Dictionary

Steno Tools allows you to generate a phonetic steno dictionary by providing a list of words to generate strokes for and specifying how each phoneme maps to steno keys. This can be very useful for generating a base phonetic dictionary that you can then manually add briefs to.

### Usage

1. Download a CSV file that maps words to their pronunciation in IPA. A good choice is to go to https://github.com/open-dict-data/ipa-dict/releases/tag/1.0 and download the `csv.zip` file, unzip it, and extract the file for your language (e.g., `en_US.csv` for American English).
2. Create a file containing the words that you want to include in the generated dictionary. There should be one word per line. A good option is to download the list of most frequently used English words from https://www.kaggle.com/datasets/rtatman/english-word-frequency and then clean it up by removing the comma and number after each word, capitalizing certain words, and anything else you want to do.
3. In a terminal, go into the `generator` directory of this repository.
4. Run `python generate_phonetic_dictionary.py /path/to/en_US.csv /path/to/your_word_list`.

To see usage options, run `python generate_phonetic_dictionary.py -h`. To write the emitted logs to `logs.txt` rather than standard output, append ` 2> logs.txt` to your command.

### Default Theory

By default the mapping from phonemes to steno keys largely follows [Plover Theory](https://www.artofchording.com/introduction/theories-and-dictionaries.html#plover-theory). A few exceptions are that left-side `z` is formed by `SWR-` and right-side `v` is `-FB`. For a more complete mapping of phonemes to keys, open `config.py` and look at `VOWELS_TO_STENO`, `LEFT_CONSONANT_TO_STENO`, and `RIGHT_CONSONANT_TO_STENO`. The phonemes in those variables are specified via the [International Phonetic Alphabet](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet) (IPA); if you're not familiar with IPA you can look at the variables `VOWELS` and `CONSONANTS` to see examples of each phoneme.

Additionally, there's some postprocessing that's done by default. This consists of:
1. For multistroke translations, if the vowel keys for the stroke consist only of `E`, `U`, or `EU` and the stroke is not the first stroke in the sequence, the vowels are removed from the stroke. For example, the generated stroke for `instead` will be `EUPB/ST-D` instead of `EUPB/STED`.
2. Strokes can use the `-F` for a right-side `s` sound, but if the `s` sound is the last sound in the syllable it must be produced with the `-S` key.
3. If the final stroke in a multistroke translation is `ʃən` (the `SHUN` sound in `ration`), that stroke is folded into the previous stroke by adding `-GS` to the previous stroke.
4. If a stroke sequence for one word is already used for a different word, the stroke `W-B` is repeatedly appended to the sequence until the sequence is unique.

### Customizing the Default Theory

You can customize how words are mapped to strokes by modifying `generator/config.py`. You shouldn't need to change any other file for any reason[^1].

#### Customizing Phonemes

The generator requires generated strokes to be in steno order. So in addition to the phonemes your language uses, you may want to add clusters of phonemes (e.g., a cluster for an ending `lp` sound because `-LP` is not in steno order so the generator could not make a stroke for words like `help`).

In `config.py`, the `VOWELS` and `CONSONANTS` variables specify which phonemes are present in the language/dialect you're generating a dictionary for, and the `VOWELS_TO_STENO` and `LEFT_CONSONANT_TO_STENO`/`RIGHT_CONSONANT_TO_STENO` variables specify how to map those sounds to keys on a steno machine.

To properly generate steno strokes, you need to ensure that the `VOWELS` and `CONSONANTS` variables contain all the vowel and consonant sounds for the language/dialect you're generating a dictionary for. The sounds are specified in IPA. Once these variables are set, for each entry in `VOWELS` you must add a corresponding entry to `VOWELS_TO_STENO`. Similarly, for each entry in `CONSONANTS` you must add a corresponding entry to both `LEFT_CONSONANT_TO_STENO` and `RIGHT_CONSONANT_TO_STENO`.

In cases where it's not possible to produce a consonant sound on one side of the vowel, set the corresponding value for that sound on the unused side to `NO_STENO_MAPPING`. If your theory allows multiple ways to make a certain sound (e.g., both `FT` and `*S` for an ending `st` sound), the entry for that side should be a list of all ways to map the sound to keys.

#### Postprocessing Strokes

You may want to modify the generated strokes in a non-phonetic way. For example, to distinguish between homophones. There's two functions in `config.py` where you can add custom postprocessing: `postprocess_steno_sequence()` and `postprocess_generated_dictionary()`.

Add any postprocessing that is independent of other generated strokes to `postprocess_steno_sequence()`. For example, for words whose last syllable is `ʃən` (the `SHUN` sound in `ration`), you may want to fold that ending into the previous stroke by adding `-GS`.

Add any postprocessing that is dependent on other generated strokes to `postprocess_generated_dictionary()`.  For example, you may want to remove conflicts where multiple words were given the same steno sequence. One way to solve this is by iterating through all of the steno sequences for all words and if that sequence is already used by a previous word, keep appending a disambiguation stroke until the sequence is unique.

## Combine Dictionaries

You may want to split your steno dictionaries into different files for better organization, but be able to easily toggle them on and off en masse. The `combine_dictionaries.py` script allows you to combine all the dictionaries in a specified directory into a single dictionary. This can be helpful if you want to split your main dictionary into normal words, proper nouns, written numbers, dates, etc. but you know that whenever you want one of these dictionaries to be active, you want them all to be active.

### Usage
1. In a terminal, run `cd /path/to/your/dictionaries`
2. Run `python /path/to/steno-tools/combine_dictionaries.py <directory>` where `<directory>` is the name of the folder containing the dictionaries you want to combine.

To see usage options, run `python /path/to/steno-tools/combine_dictionaries.py -h`.

## License

This project is under the MIT License. See the `License` file for more info.

## Contributing

Contributions are welcome! Please submit a pull request to contribute to this project. For bugs and feature requests, raise an Issue.

[^1]: If you're generating strokes for a different language, then in addition to `generator/config.py` you may need to update how the IPA listing for a word is split into syllables; this is in `ipa_config.py`. The algorithm for splitting syllables is based on https://linguistics.stackexchange.com/questions/30933/how-to-split-ipa-spelling-into-syllables/30934#30934 and may not work for all languages.
