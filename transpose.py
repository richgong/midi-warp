#!/Users/gong/c/recbro/play/.venv/bin/python
import sys
import glob
import os
import music21
import ntpath


#converting everything into the key of C major or A minor

# major conversions
majors = dict([("A-", 4),("A", 3),("B-", 2),("B", 1),("C", 0),("C#",-1),("D-", -1),("D", -2),("E-", -3),("E", -4),("F", -5),("G-", 6),("G", 5)])
minors = dict([("A-", 1),("A", 0),("B-", -1),("B", -2),("C", -3),("D-", -4),("D", -5),("E-", 6),("E", 5),("F", 4),("G-", 3),("G", 2)])


def process(full_path):
    print("Input args:", sys.argv[1])
    filename = ntpath.basename(full_path)
    print("Processing:", full_path, '=>', filename)
    score = music21.converter.parse(full_path)
    key = score.analyze('key')
    print("Original key:", key.tonic.name, key.mode)
    if key.mode == "major":
        halfSteps = majors[key.tonic.name]
    elif key.mode == "minor":
        halfSteps = minors[key.tonic.name]

    # newscore = score.transpose(halfSteps)
    # key = newscore.analyze('key')
    # print("Converted to:", key.tonic.name, key.mode)
    # newscore.write('midi', os.path.join(os.path.dirname(full_path), 'C_major_%s' % filename))



process(sys.argv[1])