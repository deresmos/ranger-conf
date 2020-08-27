from subprocess import check_output
from pathlib import Path

from ranger.api.commands import Command
from ranger.core.loader import CommandLoader


class extract_there(Command):
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
        au_flags = ["-x", "--subdir"]
        au_flags += self.line.split()[1:]
        au_flags += ["-e"]

        self.fm.copy_buffer.clear()
        self.fm.cut_buffer = False

        if len(extract_files) == 1:
            descr = "extracting: " + Path(one_file.path).name
        else:
            descr = "extracting files from: " + Path(one_file.dirname).name
        obj = CommandLoader(
            args=["aunpack"] + au_flags + [f.path for f in extract_files], descr=descr
        )

        obj.signal_bind("after", refresh)
        self.fm.loader.add(obj)


class compress(Command):
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

        descr = "compressing files in: " + Path(parts[1]).name
        obj = CommandLoader(
            args=["apack"]
            + au_flags
            + [Path(f.path).relative_to(cwd.path) for f in extract_files],
            descr=descr,
        )

        obj.signal_bind("after", refresh)
        self.fm.loader.add(obj)

    def tab(self):
        """ Complete with current folder name """

        extension = [".zip", ".tar.gz", ".rar", ".7z"]
        return [
            "compress " + Path(self.fm.thisdir.path).name + ext for ext in extension
        ]


class mount(Command):
    def execute(self):
        cwd = self.fm.thisdir
        marked_files = cwd.get_selection()

        if not marked_files:
            return

        def refresh(args):
            res = args["process"].communicate()[0].decode("utf-8")
            if res:
                self.fm.cd(res.split(" ")[3].split(".")[0])
            self.fm.notify(" ".join(msg))
            cwd = self.fm.get_directory(original_path)
            cwd.load_content()

        original_path = cwd.path
        au_flags = ["mount", "-b"]

        descr = "mounting ..."
        msg = ["Mounted"]
        for file in marked_files:
            obj = CommandLoader(
                args=["udisksctl"] + au_flags + [file.path], descr=descr
            )
            self.fm.loader.add(obj)
            msg.append('"' + file.path + '"')

        obj.signal_bind("after", refresh)


class unmount(Command):
    def execute(self):
        cwd = self.fm.thisdir
        marked_files = cwd.get_selection()

        if not marked_files:
            return

        def refresh(args):
            self.fm.notify(" ".join(msg))
            cwd = self.fm.get_directory(original_path)
            cwd.load_content()

        original_path = cwd.path
        au_flags = ["unmount", "-b"]

        descr = "Unmounting ..."
        msg = ["Unmounted"]
        for file in marked_files:
            obj = CommandLoader(
                args=["udisksctl"] + au_flags + [self.checkMountList(file.path)],
                descr=descr,
            )
            self.fm.loader.add(obj)
            msg.append('"' + file.path + '"')

        obj.signal_bind("after", refresh)

    def checkMountList(self, path):
        mount_output = check_output(["mount"]).decode("utf-8").split("\n")[:-1]
        res = [m.split()[0] for m in mount_output if m.split()[2] == path]
        if res:
            res = res[0]
        return res or path


class resize_image(Command):
    def execute(self):
        cwd = self.fm.thisdir
        marked_files = cwd.get_selection()

        if not marked_files:
            return

        def refresh(args):
            self.fm.notify(" ".join(msg))
            cwd = self.fm.get_directory(original_path)
            cwd.load_content()

        original_path = cwd.path
        au_flags = ["-resize"]

        # check 600x1200 or 60(%)
        size = self.line.split()[1]
        if "x" not in size:
            size = size + "%"
        au_flags += [size]

        resize_dirname = f"resize_{size}"
        Path(original_path, resize_dirname).mkdir(parents=True, exist_ok=True)

        src_paths = [file.path for file in marked_files]
        dest_paths = [
            Path(Path(path).parent, resize_dirname, Path(path).name)
            for path in src_paths
        ]

        descr = "Resizing ..."
        msg = ["Resized"]
        for s_path, d_path in zip(src_paths, dest_paths):
            obj = CommandLoader(
                args=["convert"] + au_flags + [s_path] + [d_path], descr=descr
            )

            self.fm.loader.add(obj)
        obj.signal_bind("after", refresh)
