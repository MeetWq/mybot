import os

dir_path = os.path.split(os.path.realpath(__file__))[0]
word_file_path = os.path.join(dir_path, 'keywords')


class DFAFilter:
    """
    Filter Messages from keywords

    Use DFA to keep algorithm perform constantly

    # >>> f = DFAFilter()
    # >>> f.add("sexy")
    # >>> f.filter("hello sexy baby")
    hello **** baby
    """

    def __init__(self):
        self.keyword_chains = {}
        self.delimit = '\x00'
        self.path = word_file_path
        self.parse()

    def add(self, keyword):
        if isinstance(keyword, bytes):
            keyword = keyword.decode('utf-8')
        keyword = keyword.lower()
        chars = keyword.strip()
        if not chars:
            return
        level = self.keyword_chains
        i = 0
        for i in range(len(chars)):
            if chars[i] in level:
                level = level[chars[i]]
            else:
                if not isinstance(level, dict):
                    break
                last_level = {}
                last_char = ''
                for j in range(i, len(chars)):
                    level[chars[j]] = {}
                    last_level, last_char = level, chars[j]
                    level = level[chars[j]]
                last_level[last_char] = {self.delimit: 0}
                break
        if i == len(chars) - 1:
            level[self.delimit] = 0

    def parse(self):
        with open(self.path, encoding='utf-8') as f:
            for keyword in f:
                self.add(keyword.strip())

    def word_replace(self, message, replace="*"):
        if isinstance(message, bytes):
            message = message.decode('utf-8')
        message = message.lower()
        ret = []
        start = 0
        while start < len(message):
            level = self.keyword_chains
            step_ins = 0
            for char in message[start:]:
                if char in level:
                    step_ins += 1
                    if self.delimit not in level[char]:
                        level = level[char]
                    else:
                        ret.append(replace * step_ins)
                        start += step_ins - 1
                        break
                else:
                    ret.append(message[start])
                    break
            else:
                ret.append(message[start])
            start += 1
        return ''.join(ret)
