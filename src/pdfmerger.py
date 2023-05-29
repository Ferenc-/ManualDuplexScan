#!/usr/bin/env python3
import sys

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Adw, Gio, Gtk
import pikepdf

class MainWindow(Gtk.ApplicationWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_size(600, 250)

        self.set_title("PDF Merger")

        self.odd_chooser = Gtk.FileDialog.new()
        self.odd_chooser.set_title("Select Odd Pages PDF")

        self.even_chooser = Gtk.FileDialog.new()
        self.even_chooser.set_title("Select Even Pages PDF")

        # Add file filters to the file choosers
        pdf_filter = Gtk.FileFilter()
        pdf_filter.set_name("PDF Files")
        pdf_filter.add_mime_type("application/pdf")
        self.filters = Gio.ListStore.new(Gtk.FileFilter)
        self.filters.append(pdf_filter)
        self.even_chooser.set_filters(self.filters)
        self.odd_chooser.set_filters(self.filters)

        # Create UI elements
        self.even_button = Gtk.Button(label="Select Even Pages PDF")
        self.even_button.connect("clicked", self.on_even_clicked)
        self.odd_button = Gtk.Button(label="Select Odd Pages PDF")
        self.odd_button.connect("clicked", self.on_odd_clicked)
        self.merge_button = Gtk.Button(label="Merge PDFs")
        self.merge_button.connect("clicked", self.on_merge_clicked)

        # Add UI elements to window
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_child(vbox)
        vbox.append(self.odd_button)
        vbox.append(self.even_button)
        vbox.append(self.merge_button)

    def on_even_clicked(self, widget):
        response = self.even_chooser.open(self, None, self.even_chooser_open_callback)

    def even_chooser_open_callback(self, dialog, result):
        try:
            file = dialog.open_finish(result)
            if file is not None:
                print(f"Even file path is {file.get_path()}")
                self.even_file = file.get_path()
        except GLib.Error as error:
            print(f"Error opening even file: {error.message}")

    def on_odd_clicked(self, button):
        response = self.odd_chooser.open(self, None, self.odd_chooser_open_callback)

    def odd_chooser_open_callback(self, dialog, result):
        try:
            file = dialog.open_finish(result)
            if file is not None:
                print(f"Odd file path is {file.get_path()}")
                self.odd_file = file.get_path()
        except GLib.Error as error:
            print(f"Error opening odd file: {error.message}")

    def on_merge_clicked(self, widget):
        even_pdf = pikepdf.Pdf.open(self.even_file)
        odd_pdf = pikepdf.Pdf.open(self.odd_file)

        output_pdf = pikepdf.new()

        for i in range(len(odd_pdf.pages)):
            output_pdf.pages.append(odd_pdf.pages[i])
            if i < len(even_pdf.pages):
                output_pdf.pages.append(even_pdf.pages[i])

        output_pdf.save("merged.pdf")
        print("PDFs merged successfully")


class PdfMerger(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present()


if Gtk.check_version(4, 10, 0):
    raise Exception('You do not have the required version of GTK+ installed. ' +
                    'Installed GTK+ version is ' +
                    '.'.join([str(Gtk.get_major_version()),
                              str(Gtk.get_minor_version()),
                              str(Gtk.get_micro_version())]) +
                    '. Required GTK+ version is 4.10 or higher.')


app = PdfMerger(application_id="com.github.Ferenc.PdfMerger")
app.run(sys.argv)
