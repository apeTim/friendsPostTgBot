LINE_ENDS = ['.', '!', ',', '?', ':', ';']

def sanitise_text(text: str) -> str:
        sanitised_text = ''

        for char in text:
            if not (ord(char) == 10 or 31 < ord(char) < 127 or 1039 < ord(char) < 1104): continue
            if char == '\n' and len(sanitised_text) == 0: continue

            if char == '\n':
                if sanitised_text[-1] == ' ':
                    sanitised_text = sanitised_text[:-1]
                if sanitised_text[-1] in LINE_ENDS:
                    sanitised_text += ' '
                    continue

                sanitised_text += '. '
            else:
                sanitised_text += char
        
        sanitised_text = sanitised_text.strip()

        return sanitised_text