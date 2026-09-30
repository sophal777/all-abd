    def load_path(self):
        if os.path.exists(path_file):
            with open(path_file, "r", encoding="utf-8") as f:
                path = f.read().strip()

                if path:
                    ldconsole = os.path.join(path, "ldconsole.exe")
                    self.combo.addItem(ldconsole)
                    self.path_edit.setText(ldconsole)
