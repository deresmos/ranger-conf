import os

from ranger.api.commands import Command
from ranger.core.loader import CommandLoader


class extract_there(Command):  # {{{1
    def execute(self):
        cwd = self.fm.thisdir
        extract_files = tuple(self.fm.copy_buffer) or cwd.get_selection()

        if not extract_files:
            return

        def refresh(_):
            cwd = self.fm.get_directory(original_path)
            cwd.load_content()

        one_file = extract_files[0]
        cwd = self.fm.thisdir
        original_path = cwd.path
        au_flags = ['-x', '--subdir']
        au_flags += self.line.split()[1:]
        au_flags += ['-e']

        self.fm.copy_buffer.clear()
        self.fm.cut_buffer = False

        if len(extract_files) == 1:
            descr = "extracting: " + os.path.basename(one_file.path)
        else:
            descr = "extracting files from: " + \
                os.path.basename(one_file.dirname)
        obj = CommandLoader(
            args=['aunpack'] + au_flags + [f.path for f in extract_files],
            descr=descr)

        obj.signal_bind('after', refresh)
        self.fm.loader.add(obj)


class compress(Command):  # {{{1
    def execute(self):
        cwd = self.fm.thisdir
        extract_files = tuple(self.fm.copy_buffer) or cwd.get_selection()

        if not extract_files:
            return

        def refresh(_):
            cwd = self.fm.get_directory(original_path)
            cwd.load_content()

        original_path = cwd.path
        parts = self.line.split()
        au_flags = parts[1:]

        self.fm.copy_buffer.clear()
        self.fm.cut_buffer = False

        descr = "compressing files in: " + os.path.basename(parts[1])
        obj = CommandLoader(
            args=['apack'] + au_flags +
            [os.path.relpath(f.path, cwd.path) for f in extract_files],
            descr=descr)

        obj.signal_bind('after', refresh)
        self.fm.loader.add(obj)

    def tab(self):
        """ Complete with current folder name """

        extension = ['.zip', '.tar.gz', '.rar', '.7z']
        return [
            'compress ' + os.path.basename(self.fm.thisdir.path) + ext
            for ext in extension
        ]


class mount(Command):  # {{{1
    def execute(self):
        cwd = self.fm.thisdir
        marked_files = cwd.get_selection()

        if not marked_files:
            return

        def refresh(args):
            res = args['process'].communicate()[0].decode('utf-8')
            if res:
                self.fm.cd(res.split(' ')[3].split('.')[0])
            self.fm.notify(res)
            cwd = self.fm.get_directory(original_path)
            cwd.load_content()

        original_path = cwd.path
        au_flags = ['mount', '-b']

        descr = 'mounting ...'
        obj = CommandLoader(
            args=['udisksctl'] + au_flags + [f.path for f in marked_files],
            descr=descr)

        obj.signal_bind('after', refresh)
        self.fm.loader.add(obj)


class unmount(Command):  # {{{1
    def execute(self):
        cwd = self.fm.thisdir
        marked_files = cwd.get_selection()

        if not marked_files:
            return

        def refresh(args):
            self.fm.notify(args['process'].communicate()[0].decode('utf-8'))
            cwd = self.fm.get_directory(original_path)
            cwd.load_content()

        original_path = cwd.path
        au_flags = ['unmount', '-b']

        descr = 'Unmounting ...'
        obj = CommandLoader(
            args=['udisksctl'] + au_flags + [f.path for f in marked_files],
            descr=descr)

        obj.signal_bind('after', refresh)
        self.fm.loader.add(obj)
