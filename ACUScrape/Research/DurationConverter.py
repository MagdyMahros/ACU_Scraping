import re


def convert_num(text):  # okay... but why tho? what about zero?
    return text.replace('one', '1').replace('two', '2').replace('three', '3').replace('four', '4').replace('five',
                                                                                                           '5').replace(
        'six', '6').replace('seven', '7').replace('eight', '8').replace('nine', '9')


def convert_duration(duration):
    duration = duration.lower()  # at this stage duration is still a string of WORDS
    duration = convert_num(duration)  # convert every number in words to digits and return them in new string
    # at this stage, duration has word numbers in NUMERIC form.

    # note that: \d+(?:\.\d+)? = any number of digit before a dot and more BUT \.\d+ won't appear in the matches
    # the DOT means any one character except newline
    # but also \. is an escape character that matches DOT
    # the question mark is simply a quantifier that checks if the pattern matched exists or not
    # SUMMARY : IF IT CONTAINS A DIGIT OR A DECIMAL
    numbers = re.findall(r'\d+(?:\.\d+)?', duration)  # also returns a list of matched words as specified

    # put all contents of the duration definition in this list
    # but only if it has the word "semester" in it.
    dur_type_list = []
    for word in duration.split():
        if 'semester' in word.lower() or 'term' in word.lower() or 'hour' in word.lower() or 'day' in word.lower() or 'week' in word.lower() or 'month' in word.lower() or 'year' in word.lower():
            dur_type_list.append(word)  # put each word of the duration into the list

    # put all numbers contained in the duration in this list
    nums = []
    for number in numbers:
        if number != '':
            nums.append(number)

    for number in nums:
        for dur in dur_type_list:

            # CHECK FOR "YEAR" (But note that Year could also carry a month field in decimals!)
            if 'year' in dur:
                if '.' in number:
                    if re.findall(r'\d+', duration)[1] != 0:  # OK, BUT WHY? right, if there's a decimal in 2nd position
                        # for example,if it says "2.5 years", the 0.5 needs to be converted to months. the next line
                        # will then ensure "year" is no longer in the string so this if-branch won't apply next time.
                        return convert_duration(str(round(float(number) * 12)) + ' month')
                    return int(re.findall(r'\d+', duration)[0]), 'Years'
                else:
                    return int(number), 'Years'

            # CHECK FOR "MONTH"
            elif 'month' in dur:
                if '.' in number:
                    # if length of the first digit detected is less than 7
                    # just like before, month could carry a decimal field which needs to be converted to weeks
                    if re.findall(r'\d+', duration)[0] < 7:
                        return convert_duration(str(int(float(number) * 4)) + ' week')
                elif int(number) % 12 == 0:  # if the number is a sharp factor of 12
                    return int(int(number) / 12), 'Years'
                else:
                    return int(round(float(number))), 'Months'  # if not, just round it up and return months

            elif 'week' in dur:
                return round(int(number)), ' Weeks'
            elif 'hour' in dur:  # for real bruh??
                return int(number), 'Hours'
            elif 'semester' in dur:  # one semester being rounded to 6 months... sure.
                return convert_duration(str(int(number) * 6) + 'month')
            elif 'trimester' in dur:
                return convert_duration(str(int(number) * 3) + 'month')
            elif 'term' in dur:
                return convert_duration(str(int(number) * 6) + 'month')
            elif 'day' in dur:
                if '.' in number:
                    for jk in re.findall(r'\d+', duration):
                        if int(jk) > 1:
                            return convert_duration(str(int(float(number) * 24)) + 'hour')
                else:
                    return int(number), 'Days'
            else:
                return 'WRONG DATA'
