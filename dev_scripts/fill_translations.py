"""
    Auto fill "verbose_name" translations:
    Just copy the model field name as translation.
"""
from pathlib import Path


BASE_PATH = Path(__file__).parent.parent

MESSAGE_MAP = {
    'id': 'ID',
}


def fill(po_file_path):
    old_content = []
    new_content = []
    with po_file_path.open('r') as f:
        for line in f:
            old_content.append(line)

            if line.startswith('msgid "'):
                msgstr = ''
                msgid = line[7:-2]
                try:
                    model, attribute, kind = msgid.strip().split('.')
                except ValueError:
                    pass
                else:
                    if kind == 'verbose_name':
                        if attribute in MESSAGE_MAP:
                            msgstr = MESSAGE_MAP[attribute]
                        else:
                            words = attribute.replace('_', ' ').split(' ')
                            msgstr = ' '.join(i.capitalize() for i in words)
                    elif kind == 'help_text':
                        msgstr = ' '  # "hide" empty "help_text"

            elif (line == 'msgstr ""\n' or line == 'msgstr "&nbsp;"\n') and msgstr:
                line = f'msgstr "{msgstr}"\n'

            line = line.replace('Content Tonie', 'Content-Tonie')
            new_content.append(line)

    if new_content == old_content:
        print('Nothing to do, ok.')
        return

    with po_file_path.open('w') as f:
        f.write(''.join(new_content))

    print(f'updated: {po_file_path}')


if __name__ == '__main__':
    for dir in ('de', 'en'):
        print('_' * 100)
        print(dir)
        fill(Path(BASE_PATH, f'src/for_runners/locale/{dir}/LC_MESSAGES/django.po'))
