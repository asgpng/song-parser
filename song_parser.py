# -*- coding: utf-8 -*-

import re, sys, time, os

class UnfinishedParse(Exception):
    pass

class InvalidMeta(Exception):
    pass

def transpose_atomic_chord(chord, steps):
    """Transpose a given atomic chord a given number of steps.
    Returns : transposed chord
    """
    # eventually make into class
    chords = ['A', 'Bb', 'B', 'C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'G#']
    alternates = {'A#':'Bb', 'Db':'C#', 'D#':'Eb','Gb':'F#', 'Ab':'G#'}
    try:
        index = chords.index(chord)
    except ValueError:
        try:
            index = chords.index(alternates[chord])
        except ValueError:
            # return "Input must be valid note."
            return ""
    if index + steps >= 12:
        return chords[index+steps-12]
    elif index + steps < 0:
        return chords[index+steps+12]
    else:
        return chords[index+steps]

def transpose_chord(chord, steps):
    """Transpose a given chord a given number of steps.
    Returns : transposed chord
    """

    # split into possible sub-chords
    chords = re.split('[\/acdefghijklmnopqrstuvwxyz0-9]', chord)

    output = []
    i = 0
    non_chord = ''
    final_chord = ''
    for c in chords:
        final_chord = c
        if is_a_chord(c):
            output.append(chord[i:chord.find(c)])
            output.append(transpose_atomic_chord(c, steps))
            # i += len(c)
            i = chord.find(c) + len(c)
        else:
            # output.append(chord[i]) # append other chord markings
            # i += 1
            pass
    output.append(chord[i:])

    return ''.join(output)

def transpose_line(line, steps):
    """Transpose a given line a given number of steps.
    It's unfortunately a bit complicated because it attempts to keep
    Relative positions of chords the same
    Returns : transposed line
    """
    # create output list
    output = []

    if not is_chord(line):
        output.append(line)
    else:
        # remove tabs
        line = un_tabify(line)

        # split line into list of chords
        chord_list = chord_split(line)

        # create indices
        current_space_index = 0
        chord_count = 0

        while chord_count < len(chord_list):
            # obtain current chord
            chord = chord_list[chord_count]
            # original index of pre-transposed chord
            orig_chord_index = line.find(chord, current_space_index)

            # length of original chord
            orig_length = len(chord)
            new_chord = transpose_chord(chord, steps)
            # length of new chord
            new_length = len(new_chord)

            # find next chord index, if it exists
            try:
                next_chord_index = line.find(chord_list[chord_count+1],
                                             orig_chord_index + orig_length)
            except IndexError:
                next_chord_index = orig_chord_index + orig_length

            # calculate number of spaces to add
            num_spaces = next_chord_index - orig_chord_index - \
                         (len(new_chord) - len(chord)) - len(chord)

            # add extra spaces at beginning
            if chord_count == 0:
                for i in range(orig_chord_index):
                    output.append(' ')

            # add the transposed chord
            output.append(transpose_chord(chord, steps))

            # insert the correct number of spaces for the next
            # chord to be in the right place
            for i in range(num_spaces):
                output.append(' ')

            # always append at least one space.
            if num_spaces <= 0:
                output.append(' ')

            chord_count += 1
            current_space_index = orig_chord_index + orig_length

        output.append('\n')

    return ''.join(output)

def transpose_lines(lines, steps):
    """Transpose a given set of lines (i.e. an entire song) a given number of steps
    Returns : transposed lines
    """
    output = []
    for line in lines:
        if is_chord(line):
            output.append(transpose_line(line, steps))
        else:
            output.append(line)

    return output

def is_date(item):
    if re.search('^[1|2]\d{3}$', item) != None:
        return True
    return False

def chord_test():
    print is_chord('A A E/G# F#m B Esus E\n')

def is_a_chord(test):
    """Check if a test string is a chord
    Returns : boolean
    """
    chords = ['A', 'Bb', 'B', 'C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'G#']
    misc = ['min', 'dim', 'sus', 'maj', 'm', 'b']

    # # regex method was tempting, but doesn't work:
    # notes = "[ABCDEFG]"
    # accidentals = "(?:#|##|b|bb)?"
    # chords = "(?:maj|min|m|sus|aug|dim)?"
    # additions = "[0-9]?"
    # chordFormPattern = notes + accidentals + chords + additions
    # fullPattern = chordFormPattern + "(?:/%s)?\s" % (notes + accidentals)
    # regex = re.compile(r"""[CDEFGAB](?=(?:#|##|b|bb)?(?:maj|min|m|sus|aug|dim)?[0-9]?)""")

    # check if leading character is an allowed letter
    try:
        if test[0] not in "ABCDEFG":
            return False
        else:
            # if length is 1, it must be a chord
            if len(test) == 1:
                return True
            else:
                if test[1] not in "msadb#0123456789/":
                    return False
                else:
                    if len(test) == 2:
                        return True
                    else:
                        if test[2] not in "ABCDEFG#baimsud0123456789/":
                            return False
                        else:
                            if len(test) == 3:
                                return True
                            else:
                                if regex.match(test):
                                    return True
                                else:
                                    return False

    except IndexError:
        return False

def is_chord(line):
    """Check if line contains chords.
    Returns : boolean
    """

    if is_blank(line):
        return False

    # test = removeSpacesFromList(re.split('[^a-zA-Z0-9#\/]', line))
    test = removeSpacesFromList(chord_split(line))
    i = 0

    # consider using more REGEXes in the future
    # while i < len(test):
    for chord in test:
        if not is_a_chord(chord):
            return False

    return True

        # # chord = test[i]

def is_blank(line):
    """Check if line is blank
    Returns : boolean
    """
    test = split(line)
    for elem in test:
        if elem != '':
            return False
    return True

def is_lyric(line):
    """Check if line contains lyrics.
    Currently not used, could be further implemented, i.e. comes after chords
    Returns : boolean
    """
    test = split(line)
    return True

def is_xml_line(line):
    """Check if line is a complete xml line i.e. <foo>bar</foo>
    Returns : boolean
    """
    # print line
    if '<' in line and '>' in line and '/' in line:
        return True
    return False

def is_xml(line):
    """Check if line contains xml
    Returns : boolean
    """
    if '<' in line and '>' in line:
        return True
    return False

def get_xml_type(line):
    """Get the xml type of an xml line by returning the first element which is
    not empty and which appears at least twice.
    Returns : xml type (string)
    """
    elems = split(line)
    for elem in elems:
        if elem != '' and elems.count(elem) >= 2:
            return elem

def get_xml_value(line):
    """Get the xml value of an xml line by returning everything that is not xml
    Returns : xml value (string)
    """
    elems = split(line)
    value = ''
    xml_tag_found = False
    i = 0
    tag = get_xml_type(line)
    for elem in elems:
        if elem != '' and elem != tag:
            value += elem + ' '
    return value

def get_heading(line):
    """Parse line to find heading, if it exists
    Returns : heading (string), or None
    """
    head = re.split('[\d\W]', line.lower())
    # print head, "head"
    # head = split(line.lower())
    # parse [verse] number, if existing:
    number = ""
    numbers = re.split('\D', line)
    for n in numbers:
        if n != "":
            number = n
        if 'order' in head:
            return 'order'
        if 'intro' in head:
            return 'intro'
        if 'verse' in head:
            return 'verse' # + str(number)
        if 'pre chorus' in line.lower():
            return 'pre chorus' # + str(number)
        if 'chorus' in head:
            return 'chorus'
        if 'bridge' in head:
            return 'bridge'
        if 'tag' in head:
            return 'tag'
        if 'refrain' in head:
            return 'refrain'
        if 'ending' in head:
            return 'ending'
        if 'outro' in head:
            return 'outro'
        if 'end' in head:
            return 'end'

        # if none of these, try single letters
        if 'v' in head:
            return 'verse' # + str(number)
        # if 'c' in head:
        #     return 'chorus'
        # if 'b' in head:
        #     return 'bridge'
        # if 'r' in head:
        #     return 'refrain'
    return None

def capitalize_first(word):
    """Capitalize first letter of word
    Returns : capitalized word
    """
    return word[0].upper() + word[1:]

def split(line):
    """Use regex to split into list of data (chords, lyrics, etc.)
    Returns : list
    """
    return re.split('\W+', line)

def split_chars(line):
    """Split line into list of characters
    Returns : list
    """
    chars = []
    for char in line:
        chars.append(char)
    return chars

# return list of lines
def read_file(file_name):
    """Read in file and produce list of lines
    Returns : list of lines
    """
    fin = open(file_name, 'r')
    lines = []
    for line in fin:
        lines.append(sanitize(un_tabify(line)))
        # print line
    return lines

def process_upload(lines):
    title = lines[0]
    try:
        meta = parse_credits(lines[1])
    except UnboundLocalError:
        return 'Unable to parse credits line.'
    print title
    print meta['author']
    print meta['producer']
    print meta['date']
    print meta['ccli']

def get_title(lines):
    return lines[0]

def get_author(lines):
    try:
        return parse_credits(lines[1])['author']
    except (KeyError, TypeError):
        return ''

def get_producer(lines):
    try:
        return parse_credits(lines[1])['producer']
    except (KeyError, TypeError):
        return ''

def get_date(lines):
    try:
        return parse_credits(lines[1])['date']
    except (KeyError, TypeError):
        return ''

def get_ccli(lines):
    try:
        return parse_credits(lines[1])['ccli']
    except (KeyError, TypeError):
        return ''

def get_text(lines):
    return '\n'.join(lines[2:])

def get_html(lines):
    return html_export(lines)

credits = "Vicky Beeching © 2001 UK/Eire CCLI # 3447521"
def parse_credits(credits):
    """Parse credits (usually second line of a song)
    to identify relevant information.
    Returns : list of keys and values
    """
    line = re.split("[\s\#\©]", credits)
    try:
        for item_index, item in enumerate(line):
            # this could also match some ccli numbers
            if is_date(item):
                date = item
                author = ' '.join(line[:line.index(item)])
            if item.lower() == 'ccli':
                if line[item_index+1] == '':
                    ccli = line[item_index+2]
                else:
                    ccli = line[item_index+1]
                producer = ' '.join(line[line.index(date)+1:line.index(item)])
                # print author, producer, date, ccli
        return {'author':author, 'producer':producer, 'date':date, 'ccli':ccli}
    except UnboundLocalError:
        # most likely CCLI # is missing
        try:
            for item_index, item in enumerate(line):
                # this could also match some ccli numbers
                if is_date(item):
                    date = item
                    author = ' '.join(line[:line.index(item)])
                    producer = ' '.join(line[line.index(date)+1:])
                    return {'author':author, 'producer':producer, 'date':date}
                    # just return everything as author, can be fixed manually
        except UnboundLocalError:
            return {'author': ' '.join(line).strip()}
            #     raise InvalidMeta


def classify_song(lines):
    """Debugging tool parses song and classifies each line
    Returns : list of lines and their type
    """
    out_lines = []
    i = 2
    # assuming title and credits on all songs
    out_lines.append(['title', lines[0]])
    out_lines.append(['credits', lines[1]])
    while i < len(lines):
        line = lines[i]
        if is_xml_line(line):
            out_lines.append([get_xml_type(line), get_xml_value(line)])
        if is_xml(line):
            pass
        elif is_blank(line):
            line_type = 'blank'
        elif get_heading(line) != None:
            line_type = get_heading(line)
        elif is_chord(line):
            line_type = 'chords'
        else: # default
            line_type = 'lyrics'
        out_lines.append([line_type, line])
        i += 1
    return out_lines

def html_head(css_file = '../style.css'):
    """Print html head
    Returns : html
    """
    return """
<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" type="text/css" href="%s">
</head>
<body>\n""" % css_file

def html_foot():
    """Print html foot
    Returns : html
    """
    return """
</body>
</html>"""

def removeNonAscii(s): return "".join(i for i in s if ord(i)<128)

def removeSpacesFromList(_list):
    tmpList = []
    for i in _list:
        if i != "":
            tmpList.append(i)
    return tmpList

def nbsp(text, chord_distance=None):
    if chord_distance <= 2 and chord_distance != None:
        return re.sub('\s', '&nbsp;&nbsp;', text)
    else:
        return re.sub('\s', '&nbsp;', text)


def sanitize(line):
    """Replace problematic characters with suitable substitutes.
    In some cases, temporary characters are used to prevent inaccurate spacing
    for lyrics and chords.
    Returns : string
    """
    line = re.sub('\xef\xbb\xbf', "", line)
    line = re.sub('0xfb', "", line)
    line = re.sub('\’', "'", line)
    line = re.sub('©', '&copy;', line)
    line = re.sub('\’', chr(251), line)
    line = re.sub('\‘', chr(252), line)
    line = re.sub('“', '"', line)
    line = re.sub('”', '"', line)
    line = re.sub('…', '...', line)
    # line = removeNonAscii(line)
    # line = re.sub('Â', "", line)
    return  line

def sanitize_decode(line):
    """Decode previous temporary characters
    Returns : string
    """
    line = re.sub(chr(251), '&apos;', line)
    line = re.sub(chr(252), '&apos;', line)
    return line

def un_tabify(chords):
    """Replace tabs with spaces
    Returns : string
    """
    return re.sub('\t', '   ', chords)

def chord_split(chords):
    list = re.split('[\s]', chords)
    chord_list = []
    for i in list:
        if i != '':
            chord_list.append(i)
    return chord_list

def chord_lyric_split(chords, lyrics, context='chords'):
    """Take line of chords and line of lyrics and combine them into
    span intput for html display.
    Returns : html with <span> tags
    """
    i = 0
    j = 0
    k = 0
    l = 0
    chords = un_tabify(chords)
    chord_list = chord_split(chords) # array of chords
    output = ""
    while k < len(chord_list):
        chord = chord_list[k]
        i = chords.find(chord, l) # index of chord location

        try:
            next_chord_index = chords.find(chord_list[k+1], l)
        except IndexError: # error on final chord
            next_chord_index = i

        chord_distance_ratio = 1.0 * (next_chord_index - i) / len(chord)

        if i >= len(lyrics): # add extra chord(s)
            output += nbsp(lyrics[j:], chord_distance_ratio)
            output += '  '
            output += '<span ' + context + '="'
            output += chord + '">'
            output += '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>'
        else:
            if i-1 >= 0:
                output += nbsp(lyrics[j:i], chord_distance_ratio)   # will this work for leading chords?
                output += '<span ' + context + '="'
                output += chord + '">'
                output += nbsp(lyrics[i], chord_distance_ratio)
                output += '</span>'
            else: # leading chord
                output += '<span ' + context + '="'
                output += chord + '">'
                output += ''
                output += '</span>'
                output += nbsp(lyrics[i], chord_distance_ratio)
        j = i+1 #len(chord)
        l = i + len(chord)
        k += 1
    if len(lyrics) > i:
        output += lyrics[i+1:]
    output += '\n<br>\n'
    return output

def chord_lyric_table(html_chords, html_lyrics):
    """Deprecated method builds html table for chords and lyrics
    Returns : html table
    """
    output = "<table>\n"
    output += line_to_html_row(html_chords, "chords")
    output += line_to_html_row(html_lyrics, "lyrics")
    output +="</table>\n"
    return output

def line_to_html_row(line, line_type):
    """Deprecated method builds html row
    Returns : html row
    """
    output = "<tr>\n"
    for elem in line:
        output += '<td class="'+line_type+'">'+elem+"&nbsp;</td>\n"
        output += "</tr>\n"
    return output

def html_export(lines):
    """
    Return output text (string)
    """
    headings = ['order', 'intro', 'verse', 'pre chorus', 'chorus', 'bridge', 'tag', 'refrain', 'ending', 'outro', 'end']
    # parse file
    out_lines = classify_song(lines)

    # split into metadata and sheet music
    metadata = []
    sheet_music = []
    for line in out_lines:
        if line[0] not in ['chords', 'lyrics', 'blank', 'heading'] and line[0] not in headings:
            metadata.append(line)
        else:
            sheet_music.append(line)
    out_text = ''
    out_text += html_head('/~asg4/songs/static/css/songs.css')

    # append beginning of metadata
    for data in metadata:
        if data[0] == 'title':
            out_text += '<div class="title">' + data[1] + '</div>\n'
    for data in metadata:
        if data[0] == 'credits':
            out_text += '<div class="credits">' + sanitize(data[1]) + '</div>\n'
            out_text += '<br>'
    for data in metadata:
        if data[0] == 'author':
            out_text += data[1] + ' '
    for data in metadata:
        if data[0] == 'copyright':
            out_text += '&copy; ' + data[1] + ', '
    for data in metadata:
        if data[0] == 'ccli':
            out_text += 'CCLI # ' + data[1] #still need ccli #

    # append sheet music
    i = 0
    context = ''
    found_header = False
    last_line = ''
    while i < len(sheet_music):
        # try:
        line = sheet_music[i]
        if found_header:
            # print line
            if line[0] in headings:
                out_text += '<div class="heading">'
                out_text += capitalize_first(line[1]) + ' '
                out_text += '</div>'
                # context = split(line[0])[0]
                i += 1
                # out_text += '<br>'
                last_line = 'heading'
            elif line[0] == 'chords':
                try:
                    lyrics = sheet_music[i+1]
                    out_text += chord_lyric_split(line[1], lyrics[1], 'chords')
                    i += 2
                    # out_text += '<br>'
                    last_line = 'chords'
                except IndexError:
                    continue
            elif line[0] == 'blank':
                i += 1
                last_line = 'blank'


                # check if next line is has chords: if so, add an extra break
                try:
                    next_line = sheet_music[i+1]
                    if next_line[0] == 'chords':
                        out_text += '<br>'
                except IndexError:
                    continue

                # if last_line != 'blank':
                # out_text += '<br>'
            elif line[0] == 'lyrics':
                out_text += line[1]
                # check if next line has chords: if so, add an extra break
                try:
                    next_line = sheet_music[i+1]
                    if next_line[0] == 'chords':
                        out_text += '<br><br>'
                except IndexError:
                    continue
                i += 1
                last_line = 'lyrics'
            else:
                print line
                raise UnfinishedParse
        else:
            if line[0] in headings:
                out_text += '<div class="heading">'
                out_text += capitalize_first(line[1]) + ' '
                out_text += '</div>'
                # context = split(line[0])[0]
                i += 1
                # out_text += '<br>\n'
                found_header = True
                last_line = 'header'
            else:
                if line[0] == 'chords':
                    try:
                        lyrics = sheet_music[i+1]
                        out_text += chord_lyric_split(line[1], lyrics[1], 'chords')
                        i += 2
                        # out_text += '<br>\n'
                        last_line = 'chords'
                    except IndexError:
                        print line[0]
                elif line[0] == 'blank':
                    # if last_line != 'blank':
                    # check if next line has is a heading: if so, DON'T add an extra break
                    try:
                        next_line = sheet_music[i+1]
                        if next_line[0] in headings:
                            pass
                        else:
                            out_text += '<br>'
                    except IndexError:
                        continue
                    i += 1
                    last_line = 'blank'
                elif line[0] == 'lyrics':
                    out_text += line[1]
                    i += 1
                    last_line = 'lyrics'
                else:
                    print line
                    raise UnfinishedParse

        out_text += '<br>'
    out_text += html_foot()
    out_text = re.sub('<br><br>', '<br>', out_text)
    return sanitize_decode(out_text)

def parse_credit_test():
    TEXT_DIR = 'txt'
    songs = os.listdir(TEXT_DIR)
    for i in songs:
        credit_line = read_file(TEXT_DIR + '/' + i)[1]
        print parse_credits(credit_line)

def main():

    s = time.time()
    HTML_DIR = 'html'
    SONG_DIR = 'songs'
    TEXT_DIR = 'txt'
    # print chord_lyric_split(chords, lyrics, 'verse')
    # for i in os.listdir(SONG_DIR):
    #     html_export(SONG_DIR + '/' + i, HTML_DIR + '/' + i)
    # html_export(SONG_DIR + '/' + songs[0], HTML_DIR + '/' + songs[0])
    # print classify_song('txt/Oh Great God')
    # a = html_export(sys.argv[1], sys.argv[2])
    # print re.sub('\’', "'", '’')
    # line = '<body>Body</body>'
    # print is_xml_line(line)
    # print parse_credits(credits)
    # process_upload(read_file(sys.argv[1]))
    parse_credit_test()

    print 'time: %e' % (time.time() - s)

if __name__=='__main__':
    main()
