import os
from subprocess import check_output

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
            self.fm.notify(' '.join(msg))
            cwd = self.fm.get_directory(original_path)
            cwd.load_content()

        original_path = cwd.path
        au_flags = ['mount', '-b']

        descr = 'mounting ...'
        msg = ['Mounted']
        for file in marked_files:
            obj = CommandLoader(
                args=['udisksctl'] + au_flags + [file.path], descr=descr)
            self.fm.loader.add(obj)
            msg.append('"' + file.path + '"')

        obj.signal_bind('after', refresh)


class unmount(Command):  # {{{1
    def execute(self):  # {{{2
        cwd = self.fm.thisdir
        marked_files = cwd.get_selection()

        if not marked_files:
            return

        def refresh(args):
            self.fm.notify(' '.join(msg))
            cwd = self.fm.get_directory(original_path)
            cwd.load_content()

        original_path = cwd.path
        au_flags = ['unmount', '-b']

        descr = 'Unmounting ...'
        msg = ['Unmounted']
        for file in marked_files:
            obj = CommandLoader(
                args=['udisksctl'] + au_flags +
                [self.checkMountList(file.path)],
                descr=descr)
            self.fm.loader.add(obj)
            msg.append('"' + file.path + '"')

        obj.signal_bind('after', refresh)

    def checkMountList(self, path):  # {{{2
        mount_output = check_output(['mount']).decode('utf-8').split('\n')[:-1]
        res = [m.split()[0] for m in mount_output if m.split()[2] == path]
        if res:
            res = res[0]
        return res or path


class resize_image(Command):  # {{{1
    def execute(self):  # {{{2
        cwd = self.fm.thisdir
        marked_files = cwd.get_selection()

        if not marked_files:
            return

        def refresh(args):
            self.fm.notify(' '.join(msg))
            cwd = self.fm.get_directory(original_path)
            cwd.load_content()

        original_path = cwd.path
        au_flags = ['-resize']
        size = self.line.split()[1]
        if 'x' not in size:
            size = size + '%'
        au_flags += [size]

        if not os.path.isdir(os.path.join(original_path, 'resize')):
            os.mkdir(os.path.join(original_path, 'resize'))

        src_paths = [file.path for file in marked_files]
        # Set dest paths {{{
        dest_paths = []
        if len(self.line.split()) == 2:
            for path in src_paths:
                dir_path, filename = os.path.split(path)
                filena, ext = os.path.splitext(filename)
                dest_paths.append(
                    os.path.join(dir_path, 'resize', filena + '_' + size +
                                 ext))
        else:
            dest_paths = [
                os.path.join(original_path, 'resize', self.line.split()[2])
            ]
        # }}}

        descr = 'Resizing ...'
        msg = ['Resized']
        for i, path in enumerate(dest_paths):
            src_path = src_paths if (
                len(self.line.split()) > 2) else src_paths[i:i + 1]
            obj = CommandLoader(
                args=['convert'] + au_flags + src_path + [path], descr=descr)

            self.fm.loader.add(obj)
        obj.signal_bind('after', refresh)
